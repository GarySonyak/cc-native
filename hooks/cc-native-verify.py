#!/usr/bin/env python3
"""PostToolUse deterministic lint for Claude Code config artifacts.

Fires on Edit/Write/MultiEdit. Validates the artifact that was just modified:
JSON parses, frontmatter has required keys, hook event names match the live enum
extracted from the feature-guide skill, tools field uses canonical syntax,
hook scripts are executable, /root/... paths warn for portability.

Exit codes: 0 pass, 1 warnings (stdout), 2 hard fail (stderr).
"""
from __future__ import annotations

import json
import os
import re
import stat
import subprocess
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import CONFIG_PATTERNS  # noqa: E402

PLUGIN_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
HOOKS_REF = os.path.join(PLUGIN_ROOT, "skills", "feature-guide", "references", "hooks.md")

TOOL_TOKEN_RE = re.compile(
    r"^([A-Z][A-Za-z0-9_]*|mcp__[A-Za-z0-9_]+__[A-Za-z0-9_]+)(\(.*\))?$"
)
ROOT_PATH_RE = re.compile(r"(^|[\s\"'`])/root/[^\s\"'`]+")

REQUIRED_FRONTMATTER = {
    "agents": ("name", "description"),
    "skills": ("name", "description"),
    "commands": ("description",),
    "output-styles": ("name", "description"),
}


def _emit(level: str, msg: str, errors: list[str], warnings: list[str]) -> None:
    if level == "error":
        errors.append(msg)
    else:
        warnings.append(msg)


def _load_hook_events() -> set[str]:
    """Extract hook event names from skills/feature-guide/references/hooks.md.

    Pulls every backtick-quoted CamelCase token under the "## Events by category"
    section. Falls back to an empty set if the file is missing — the verify hook
    must not crash on a partial install.
    """
    if not os.path.isfile(HOOKS_REF):
        return set()
    try:
        with open(HOOKS_REF, encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return set()

    m = re.search(
        r"## Events by category\s*\n(.+?)(?:\n## |\Z)", text, re.DOTALL
    )
    section = m.group(1) if m else text
    return set(re.findall(r"`([A-Z][A-Za-z0-9_]+)`", section))


def _parse_frontmatter(path: str) -> dict[str, Any] | None:
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    block = text[4:end]

    try:
        import yaml  # type: ignore

        data = yaml.safe_load(block)
        return data if isinstance(data, dict) else None
    except ImportError:
        # Minimal fallback: line-by-line key: value (no nesting, no lists)
        out: dict[str, Any] = {}
        for line in block.splitlines():
            if ":" not in line or line.startswith(" ") or line.startswith("\t"):
                continue
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
        return out


def _check_artifact_type(path: str) -> str | None:
    for kind in ("agents", "skills", "commands", "output-styles"):
        if f"/.claude/{kind}/" in path or f"/{kind}/" in path:
            return kind
    return None


def _validate_json(path: str, errors: list[str]) -> Any:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON — {exc}")
        return None


def _validate_settings(path: str, hook_events: set[str], errors: list[str]) -> None:
    data = _validate_json(path, errors)
    if not isinstance(data, dict):
        return
    hooks_block = data.get("hooks") or {}
    if not isinstance(hooks_block, dict):
        return
    for event in hooks_block:
        if hook_events and event not in hook_events:
            errors.append(
                f"{path}: unknown hook event '{event}' — see skills/feature-guide/references/hooks.md"
            )


def _validate_frontmatter(
    path: str, kind: str, errors: list[str], warnings: list[str]
) -> None:
    fm = _parse_frontmatter(path)
    if fm is None:
        errors.append(f"{path}: missing or malformed frontmatter")
        return
    for key in REQUIRED_FRONTMATTER.get(kind, ()):
        if key not in fm:
            errors.append(f"{path}: frontmatter missing required key '{key}'")

    if kind == "agents":
        if "permissionMode" in fm or "hooks" in fm or "mcpServers" in fm:
            errors.append(
                f"{path}: plugin agents cannot use permissionMode/hooks/mcpServers — "
                "these fields are ignored by the plugin loader"
            )

    tools_val = fm.get("tools") or fm.get("allowed-tools")
    if isinstance(tools_val, str):
        tokens = [t.strip() for t in tools_val.split(",") if t.strip()]
    elif isinstance(tools_val, list):
        tokens = [str(t).strip() for t in tools_val]
    else:
        tokens = []
    for tok in tokens:
        if not TOOL_TOKEN_RE.match(tok):
            warnings.append(f"{path}: tool token '{tok}' does not match canonical syntax")


def _validate_hook_script(path: str, errors: list[str], warnings: list[str]) -> None:
    if not path.endswith(".py"):
        return
    try:
        st = os.stat(path)
    except OSError:
        return
    if not (st.st_mode & stat.S_IXUSR):
        warnings.append(f"{path}: hook script not executable (chmod +x missing)")
    try:
        with open(path, encoding="utf-8") as fh:
            first = fh.readline()
    except OSError:
        return
    if not first.startswith("#!"):
        warnings.append(f"{path}: hook script missing shebang")
        return
    try:
        proc = subprocess.run(
            ["python3", path],
            input="{}",
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        warnings.append(f"{path}: smoke test failed ({exc})")
        return
    if proc.returncode not in (0, 2):
        errors.append(
            f"{path}: smoke test crashed (exit {proc.returncode}); "
            f"stderr={proc.stderr.strip()[:200]}"
        )


def _check_portability(path: str, warnings: list[str]) -> None:
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return
    for m in ROOT_PATH_RE.finditer(text):
        warnings.append(
            f"{path}: hardcoded /root/... path '{m.group(0).strip()}' — not portable"
        )
        break  # one warning per file is enough


def _matches_config(path: str) -> bool:
    return any(re.search(p, path) for p in CONFIG_PATTERNS)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    file_path = (data.get("tool_input") or {}).get("file_path") or ""
    if not file_path or not _matches_config(file_path):
        sys.exit(0)
    if not os.path.isfile(file_path):
        sys.exit(0)

    errors: list[str] = []
    warnings: list[str] = []
    hook_events = _load_hook_events()

    if file_path.endswith(".json"):
        if "settings" in os.path.basename(file_path):
            _validate_settings(file_path, hook_events, errors)
        else:
            _validate_json(file_path, errors)

    kind = _check_artifact_type(file_path)
    if kind and file_path.endswith(".md"):
        _validate_frontmatter(file_path, kind, errors, warnings)

    if "/hooks/" in file_path:
        _validate_hook_script(file_path, errors, warnings)

    _check_portability(file_path, warnings)

    if errors:
        sys.stderr.write("cc-native-verify: errors\n")
        for e in errors:
            sys.stderr.write(f"  - {e}\n")
        if warnings:
            sys.stderr.write("cc-native-verify: warnings\n")
            for w in warnings:
                sys.stderr.write(f"  - {w}\n")
        sys.exit(2)

    if warnings:
        for w in warnings:
            print(f"cc-native-verify: warning — {w}")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
