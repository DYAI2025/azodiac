#!/usr/bin/env python3
"""Write a per-candidate evidence ledger entry for agent migration."""
import argparse
import json
import pathlib
import subprocess
from datetime import date


def run_validator(validator: str, target_file: str) -> dict:
    target = pathlib.Path(target_file)
    r = subprocess.run(
        ["uv", "run", "python3", validator, str(target.parent)],
        capture_output=True, text=True,
    )
    try:
        data = json.loads(r.stdout)
        target_abs = target.resolve()
        candidate_results = [
            x for x in data.get("results", [])
            if pathlib.Path(x.get("file", "")).resolve() == target_abs
        ]
        if not candidate_results:
            return {
                "frontmatter_schema": "fail",
                "errors": [
                    f"validator ran but no result matched '{target_file}' "
                    f"(scanned {len(data.get('results', []))} files)"
                ],
            }
        errors = candidate_results[0]["errors"]
    except Exception as e:
        errors = [r.stderr.strip() or f"validator parse error: {e}"]
    return {
        "frontmatter_schema": "pass" if not errors else "fail",
        "errors": errors,
    }


def write_ledger(args) -> pathlib.Path:
    ledger_dir = pathlib.Path(args.ledger_dir)
    ledger_dir.mkdir(parents=True, exist_ok=True)

    checks = run_validator(args.validator, args.target_file)
    status = "validated" if checks["frontmatter_schema"] == "pass" else "needs_review"

    try:
        target_file_stored = str(pathlib.Path(args.target_file).resolve().relative_to(pathlib.Path.cwd()))
    except ValueError:
        # File is outside project root; store absolute path rather than a ../../ traversal.
        target_file_stored = str(pathlib.Path(args.target_file).resolve())

    entry = {
        "candidate": args.candidate,
        "source": args.source,
        "target_file": target_file_stored,
        "status": status,
        "checks": {
            "frontmatter_schema": checks["frontmatter_schema"],
            "name_collision": "not_checked",
            "tools_explicit": "pass" if checks["frontmatter_schema"] == "pass" else "unknown",
            "routing_overlap": "not_checked",
            "hook_schema": "not_applicable",
            "validator_errors": checks["errors"],
        },
        "risks": checks["errors"],
        "review_decision": "pending",
        "created": str(date.today()),
    }

    out = ledger_dir / f"{args.candidate}.json"
    out.write_text(json.dumps(entry, indent=2))
    print(f"Ledger: {out}")
    return out


def main():
    p = argparse.ArgumentParser(description="Write migration evidence ledger entry")
    p.add_argument("--candidate", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--target-file", required=True)
    p.add_argument("--validator", default="scripts/validate-claude-agents.py")
    p.add_argument("--ledger-dir", default="docs/agent-migration/evidence-ledger")
    args = p.parse_args()
    write_ledger(args)


if __name__ == "__main__":
    main()
