# Changelog

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
