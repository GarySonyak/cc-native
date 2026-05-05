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
AUDITOR_NAME_FRAGMENT = "cc-native-auditor"
# Subagent-spawn tool is "Task" in legacy CC and "Agent" in the SDK / newer harness.
SUBAGENT_TOOLS = {"Task", "Agent"}


def _matches_config(path: str) -> bool:
    return any(re.search(p, path) for p in CONFIG_PATTERNS)


def _is_auditor_invocation(block: dict) -> bool:
    if not isinstance(block, dict) or block.get("type") != "tool_use":
        return False
    if block.get("name") not in SUBAGENT_TOOLS:
        return False
    inp = block.get("input") or {}
    if not isinstance(inp, dict):
        return False
    return AUDITOR_NAME_FRAGMENT in (inp.get("subagent_type") or "")


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
    """Return config paths edited *after* the most recent cc-native-auditor invocation.

    Earlier versions tracked "this turn" via the last real user-message index, then required
    the auditor to have run since that boundary. That created a self-sustaining loop: every
    hook block elicits a user relay of the block message, which counts as a new user turn,
    which makes the auditor look stale even though it just ran. The correct anchor is the
    auditor itself: edits before the last auditor call are already-reviewed; edits after it
    are not. The hook should only re-block when there is genuinely new config-edit activity
    the auditor has not yet seen.
    """
    if not transcript_path or not os.path.isfile(transcript_path):
        return []
    edits: list[tuple[int, str]] = []
    last_auditor_idx = -1
    try:
        with open(transcript_path, encoding="utf-8") as fh:
            for idx, line in enumerate(fh):
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
                    if _is_auditor_invocation(block):
                        last_auditor_idx = idx
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
                        if _matches_config(norm):
                            edits.append((idx, norm))
    except OSError:
        return []
    seen: set[str] = set()
    unaudited: list[str] = []
    for idx, path in edits:
        if idx <= last_auditor_idx:
            continue
        if path in seen:
            continue
        seen.add(path)
        unaudited.append(path)
    return unaudited


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    transcript_path = data.get("transcript_path") or ""
    unaudited = _scan_transcript(transcript_path)
    if not unaudited:
        sys.exit(0)

    file_list = "\n".join(f"  - {p}" for p in unaudited)
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
