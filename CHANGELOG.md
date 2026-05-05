# Changelog

## [0.1.3] — 2026-05-05

- chore(metadata): sync `keywords` between `plugin.json` and `marketplace.json` (marketplace was advertising 3, manifest had 7) and add the `audit` keyword to reflect the auditor subagent. Marketplace listings are populated from `marketplace.json`, so this widens discoverability for users searching `skills`, `hooks`, `agents`, `docs`, `linting`, or `audit`.
- chore(metadata): mirror `category: "developer-tools"` from `marketplace.json` into `plugin.json` so both manifests agree.

Pre-submission cleanup ahead of the official Anthropic marketplace form (https://claude.ai/settings/plugins/submit). No behavior change.

## [0.1.2] — 2026-05-05

- fix(windows): `hooks.json` now invokes `python` instead of `python3`. On Windows the `python3` command resolves to the Microsoft Store install stub (which exits non-zero) — every hook was silently failing on Windows installs.
- fix(windows): `cc-native-reminder.py`, `cc-native-verify.py`, and `maybe-audit.py` now normalize incoming `file_path` values (`\` → `/`) so the POSIX-style `CONFIG_PATTERNS` and the `/.claude/<kind>/` literal checks in `_check_artifact_type` match Windows tool inputs.
- fix(windows): `_validate_hook_script` skips the POSIX `S_IXUSR` exec-bit check on `os.name == "nt"` (Windows files don't carry POSIX exec bits — the warning was firing on every hook).
- fix: hook smoke-test in `_validate_hook_script` now uses `sys.executable` instead of hardcoded `python3`, so it runs under whatever interpreter invoked the verify hook.
- improve: hardcoded-user-path portability check expanded — was only flagging `/root/...`, now also catches `/home/<user>/...`, `/Users/<user>/...`, and `C:\Users\<user>\...` (renamed `ROOT_PATH_RE` → `HARDCODED_USER_PATH_RE`).

## [0.1.1] — 2026-05-05

- fix: workflow rule scope had typo `.claube-plugin/` (missed marketplace.json edits).
- fix: `maybe-audit.py` now uses `decision: "block"` instead of undocumented Stop `additionalContext`; also traverses `MultiEdit` `edits[]` array (previously only top-level `file_path`).
- fix: `_check_artifact_type` no longer false-matches `references/*.md` inside installed skills as SKILL.md (was firing "missing frontmatter" errors on edits to skill reference files).
- fix: `cc-native-verify` warns when the live hook-event enum is unloadable, instead of silently passing invalid event names.
- improve: `.claude-plugin/` paths now in `CONFIG_PATTERNS` so plugin-manifest edits trigger the reminder/verify hooks.
- improve: auditor's skill-unavailable fallback now returns `warn` (was `info`) so the main agent sees that the audit was incomplete.

## [0.1.0] — 2026-05-05

- Initial scaffold (private dogfood release).
- `feature-guide` skill (renamed from `cc-native`) with progressive-disclosure references for hooks, skills, agents, MCP, plugins, settings, modes, memory, schedules, and a changelog.
- `cc-native-reminder` PreToolUse hook injects a feature-guide directive on `.claude/` edits.
- `cc-native-verify` PostToolUse deterministic lint with hook event-name validation against the live skill enum.
- `cc-native-auditor` Sonnet subagent for semantic review of changed artifacts.
- `maybe-audit` Stop hook signals the main agent to invoke the auditor.
- `rules/cc-native-agentic.md` Guide-and-Verify workflow rule.
- Maintainer-only `scripts/maintainer/` with docs-monitor agent + cron + bumper for daily reference refresh and auto-PATCH bumps.
- Test fixtures and Makefile (`make test` exercises all three hooks).
