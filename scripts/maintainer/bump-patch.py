#!/usr/bin/env python3
"""Bump PATCH version in plugin.json + marketplace.json and prepend a CHANGELOG entry.

Idempotent in the sense that re-running on already-bumped state without staged
material changes produces no further bump (the cron wrapper guards on `git diff`
before calling this).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLUGIN_JSON = REPO / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = REPO / ".claude-plugin" / "marketplace.json"
CHANGELOG = REPO / "CHANGELOG.md"

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def bump(version: str) -> str:
    m = SEMVER_RE.match(version)
    if not m:
        raise SystemExit(f"unparseable semver: {version!r}")
    major, minor, patch = (int(g) for g in m.groups())
    return f"{major}.{minor}.{patch + 1}"


def update_plugin_json(new_version: str) -> str:
    data = json.loads(PLUGIN_JSON.read_text())
    old = data["version"]
    data["version"] = new_version
    PLUGIN_JSON.write_text(json.dumps(data, indent=2) + "\n")
    return old


def update_marketplace_json(new_version: str) -> None:
    data = json.loads(MARKETPLACE_JSON.read_text())
    for plugin in data.get("plugins", []):
        if plugin.get("name") == "cc-native":
            plugin["version"] = new_version
    MARKETPLACE_JSON.write_text(json.dumps(data, indent=2) + "\n")


def prepend_changelog(new_version: str, summary: str) -> None:
    today = dt.date.today().isoformat()
    entry = f"## [{new_version}] — {today}\n\n- {summary or 'docs-monitor patch update'}\n\n"
    if CHANGELOG.exists():
        existing = CHANGELOG.read_text()
        if existing.startswith("# Changelog"):
            head, _, rest = existing.partition("\n\n")
            CHANGELOG.write_text(f"{head}\n\n{entry}{rest}")
            return
    CHANGELOG.write_text(f"# Changelog\n\n{entry}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", default="", help="Summary line for the changelog entry")
    args = parser.parse_args()

    current = json.loads(PLUGIN_JSON.read_text())["version"]
    new_version = bump(current)
    old = update_plugin_json(new_version)
    update_marketplace_json(new_version)
    prepend_changelog(new_version, args.summary.strip())
    print(f"bumped {old} -> {new_version}")


if __name__ == "__main__":
    main()
