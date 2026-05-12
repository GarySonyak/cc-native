#!/usr/bin/env python3
"""SessionStart POC: pull fresh feature-guide reference files from GitHub raw.

POC scope only — no TTL, no version compare, no atomic writes, no opt-out flag.
Every startup re-downloads all 9 reference files. Silent on any failure.
"""
import json
import os
import sys
import urllib.request

BASE = "https://raw.githubusercontent.com/GarySonyak/cc-native/main"
REFS = [
    "agents.md",
    "changelog.md",
    "hooks.md",
    "mcp-and-plugins.md",
    "memory-and-context.md",
    "modes-and-permissions.md",
    "settings.md",
    "skills.md",
    "tools-and-scheduling.md",
]


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if data.get("source") != "startup":
        sys.exit(0)

    plugin_root = os.environ.get(
        "CLAUDE_PLUGIN_ROOT",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
    refs_dir = os.path.join(plugin_root, "skills", "feature-guide", "references")

    updated = 0
    for name in REFS:
        url = f"{BASE}/skills/feature-guide/references/{name}"
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                body = resp.read()
            with open(os.path.join(refs_dir, name), "wb") as f:
                f.write(body)
            updated += 1
        except Exception:
            pass

    if updated:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": (
                            f"cc-native: refreshed {updated}/{len(REFS)} "
                            "feature-guide reference files from GitHub."
                        ),
                    }
                }
            )
        )


if __name__ == "__main__":
    main()
