#!/usr/bin/env python3
"""PreToolUse hook: reminds Claude to consult the feature-guide skill when editing CC config.

Fires on Edit/Write/MultiEdit. If the target file is a Claude Code configuration file
(under .claude/ config subdirs or .mcp.json), allows the tool but injects an
additionalContext line steering Claude to the cc-native:feature-guide skill before
subsequent edits.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import CONFIG_PATTERNS  # noqa: E402

REMINDER = (
    "You are editing a Claude Code configuration file. Before further edits, consult "
    "the cc-native:feature-guide skill — invoke /cc-native:feature-guide and read the "
    "matching file under references/ for the relevant feature. CC features change "
    "weekly — do not work from training memory; verify against the skill's reference docs."
)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    file_path = (data.get("tool_input") or {}).get("file_path") or ""
    if not file_path:
        sys.exit(0)

    if any(re.search(p, file_path) for p in CONFIG_PATTERNS):
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "allow",
                        "additionalContext": REMINDER,
                    }
                }
            )
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
