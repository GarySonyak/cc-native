# Changelog

## [0.1.7] — 2026-05-05

- fix(maybe-audit): the v0.1.6 loop guard was logically correct but counted every `type: "user"` transcript record as a real user-turn boundary. Claude Code wraps tool_use_result blocks in synthetic `user` records, so `last_user_idx` slid forward on every tool call, making `auditor_idx > last_user_idx` always False and re-blocking on every Stop. New `_is_real_user_turn()` predicate excludes records that carry a top-level `toolUseResult` key or whose `message.content` contains a `tool_result` block. Regression covered by `tests/fixtures/transcripts/loop-fixed.jsonl` (auditor invoked, then tool result — must NOT re-block) and `needs-audit.jsonl` (no auditor — must block). Found by user re-hitting the loop after `/reload-plugins` brought v0.1.6 live.

## [0.1.6] — 2026-05-05

- fix(maybe-audit): the Stop hook now detects when the `cc-native-auditor` subagent has already been invoked since the last user message and stays silent on subsequent Stops in the same turn. Before this fix, the hook re-fired indefinitely whenever the user kept the turn open without resolving every flagged block (e.g., test artifacts intentionally left flawed, or findings the user explicitly accepts), because the transcript scan kept rediscovering the same prior edits. Found via dogfood session.
- fix(auditor): hardened the `cc-native-auditor` system prompt. The auditor now MUST `Read` the matching `references/<topic>.md` file before issuing any schema- or feature-shape finding on that artifact. Previously the prompt suggested consulting the reference but didn't enforce it, so the auditor would hallucinate marketplace-manifest schema details (claiming `url` source isn't documented, claiming `owner` isn't a marketplace field, inventing a `monitors` plugin field). Mapping table added so the auditor knows exactly which reference to read for each artifact type.

## [0.1.5] — 2026-05-05

- fix(marketplace): switch plugin `source` from `github` shorthand to explicit `url` form (`https://github.com/GarySonyak/cc-native.git`). Reason: Claude Code's plugin-install path on the `github` source defaults to SSH (`git@github.com:owner/repo.git`) and does not gracefully fall back to HTTPS the way the marketplace-add path does, so HTTPS-only users (no SSH keys configured for github.com) get `Permission denied (publickey)` on install. The `url` source clones over the literal URL string, which forces HTTPS and works for every user regardless of SSH setup.

## [0.1.4] — 2026-05-05

- chore(metadata): tighten manifests to documented schema ahead of marketplace submission. `marketplace.json` now declares a top-level `description` (was missing — flagged by `claude plugin validate`), drops the undocumented `owner.url` field, drops the `version` field on the plugin entry to avoid the silent-override pitfall the docs warn about ("`plugin.json` value always wins"), and mirrors `author`, `homepage`, `repository`, and `license` into the plugin entry so they appear on the marketplace listing card.
- chore(metadata): `plugin.json` drops the undocumented `author.url` field. The author block now matches the documented `{name, email?}` schema.

No behavior change. All hooks, skills, agents, and the audit subagent are unchanged.

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
