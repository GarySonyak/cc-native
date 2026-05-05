# Changelog

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
