#!/usr/bin/env python3
"""Stop hook: scans the session transcript for edits to Claude Code config files.

If any Edit/Write/MultiEdit call this turn touched a path matching CONFIG_PATTERNS,
emits a `decision: "block"` Stop response with a reason instructing the main agent
to invoke the cc-native-auditor subagent on those files. Stop hooks cannot spawn
subagents directly — `decision: "block"` is the documented mechanism for steering
the model to do more work before allowing the turn to end.
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


def _extract_paths(tool_name: str, tool_input: dict) -> list[str]:
    """Return all file_paths referenced by a watched tool invocation.

    Edit/Write put `file_path` at the top level. MultiEdit uses `edits: [{file_path, ...}]`.
    """
    paths: list[str] = []
    if tool_name == "MultiEdit":
        edits = tool_input.get("edits") or []
        if isinstance(edits, list):
            for edit in edits:
                if isinstance(edit, dict):
                    fp = edit.get("file_path") or ""
                    if fp:
                        paths.append(fp)
        # MultiEdit may also carry a top-level file_path in some versions
        top = tool_input.get("file_path") or ""
        if top:
            paths.append(top)
    else:
        fp = tool_input.get("file_path") or ""
        if fp:
            paths.append(fp)
    return paths


def _scan_transcript(transcript_path: str) -> list[str]:
    """Return unique config-file paths touched by Edit/Write/MultiEdit in this transcript."""
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
                    tool = block.get("name")
                    if tool not in WATCHED_TOOLS:
                        continue
                    inp = block.get("input") or {}
                    if not isinstance(inp, dict):
                        continue
                    for fp in _extract_paths(tool, inp):
                        # Normalize Windows backslashes for POSIX-style pattern matching.
                        norm = fp.replace("\\", "/")
                        if norm not in seen and _matches_config(norm):
                            seen.add(norm)
                            touched.append(norm)
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
    reason = (
        "Claude Code config files were edited this turn. Before declaring done, "
        "invoke the `cc-native-auditor` subagent (via the Task tool) on these files "
        f"for semantic review:\n{file_list}\n"
        "The auditor will return a per-file verdict; treat any 'block' severity as "
        "a stop-ship issue. Once the auditor reports back (and any blocks are fixed), "
        "you may end the turn."
    )

    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


if __name__ == "__main__":
    main()
