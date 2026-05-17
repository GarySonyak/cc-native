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
- `/heapdump` -- write JS heap snapshot + memory breakdown to `~/Desktop` (or home dir on Linux) for diagnosing high memory usage
- `/teleport` (alias `/tp`) -- pull a Claude Code on the web session into this terminal (fetches branch + conversation); requires claude.ai subscription
- `/goal` -- set completion condition; Claude works across turns until goal is met; use for non-interactive autonomous tasks (v2.1.139)
- `/background` -- detach current session as background agent (frees terminal); visible in Agent View (`claude agents`) (v2.1.139)
- `/stop` -- stop the current background session (only available while attached to a background session); transcript and worktree are kept. `/exit` or `←` to detach without stopping.

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
- **v2.1.128** (2026-05-04): bare `/color` picks random session color; `/mcp` shows tool count per connected server; `--plugin-dir` accepts `.zip` archives; `--channels` works with console (API key) auth; `workspace` is reserved MCP server name; MCP reconnect no longer floods chat with tool lists; auto mode classifier errors include helpful hints. New `allowedMcpServers`/`deniedMcpServers` managed settings for MCP server allowlists/denylists.
- **v2.1.129** (2026-05-06): `--plugin-url <url>` CLI flag installs plugin from URL `.zip` archive; `skillOverrides` setting: `off` (disable all auto-invocation), `user-invocable-only` (only user-invocable skills visible to model), or `name-only` (model sees names but not descriptions); Ctrl+R history picker now searches all projects by default (Ctrl+S narrows to current project). (v2.1.129)
- **v2.1.131** (2026-05-06): bug fixes only — VS Code extension activation on Windows; Mantle endpoint auth header fix.
- **v2.1.132** (2026-05-06): `CLAUDE_CODE_SESSION_ID` env var injected into Bash tool subprocess environment (scripts can correlate with session). `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN=1` opts out of fullscreen rendering. Bug fixes: SIGINT graceful shutdown, `--resume` emoji truncation, `--permission-mode` ignored on plan-mode resume, fullscreen blank after sleep/wake, stdio MCP server memory leak.
- **v2.1.133** (2026-05-07): Active effort level now in all hook JSON inputs (`effort.level` field; `$CLAUDE_EFFORT` env var for command hooks). `worktree.baseRef` setting (`fresh`/`head`). Bug fixes: subagents not discovering project/user/plugin skills; permission rules broken on mapped network drives; Remote Control stop/interrupt not fully canceling CLI; `/effort` affecting concurrent sessions.
- **v2.1.136** (2026-05-08): `autoMode.hard_deny` — unconditional auto mode blocking rules; user intent and `allow` exceptions cannot override. `CLAUDE_CODE_ENABLE_FEEDBACK_SURVEY_FOR_OTEL` env var for enterprise OTel deployments. Bug fixes: MCP servers disappeared after `/clear`; MCP OAuth refresh tokens lost on concurrent refresh; login loops from concurrent credential writes; extended thinking API errors with redacted blocks; `--resume`/`--continue` with underscores in project paths; WSL2 image paste via PowerShell fallback.
- **v2.1.137** (2026-05-09): VSCode extension activation fix on Windows.
- **v2.1.138** (2026-05-09): Internal fixes.
- **v2.1.139** (2026-05-11): Agent View research preview: `claude agents` opens unified session list showing all running CC sessions; `/background` detaches current session as background agent. `/goal` command: set completion condition, Claude works until met. `claude plugin details <name>`: component inventory + token cost projections. New tools: `PushNotification` (desktop + phone push via Remote Control; not on Bedrock/Vertex/Foundry) and `RemoteTrigger` (manage Routines on claude.ai, backs `/schedule`; requires Pro/Max/Team/Enterprise). Improved MCP OAuth handling, retry logic, env var passing.
- **v2.1.141** (2026-05-13): `terminalSequence: "<string>"` in hook JSON output emits a terminal escape sequence (desktop notifications, bell). `CLAUDE_CODE_PLUGIN_PREFER_HTTPS` env var for GitHub plugin cloning over HTTPS. `ANTHROPIC_WORKSPACE_ID` for workload identity federation. Enhanced `/feedback` shows last 24h/7-day sessions. "Summarize up to here" option in Rewind menu. 40+ bug fixes. (v2.1.141)
- **v2.1.140** (2026-05-12): Bug fixes — `subagent_type` matching now case/separator insensitive; `/goal` hang fix with certain hooks; background service startup fix on enterprise machines; tool validation fixes. (v2.1.140)
- **v2.1.142** (2026-05-14): `claude agents` dispatched session flags: `--add-dir`, `--settings`, `--mcp-config`, `--plugin-dir`, `--permission-mode`, `--model`, `--effort`, `--dangerously-skip-permissions`. Fast mode defaults to Opus 4.7 (`CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE=1` to pin 4.6). Plugins with root-level `SKILL.md` and no `skills/` subdirectory surface as skills. `MCP_TOOL_TIMEOUT` env var now properly raises per-request fetch timeout for remote servers (was capped at 60s). Bug fixes: background sessions + pre-existing worktrees, daemon exit after binary upgrade. (v2.1.142)
- **v2.1.143** (2026-05-15): Plugin dependency enforcement — `claude plugin disable` refuses when another enabled plugin depends on it. `worktree.bgIsolation: "none"` setting for direct working copy editing by background agents. Background session persistence: model and effort level preserved after idle wake; background agents now also preserve MCP configuration. PowerShell passes `-ExecutionPolicy Bypass` by default; enabled by default on Windows for Bedrock/Vertex/Foundry. Projected context costs shown per-turn in plugin marketplace. Bug fixes: corrupt `.credentials.json` hanging CLI startup, Esc/Ctrl+C not cancelling pending `/loop` wakeup, `/goal` evaluator firing while background shells run. (v2.1.143)
