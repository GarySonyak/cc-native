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


def _matches_config(path: str) -> bool:
    return any(re.search(p, path) for p in CONFIG_PATTERNS)


def _record_role(rec: dict) -> str:
    """Best-effort role detection across transcript variants ('type' or message.role)."""
    t = rec.get("type")
    if t in ("user", "assistant"):
        return t
    return (rec.get("message") or {}).get("role") or ""


def _is_real_user_turn(rec: dict) -> bool:
    """True only for human-authored user turns, not synthetic tool-result records.

    Claude Code wraps tool_use_result blocks in records typed `user`. Treating those as
    user-turn boundaries makes "since last user message" slide forward on every tool
    call, which broke v0.1.6's loop guard. A real user turn either has string content
    or a content list with no tool_result blocks; tool-result records also carry a
    top-level `toolUseResult` key we can use as a fast path.
    """
    if _record_role(rec) != "user":
        return False
    if "toolUseResult" in rec:
        return False
    content = (rec.get("message") or {}).get("content")
    if isinstance(content, str):
        return True
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                return False
        return True
    return True


def _is_auditor_invocation(block: dict) -> bool:
    if not isinstance(block, dict) or block.get("type") != "tool_use":
        return False
    if block.get("name") != "Task":
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


def _scan_transcript(transcript_path: str) -> tuple[list[str], bool]:
    """Walk the transcript once. Return (touched_config_paths, auditor_already_invoked_this_turn).

    "This turn" = records appearing after the most recent user message. If the cc-native-auditor
    has been invoked since that boundary, the Stop hook should not re-prompt — the audit already
    happened (or is happening) for the current set of edits, and re-firing would loop forever
    because every subsequent Stop also sees the same transcript edits.
    """
    touched: list[str] = []
    seen: set[str] = set()
    last_user_idx = -1
    auditor_idx = -1
    if not transcript_path or not os.path.isfile(transcript_path):
        return touched, False
    try:
        with open(transcript_path, encoding="utf-8") as fh:
            for idx, line in enumerate(fh):
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if _is_real_user_turn(rec):
                    last_user_idx = idx
                msg = rec.get("message") or {}
                content = msg.get("content")
                if not isinstance(content, list):
                    continue
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if _is_auditor_invocation(block):
                        auditor_idx = idx
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
        return touched, False
    auditor_invoked_this_turn = auditor_idx > last_user_idx
    return touched, auditor_invoked_this_turn


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    transcript_path = data.get("transcript_path") or ""
    touched, auditor_already_ran = _scan_transcript(transcript_path)
    if not touched or auditor_already_ran:
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
