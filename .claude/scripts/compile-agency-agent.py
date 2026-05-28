#!/usr/bin/env python3
"""Compile an Agency-agent YAML into a normalized Claude-Code subagent Markdown.

Writes only to agents-src/agency-normalized/ or a user-supplied --out path.
Writing to live agents/ directory is blocked.
"""
import argparse
import pathlib
import re
import sys

import yaml

SECRET_PATTERNS = re.compile(
    r"(ghp_[A-Za-z0-9_]+|sk-[A-Za-z0-9_]+|token\s*[:=]\s*\S+|password\s*[:=]\s*\S+)",
    re.IGNORECASE,
)

TEMPLATE = """\
---
name: {name}
description: {description}
tools:
{tools_block}
model: sonnet
permissionMode: default
maxTurns: 20
memory: project
color: blue
---

# {title}

## Mission

{mission}

## When to use

{when_to_use}

## When not to use

Not applicable until validated and accepted via review gate.

## Tools and permissions

{tools_narrative}

## Workflow

1. Read available evidence or diff.
2. Analyze against stated criteria.
3. Produce structured output.

## Evidence required

Prior task outputs must exist in working directory.

## Output contract

Structured Markdown report with: summary, findings list, confidence, recommendation.

## Failure modes

- Missing input files → report `blocked: missing_evidence`
- Ambiguous scope → report `needs_clarification`

## Escalation

Return `blocked` status to orchestrator with reason.
"""


def kebab(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def scrub_secrets(text: str) -> str:
    return SECRET_PATTERNS.sub("[REDACTED]", text)


def is_blocked_output(out_dir: pathlib.Path) -> bool:
    """Block writes that resolve into the live agents/ directory.

    Safe: any path containing 'agents-src' or 'agency-normalized'.
    Blocked: paths where 'agents' is a standalone directory component.
    """
    def _is_safe(s: str) -> bool:
        return bool(re.search(r"(^|/)agents-src(/|$)", s) or
                    re.search(r"(^|/)agency-normalized(/|$)", s))

    # Check resolved absolute path
    try:
        resolved = str(out_dir.resolve()).replace("\\", "/")
        if _is_safe(resolved):
            return False
        if "/agents/" in resolved or resolved.endswith("/agents"):
            return True
    except Exception:
        pass

    # Check raw string (handles relative paths like "agents/core" or bare "agents")
    raw = str(out_dir).replace("\\", "/")
    if _is_safe(raw):
        return False
    return bool(re.match(r"^agents(/|$)", raw) or "/agents/" in raw or raw.endswith("/agents"))


def compile_agent(source_path: pathlib.Path, candidate: str, out_dir: pathlib.Path) -> pathlib.Path:
    if is_blocked_output(out_dir):
        print(
            f"BLOCKED: output path '{out_dir}' resolves to live agents/ directory. "
            "Use agents-src/agency-normalized/ instead.",
            file=sys.stderr,
        )
        sys.exit(1)

    raw = yaml.safe_load(source_path.read_text()) or {}
    name = kebab(candidate)
    title = raw.get("name", candidate)
    description = scrub_secrets(
        str(raw.get("description", f"Migrated from agency-agents: {title}")).strip()
    )
    mission = scrub_secrets(
        str(raw.get("persona", raw.get("description", "TBD"))).strip()
    )
    tools_narrative = scrub_secrets(
        str(raw.get("tools_guidance", "Explicit tools listed in frontmatter only.")).strip()
    )
    tools_list = raw.get("tools", ["Read"])
    if not isinstance(tools_list, list):
        tools_list = [str(tools_list)]

    tools_block = "\n".join(f"  - {t}" for t in tools_list)

    content = TEMPLATE.format(
        name=name,
        title=title,
        description=description,
        tools_block=tools_block,
        mission=mission,
        when_to_use=f"When {title.lower()} output is needed after a task run.",
        tools_narrative=tools_narrative,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{name}.md"
    out_file.write_text(content)
    return out_file


def main():
    p = argparse.ArgumentParser(description="Compile Agency agent YAML to Claude-Code subagent Markdown")
    p.add_argument("--source", required=True, help="Path to agency source YAML")
    p.add_argument("--candidate", required=True, help="Target agent name (will be kebab-cased)")
    p.add_argument("--out", required=True, help="Output directory (must not be agents/)")
    args = p.parse_args()

    outfile = compile_agent(
        pathlib.Path(args.source),
        args.candidate,
        pathlib.Path(args.out),
    )
    print(f"Generated: {outfile}")


if __name__ == "__main__":
    main()
