#!/usr/bin/env python3
"""Heuristic routing overlap detector for Claude Code subagents.

Compares descriptions of new (candidate) agents against existing agents
using keyword overlap. Output is a human-readable Markdown report.

NOTE: This is a keyword heuristic, NOT semantic analysis. Overlap score
>= threshold is a signal for human review, not a hard block.
"""
import argparse
import pathlib
import re

import yaml

FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

# Words that carry no routing signal — skip them in overlap calculation
STOP_WORDS = {
    "the", "and", "for", "from", "with", "that", "this", "when", "into",
    "your", "will", "are", "have", "been", "they", "them", "their",
    "task", "tasks", "agent", "agents", "output", "outputs", "file", "files",
}


def extract_descriptions(directory: pathlib.Path) -> dict:
    result = {}
    for p in sorted(directory.rglob("*.md")):
        m = FM_RE.match(p.read_text())
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue  # skip agents with unparseable frontmatter
        if fm.get("name") and fm.get("description"):
            result[fm["name"]] = str(fm["description"]).strip()
    return result


def meaningful_words(text: str) -> set:
    words = set(re.findall(r"\b\w{4,}\b", text.lower()))
    return words - STOP_WORDS


def keyword_overlap_score(desc_a: str, desc_b: str) -> float:
    a_words = meaningful_words(desc_a)
    b_words = meaningful_words(desc_b)
    if not a_words or not b_words:
        return 0.0
    return len(a_words & b_words) / min(len(a_words), len(b_words))


def main():
    p = argparse.ArgumentParser(description="Heuristic routing overlap check for Claude Code agents")
    p.add_argument("--existing", required=True, help="Directory of current live agents")
    p.add_argument("--new", required=True, help="Directory of new candidate agents")
    p.add_argument("--report", default="docs/agent-migration/routing-overlap-report.md")
    p.add_argument("--threshold", type=float, default=0.3,
                   help="Keyword overlap ratio to flag as potential conflict (default 0.3)")
    args = p.parse_args()

    existing = extract_descriptions(pathlib.Path(args.existing))
    new_agents = extract_descriptions(pathlib.Path(args.new))

    conflicts = []
    clean_pairs = []

    for new_name, new_desc in sorted(new_agents.items()):
        agent_conflicts = []
        for ex_name, ex_desc in sorted(existing.items()):
            if new_name == ex_name:
                continue
            score = keyword_overlap_score(new_desc, ex_desc)
            if score >= args.threshold:
                agent_conflicts.append((ex_name, score, new_desc, ex_desc))
            else:
                clean_pairs.append((new_name, ex_name, score))
        if agent_conflicts:
            conflicts.append((new_name, new_desc, agent_conflicts))

    lines = [
        "# Routing Overlap Report\n\n",
        f"> **Threshold:** {args.threshold} keyword overlap ratio\n",
        f"> **Existing agents scanned:** {len(existing)}\n",
        f"> **New candidates checked:** {len(new_agents)}\n",
        "> **Method:** keyword heuristic — NOT semantic analysis. Human review required for all flagged pairs.\n\n",
    ]

    if conflicts:
        total_flags = sum(len(c[2]) for c in conflicts)
        lines.append(f"## Potential Conflicts ({total_flags} pairs flagged)\n\n")
        lines.append("> ⚠️  These are heuristic matches. Sharpen descriptions if delegation is genuinely distinct.\n\n")
        for new_name, new_desc, agent_conflicts in conflicts:
            for ex_name, score, n_desc, ex_desc in agent_conflicts:
                shared = meaningful_words(n_desc) & meaningful_words(ex_desc)
                lines.append(f"### `{new_name}` ↔ `{ex_name}` (score: {score:.2f})\n\n")
                lines.append(f"- **New:** {n_desc}\n")
                lines.append(f"- **Existing:** {ex_desc}\n")
                lines.append(f"- **Shared keywords:** {', '.join(sorted(shared))}\n")
                lines.append("- **Action:** Review whether Claude would correctly differentiate these at dispatch time. Sharpen `description` if ambiguous.\n\n")
    else:
        lines.append(f"## No Conflicts Detected (threshold {args.threshold})\n\n")
        lines.append("> Note: keyword heuristic only — semantic overlap may still exist.\n\n")

    if clean_pairs:
        lines.append("## Clean Pairs (below threshold)\n\n")
        lines.append("| New Agent | Existing Agent | Score |\n")
        lines.append("|-----------|---------------|-------|\n")
        for new_name, ex_name, score in sorted(clean_pairs):
            lines.append(f"| `{new_name}` | `{ex_name}` | {score:.2f} |\n")

    report = pathlib.Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("".join(lines))
    print(f"Report: {report}")
    if conflicts:
        total = sum(len(c[2]) for c in conflicts)
        print(f"Flagged: {total} pair(s) need review (exit 0 — review is advisory)")


if __name__ == "__main__":
    main()
