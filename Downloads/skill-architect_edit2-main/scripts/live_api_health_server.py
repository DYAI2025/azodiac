#!/usr/bin/env python3
"""Minimal FastAPI server for architecture endpoint health checks.

Environment variables:
  HEALTHCHECK_BASE_URL          Base URL used when a check provides only path, e.g. https://api.example.com
  HEALTHCHECK_ALLOWED_HOSTS     Comma-separated allowed hostnames, e.g. api.example.com,staging.example.com
  HEALTHCHECK_BEARER_TOKEN      Optional bearer token required by this server.
  HEALTHCHECK_UPSTREAM_TOKEN    Optional bearer token forwarded to checked upstream APIs.
  HEALTHCHECK_TIMEOUT_SECONDS   Per-endpoint timeout. Default: 10
  HEALTHCHECK_CORS_ORIGINS      Comma-separated allowed browser origins. Default: *

The server accepts endpoint checks and service-to-service flow checks. Flow checks may
include source, target, flowIndex, method, path, expectedStatus, and expectedResponse.

Run:
  pip install fastapi uvicorn httpx
  uvicorn live_api_health_server:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

BASE_URL = os.getenv("HEALTHCHECK_BASE_URL", "").rstrip("/")
ALLOWED_HOSTS = {h.strip().lower() for h in os.getenv("HEALTHCHECK_ALLOWED_HOSTS", "").split(",") if h.strip()}
SERVER_TOKEN = os.getenv("HEALTHCHECK_BEARER_TOKEN", "")
UPSTREAM_TOKEN = os.getenv("HEALTHCHECK_UPSTREAM_TOKEN", "")
TIMEOUT_SECONDS = float(os.getenv("HEALTHCHECK_TIMEOUT_SECONDS", "10"))
CORS_ORIGINS = [o.strip() for o in os.getenv("HEALTHCHECK_CORS_ORIGINS", "*").split(",") if o.strip()]

app = FastAPI(title="Architecture Live API Health Check", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


def require_auth(authorization: str | None) -> None:
    if not SERVER_TOKEN:
        return
    expected = f"Bearer {SERVER_TOKEN}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid bearer token")


def build_url(check: dict[str, Any]) -> str:
    raw_url = str(check.get("url") or "").strip()
    path = str(check.get("path") or "").strip()
    if raw_url:
        url = raw_url
    elif BASE_URL and path:
        url = urljoin(BASE_URL + "/", path.lstrip("/"))
    else:
        raise ValueError("Each check needs either url or path plus HEALTHCHECK_BASE_URL")

    parsed = urlparse(url)
    if parsed.scheme != "https" and parsed.hostname not in {"localhost", "127.0.0.1"}:
        raise ValueError("Only HTTPS URLs are allowed outside localhost")
    host = (parsed.hostname or "").lower()
    if ALLOWED_HOSTS and host not in ALLOWED_HOSTS:
        raise PermissionError(f"Host is not allowlisted: {host}")
    return url


def has_json_path(data: Any, dotted_path: str) -> bool:
    current = data
    for part in dotted_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            return False
    return True


def classify_response(status_code: int | None, error: str | None, expected_status: list[int], response_json: Any, expected_response: dict[str, Any] | None) -> tuple[str, str]:
    if error:
        return "red", error
    if status_code is None:
        return "red", "No HTTP status returned"
    if 500 <= status_code <= 599:
        return "red", f"HTTP {status_code} server error"
    if status_code not in expected_status:
        return "yellow", f"HTTP {status_code}, expected one of {expected_status}"
    required_paths = (expected_response or {}).get("requiredJsonPaths") or []
    missing = [p for p in required_paths if not has_json_path(response_json, p)]
    if missing:
        return "yellow", "Missing expected response paths: " + ", ".join(missing)
    return "green", f"HTTP {status_code}"


async def probe_one(client: httpx.AsyncClient, check: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    method = str(check.get("method") or "GET").upper()
    expected_status = check.get("expectedStatus") or [200, 201, 202, 204]
    if isinstance(expected_status, int):
        expected_status = [expected_status]
    headers = {str(k): str(v) for k, v in (check.get("headers") or {}).items()}
    if UPSTREAM_TOKEN and "authorization" not in {k.lower() for k in headers}:
        headers["Authorization"] = f"Bearer {UPSTREAM_TOKEN}"

    status_code = None
    response_json = None
    error = None
    try:
        url = build_url(check)
        response = await client.request(
            method,
            url,
            headers=headers,
            params=check.get("query") or None,
            json=check.get("body") if check.get("body") is not None else None,
        )
        status_code = response.status_code
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            response_json = response.json()
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        error = type(exc).__name__ + ": " + str(exc)

    latency_ms = int((time.perf_counter() - started) * 1000)
    status, summary = classify_response(
        status_code=status_code,
        error=error,
        expected_status=[int(x) for x in expected_status],
        response_json=response_json,
        expected_response=check.get("expectedResponse"),
    )
    return {
        "nodeId": check.get("nodeId"),
        "endpointIndex": int(check.get("endpointIndex", 0)),
        "source": check.get("source"),
        "target": check.get("target"),
        "flowIndex": check.get("flowIndex"),
        "method": method,
        "path": check.get("path") or check.get("url") or "",
        "critical": bool(check.get("critical", False)),
        "status": status,
        "summary": summary,
        "httpStatus": status_code,
        "latencyMs": latency_ms,
        "error": error or "",
    }


def node_status(endpoint_results: list[dict[str, Any]]) -> str:
    statuses = [r.get("status", "unknown") for r in endpoint_results]
    if not statuses:
        return "unknown"
    if all(s == "green" for s in statuses):
        return "green"
    if all(s == "red" for s in statuses):
        return "red"
    return "yellow"


@app.post("/probe-architecture")
async def probe_architecture(request: Request, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    require_auth(authorization)
    payload = await request.json()
    checks = payload.get("checks") or []
    if not isinstance(checks, list):
        raise HTTPException(status_code=400, detail="checks must be an array")

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, follow_redirects=False) as client:
        results = [await probe_one(client, check) for check in checks]

    nodes: dict[str, dict[str, Any]] = {}
    for result in results:
        node_id = str(result.get("nodeId") or "unknown")
        endpoint_index = int(result.get("endpointIndex") or 0)
        node = nodes.setdefault(node_id, {"status": "unknown", "summary": "", "endpoints": []})
        while len(node["endpoints"]) <= endpoint_index:
            node["endpoints"].append({"status": "unknown", "summary": "not checked"})
        node["endpoints"][endpoint_index] = {
            "status": result["status"],
            "summary": result["summary"],
            "httpStatus": result["httpStatus"],
            "latencyMs": result["latencyMs"],
            "error": result["error"],
        }

    for node in nodes.values():
        node["status"] = node_status(node["endpoints"])
        passed = sum(1 for e in node["endpoints"] if e.get("status") == "green")
        total = len(node["endpoints"])
        node["summary"] = f"{passed}/{total} endpoints passed"

    edges: dict[str, dict[str, Any]] = {}
    for result in results:
        source = result.get("source")
        target = result.get("target")
        if not source or not target:
            continue
        key = f"{source}->{target}"
        edge = edges.setdefault(key, {"status": "unknown", "summary": "", "flows": []})
        edge["flows"].append({
            "index": result.get("flowIndex"),
            "method": result.get("method"),
            "path": result.get("path"),
            "critical": result.get("critical", False),
            "status": result.get("status", "unknown"),
            "summary": result.get("summary", ""),
            "httpStatus": result.get("httpStatus"),
            "latencyMs": result.get("latencyMs"),
        })

    for edge in edges.values():
        statuses = [f.get("status", "unknown") for f in edge["flows"]]
        if statuses and all(s == "green" for s in statuses):
            edge["status"] = "green"
        elif statuses and all(s == "red" for s in statuses):
            edge["status"] = "red"
        elif statuses:
            edge["status"] = "yellow"
        passed = sum(1 for f in edge["flows"] if f.get("status") == "green")
        edge["summary"] = f"{passed}/{len(edge['flows'])} flows passed"

    counts = {"green": 0, "yellow": 0, "red": 0, "unknown": 0}
    for node in nodes.values():
        counts[node["status"]] += 1
    for edge in edges.values():
        counts[edge["status"]] += 1
    overall = "green" if counts["red"] == 0 and counts["yellow"] == 0 and counts["unknown"] == 0 else "red" if counts["red"] else "yellow" if counts["yellow"] else "unknown"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {"status": overall, **counts},
        "nodes": nodes,
        "edges": edges,
        "results": results,
    }
