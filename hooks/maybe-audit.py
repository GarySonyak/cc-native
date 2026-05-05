#!/usr/bin/env python3
"""Stop hook: scans the session transcript for edits to Claude Code config files.

If any Edit/Write/MultiEdit call this turn touched a path matching CONFIG_PATTERNS,
emits an additionalContext directive instructing the main agent to invoke the
cc-native-auditor subagent on those files. Stop hooks cannot spawn subagents
directly — they signal the main agent.
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import CONFIG_PATTERNS  # noqa: E402

WATCHED_TOOLS = {"Edit", "Write", "MultiEdit"}


def _matches_config(path: str) -> bool:
    return any(re.search(p, path) for p in CONFIG_PATTERNS)


def _scan_transcript(transcript_path: str) -> list[str]:
    """Return unique file_paths touched by Edit/Write/MultiEdit in this transcript."""
    touched: list[str] = []
    seen: set[str] = set()
    if not transcript_path or not os.path.isfile(transcript_path):
        return touched
    try:
        with open(transcript_path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = rec.get("message") or {}
                content = msg.get("content")
                if not isinstance(content, list):
                    continue
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") != "tool_use":
                        continue
                    if block.get("name") not in WATCHED_TOOLS:
                        continue
                    inp = block.get("input") or {}
                    fp = inp.get("file_path") or ""
                    if fp and fp not in seen and _matches_config(fp):
                        seen.add(fp)
                        touched.append(fp)
    except OSError:
        return touched
    return touched


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    transcript_path = data.get("transcript_path") or ""
    touched = _scan_transcript(transcript_path)
    if not touched:
        sys.exit(0)

    file_list = "\n".join(f"  - {p}" for p in touched)
    directive = (
        "Claude Code config files were edited this turn. Before declaring done, "
        "invoke the `cc-native-auditor` subagent (via the Task tool) on these files "
        f"for semantic review:\n{file_list}\n"
        "The auditor will return a per-file verdict; treat any 'block' severity as "
        "a stop-ship issue."
    )

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "Stop",
                    "additionalContext": directive,
                }
            }
        )
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
