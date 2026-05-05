# Commands & Changelog (recent versions)

## Key Commands (additions since last review)

- `/diff` -- interactive diff viewer for uncommitted changes + per-turn diffs
- `/insights` -- report on session patterns and friction points
- `/security-review` -- analyze pending branch changes for vulnerabilities
- `/sandbox` -- toggle sandbox mode (supported platforms only)
- `/setup-bedrock` -- Bedrock setup wizard (interactive auth/region/model config; visible when `CLAUDE_CODE_USE_BEDROCK=1`) (v2.1.92)
- `/setup-vertex` -- Google Vertex AI setup wizard (auth/project/region/model; visible when `CLAUDE_CODE_USE_VERTEX=1`) (v2.1.98)
- `/team-onboarding` -- generate teammate ramp-up guide from local Claude Code usage (v2.1.101)
- `/autofix-pr [prompt]` -- spawn cloud session to watch PR, push fixes for CI failures/review comments
- `/doctor` -- diagnose Claude Code installation
- `/schedule [description]` -- create/manage Cloud scheduled tasks (1hr minimum, survives restarts)
- `/ultraplan <prompt>` -- draft plan in browser, execute remotely or return to terminal
- `/tasks` -- list and manage background tasks (alias: `/bashes`)
- `/remote-control` -- make session available for remote control from claude.ai (alias: `/rc`)
- `/plugin` -- manage Claude Code plugins
- `/skills` -- list available skills
- `/tui` -- toggle flicker-free fullscreen rendering mode (v2.1.110)
- `/ultrareview` -- parallel cloud-based multi-agent code review (v2.1.111); `claude ultrareview [target]` non-interactive (v2.1.120)
- `/fewer-permission-prompts` -- [Skill] scan transcripts for common read-only Bash/MCP calls and add allowlist to project settings.json (renamed from /less-permission-prompts, v2.1.114)
- `/usage` consolidates `/cost`+`/stats` (v2.1.118)

## Version notes

- **v2.1.113**: security hardening -- `sandbox.network.deniedDomains` setting; `Bash(find:*)` no longer auto-approves `find -exec`/`-delete`; deny rules now match commands wrapped in `env`/`sudo`/`watch`/`ionice`/`setsid`; macOS `/private/{etc,var,tmp,home}` treated as dangerous.
- **v2.1.114** (2026-04-18): `/less-permission-prompts` renamed to `/fewer-permission-prompts`; permission-dialog crash fix when teammate requested tool permission.
- **v2.1.116** (2026-04-20): `/resume` 67% faster; `/reload-plugins` auto-installs missing plugin deps; agent `hooks:` frontmatter fires via `--agent`.
- **v2.1.117**: `CLAUDE_CODE_FORK_SUBAGENT=1` enables forked subagents on external/non-Anthropic builds.
- **v2.1.118** (2026-04-23): new `mcp_tool` hook type; hooks `"$defaults"` in auto mode rules; `/usage`; custom themes at `~/.claude/themes/`; `DISABLE_UPDATES` env var; Vim visual mode (v, V).
- **v2.1.119** (2026-04-23): `PostToolUse`/`PostToolUseFailure` hooks include `duration_ms`; `prUrlTemplate` setting; `--from-pr` accepts GitLab MRs/Bitbucket PRs/GHE; `/config` persists to `~/.claude/settings.json`; new index pages: `admin-setup`, `auto-mode-config`.
- **v2.1.120** (2026-04-28): Windows no longer requires Git Bash to launch CC (PowerShell default); `claude ultrareview [target]` non-interactive; `${CLAUDE_EFFORT}` in skills.
- **v2.1.121** (2026-04-28): `alwaysLoad` MCP option; `PostToolBatch` hook event; `PostToolUse` hooks can replace tool output for any tool; `claude plugin prune` removes orphaned deps; type-to-filter in `/skills`.
- **v2.1.122** (2026-04-28): `ANTHROPIC_BEDROCK_SERVICE_TIER` env var; PR URL search in `/resume`; `/mcp` duplicate server detection.
- **v2.1.123** (2026-04-29): OAuth 401 retry-loop fix when `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1`.
- **v2.1.126** (2026-05-01): `claude project purge` deletes all CC state for a project; `bypassPermissions` now bypasses protected paths (rm -rf / and ~ still prompt); OAuth improvements for WSL2/SSH/containers; auto-mode spinner turns red when classifier stalls; image auto-downscale >2000px on paste.
