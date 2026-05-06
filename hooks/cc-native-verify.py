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
HARDCODED_USER_PATH_RE = re.compile(
    r"(^|[\s\"'`])("
    r"/root/[^\s\"'`]+"
    r"|/home/[^/\s\"'`]+/[^\s\"'`]+"
    r"|/Users/[^/\s\"'`]+/[^\s\"'`]+"
    r"|[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s\"'`]+[\\/]+[^\s\"'`]*"
    r")"
)

# Detects literal credentials embedded inside permissions.allow[] Bash() patterns.
# Two leak shapes seen in real configs: env-var prefix (KEY=value cmd) and basic
# auth (-u user:password). When CC's "Always allow" persists a one-off command
# verbatim, any inline secret ends up baked into settings.json forever.
ENV_PREFIX_RE = re.compile(
    r"(?<![A-Za-z0-9_])([A-Z][A-Z0-9_]{2,})="
    r"(?:\"([^\"]+)\"|'([^']+)'|([^\s\\]+))"
)
BASIC_AUTH_RE = re.compile(
    r"(?:-u|--user)\s+[\"']?([^:\"'\s]+):([^\"'\s]{3,})[\"']?"
)
SECRET_KEY_NAMES = re.compile(
    r"PASSWORD|PASSWD|PWD|API[_-]?KEY|APIKEY|SECRET|TOKEN|PGPASSWORD",
    re.IGNORECASE,
)
# Values that match a SECRET_KEY_NAMES key but are clearly not real secrets.
SAFE_VALUES = {
    "1", "0", "true", "false", "yes", "no", "on", "off",
    "production", "development", "test", "staging", "local",
    "en_US.UTF-8", "C", "POSIX",
}

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
    """Determine the artifact kind from a config-file path.

    Skills are special: only files named SKILL.md count — references/*.md
    inside a skill have no frontmatter and must not be validated as skills.
    For agents/commands/output-styles we require `.claude/<kind>/` to be in
    the path so that nested directories (e.g. `references/agents.md`) do not
    false-match.
    """
    if path.endswith("/SKILL.md") and "/skills/" in path:
        return "skills"
    for kind in ("agents", "commands", "output-styles"):
        if f"/.claude/{kind}/" in path:
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


def _scan_allow_for_secrets(pattern: str) -> list[str]:
    """Find literal credentials embedded inside a permissions.allow[] Bash() rule.

    Two leak shapes the real-world audit surfaced in user settings:
      1. `Bash(KEY=literal_value cmd:*)` — env-var prefix with the secret baked
         into the allow rule. Triggered by "Always allow" on a one-off command
         that included the password inline (e.g. PGPASSWORD=, BINANCE_API_KEY=).
      2. `Bash(... curl -u "user:password" ...)` — basic-auth credential
         embedded literally rather than via a secret store.

    Both are detected via narrow regex + a credential-keyword filter and a
    safe-values whitelist to keep false positives low. Findings mask the
    secret so the verify hook itself doesn't echo it back into stderr/logs.
    """
    findings: list[str] = []
    for m in ENV_PREFIX_RE.finditer(pattern):
        key = m.group(1)
        value = m.group(2) or m.group(3) or m.group(4) or ""
        if not value or value.startswith("$"):
            continue
        if value in SAFE_VALUES:
            continue
        if not SECRET_KEY_NAMES.search(key):
            continue
        masked = (value[0] + "*" * max(len(value) - 1, 1)) if value else ""
        findings.append(
            f"literal credential in env-var prefix '{key}={masked}'"
        )
    for m in BASIC_AUTH_RE.finditer(pattern):
        user, pwd = m.group(1), m.group(2)
        if pwd.startswith("$"):
            continue
        masked = pwd[0] + "*" * max(len(pwd) - 1, 1)
        findings.append(f"basic-auth literal in '-u {user}:{masked}'")
    return findings


def _validate_settings(
    path: str, hook_events: set[str], errors: list[str], warnings: list[str]
) -> None:
    data = _validate_json(path, errors)
    if not isinstance(data, dict):
        return

    permissions = data.get("permissions") or {}
    allow = permissions.get("allow") if isinstance(permissions, dict) else None
    if isinstance(allow, list):
        for idx, entry in enumerate(allow):
            if not isinstance(entry, str) or not entry.startswith("Bash("):
                continue
            for finding in _scan_allow_for_secrets(entry):
                errors.append(
                    f"{path}: permissions.allow[{idx}] — {finding}. "
                    "Use $VAR + a secrets file (e.g. ~/.config/secrets.env); "
                    "literal credentials in allow rules persist into transcripts and telemetry."
                )

    hooks_block = data.get("hooks") or {}
    if not isinstance(hooks_block, dict):
        return
    if not hook_events:
        warnings.append(
            f"{path}: hook event-name validation skipped — could not load skills/"
            "feature-guide/references/hooks.md (skill not present?). Install or "
            "load the cc-native plugin to re-enable this check."
        )
        return
    for event in hooks_block:
        if event not in hook_events:
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
    # POSIX exec bits don't exist on Windows — skip the chmod check there.
    if os.name != "nt":
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
        # Use sys.executable so the smoke test runs under whatever interpreter
        # invoked us — avoids the python3-vs-python ambiguity across platforms.
        proc = subprocess.run(
            [sys.executable, path],
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
    for m in HARDCODED_USER_PATH_RE.finditer(text):
        warnings.append(
            f"{path}: hardcoded user path '{m.group(0).strip()}' — not portable"
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
    if not file_path:
        sys.exit(0)
    # Normalize Windows backslashes so POSIX-style CONFIG_PATTERNS and the
    # `/skills/` / `/.claude/<kind>/` literals in _check_artifact_type match.
    # Python's os.path on Windows accepts forward slashes, so file I/O still works.
    file_path = file_path.replace("\\", "/")
    if not _matches_config(file_path):
        sys.exit(0)
    if not os.path.isfile(file_path):
        sys.exit(0)

    errors: list[str] = []
    warnings: list[str] = []
    hook_events = _load_hook_events()

    if file_path.endswith(".json"):
        if "settings" in os.path.basename(file_path):
            _validate_settings(file_path, hook_events, errors, warnings)
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
