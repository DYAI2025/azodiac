#!/usr/bin/env python3
"""Claude Code agent schema validator and inventory tool."""
import argparse
import json
import pathlib
import re
import sys

import yaml

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

ALLOWED_MODELS = {"sonnet", "opus", "haiku", "inherit", None}
ALLOWED_PERMISSIONS = {"default", "acceptEdits", "readOnly", None}
ALLOWED_MEMORY = {"none", "project", "user", "local", None}
ALLOWED_COLORS = {
    "red", "orange", "yellow", "green", "blue", "purple",
    "pink", "cyan", "white", "black", None,
}
KEBAB_RE = re.compile(r"^[a-z][a-z0-9\-]+$")
REQUIRED_BODY_SECTIONS = ["Output contract", "Failure modes"]


def parse_agent(path: pathlib.Path) -> dict:
    text = path.read_text()
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {"file": str(path), "name": path.stem, "parse_error": "no frontmatter"}
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return {"file": str(path), "name": path.stem, "parse_error": str(e)}
    return {
        "file": str(path),
        "name": fm.get("name"),
        "description": fm.get("description"),
        "tools": fm.get("tools"),
        "model": fm.get("model"),
        "permissionMode": fm.get("permissionMode"),
        "maxTurns": fm.get("maxTurns"),
        "memory": fm.get("memory"),
        "color": fm.get("color"),
        "parse_error": None,
        "frontmatter": fm,
    }


def collect_agents(root: pathlib.Path) -> list:
    agents = []
    for p in sorted(root.rglob("*.md")):
        entry = parse_agent(p)
        if entry.get("parse_error") is None and entry.get("name") is None:
            continue  # not an agent file (no name: field)
        agents.append(entry)
    return agents


def validate_agent(entry: dict) -> list:
    errors = []
    if entry.get("parse_error"):
        return [f"parse_error: {entry['parse_error']}"]

    name = entry.get("name")
    if not name:
        errors.append("name: missing")
    elif not KEBAB_RE.match(name):
        errors.append(f"name: '{name}' must be kebab-case (lowercase letters, digits, hyphens)")

    if not entry.get("description"):
        errors.append("description: missing or empty")

    if not entry.get("tools"):
        errors.append("tools: missing — must be explicit list (not inherited)")

    pm = entry.get("permissionMode")
    if pm == "bypassPermissions":
        errors.append("permissionMode: bypassPermissions is blocked without explicit approval")
    elif pm not in ALLOWED_PERMISSIONS:
        errors.append(f"permissionMode: '{pm}' not in allowed values {sorted(str(v) for v in ALLOWED_PERMISSIONS)}")

    if entry.get("model") not in ALLOWED_MODELS:
        errors.append(f"model: '{entry.get('model')}' not in allowed values")

    if entry.get("memory") not in ALLOWED_MEMORY:
        errors.append(f"memory: '{entry.get('memory')}' not in allowed values {sorted(str(v) for v in ALLOWED_MEMORY)}")

    if entry.get("color") not in ALLOWED_COLORS:
        errors.append(f"color: '{entry.get('color')}' not in allowed values")

    body = pathlib.Path(entry["file"]).read_text()
    for section in REQUIRED_BODY_SECTIONS:
        if section.lower() not in body.lower():
            errors.append(f"body: missing required section '{section}'")

    return errors


def check_duplicates(agents: list) -> list:
    seen, errors = {}, []
    for a in agents:
        n = a.get("name")
        if n and n in seen:
            errors.append(f"name: '{n}' duplicated in {a['file']} and {seen[n]}")
        elif n:
            seen[n] = a["file"]
    return errors


def main():
    parser = argparse.ArgumentParser(description="Claude Code agent schema validator")
    parser.add_argument("path", help="Directory to scan")
    parser.add_argument("--inventory-only", action="store_true",
                        help="Emit JSON inventory without validation; always exits 0")
    args = parser.parse_args()

    root = pathlib.Path(args.path)
    if not root.exists():
        print(f"Error: path not found: {root}", file=sys.stderr)
        sys.exit(2)

    agents = collect_agents(root)

    if args.inventory_only:
        print(json.dumps({"agents": agents}, indent=2))
        sys.exit(0)

    # Validation mode
    all_errors = check_duplicates(agents)
    results = []
    for agent in agents:
        errs = validate_agent(agent)
        results.append({"file": agent["file"], "name": agent.get("name"), "errors": errs})
        all_errors.extend([f"{agent['file']}: {e}" for e in errs])

    print(json.dumps({"results": results, "global_errors": all_errors[:50], "total_errors": len(all_errors)}, indent=2))
    sys.exit(1 if all_errors else 0)


if __name__ == "__main__":
    main()
