# Tools Reference, Scheduled Tasks, Effort, Sessions

## Tools Reference (key additions)

| Tool | Notes |
|------|-------|
| `AskUserQuestion` | Presents multiple-choice questions to user to gather requirements or clarify ambiguity. Permission: No. |
| `ListMcpResourcesTool` | Lists resources exposed by connected MCP servers. Permission: No. |
| `ReadMcpResourceTool` | Reads a specific MCP resource by URI. Permission: No. |
| `LSP` | Code intelligence (type errors, go-to-def, find refs). Requires code intelligence plugin + language server binary. |
| `PowerShell` | Opt-in on all platforms (Windows, Linux, macOS, WSL). Set `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`. Windows: auto-detects pwsh.exe (PS 7+) vs powershell.exe (PS 5.1). Linux/macOS/WSL: requires `pwsh` (PS 7+). PowerShell profiles not loaded; sandboxing not supported on Windows. PowerShell commands auto-approvable in permission mode. (v2.1.114/v2.1.119) |
| `CronCreate/List/Delete` | Scheduled tasks within session. |
| `TaskOutput` | Deprecated -- use `Read` on output file path instead. |
| `TeamCreate` / `TeamDelete` | Create/disband agent teams. Only available when `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. |
| `TaskStop` | Kill a running background task by ID. |
| `TodoWrite` | Non-interactive mode / Agent SDK only. Interactive sessions use TaskCreate/TaskList/TaskUpdate. Set `CLAUDE_CODE_ENABLE_TASKS=1` to switch SDK/headless sessions to Task tools before `TodoWrite` is removed. |
| `Bash` | `$CLAUDE_CODE_SESSION_ID` is injected into every Bash tool subprocess — scripts can use it for logging or output correlation. (v2.1.132) |
| `Monitor` | Run command in background; each output line fed back to Claude mid-conversation. Watch logs, poll CI, tail files. (v2.1.98) |
| `ShareOnboardingGuide` | Uploads `ONBOARDING.md` and returns a share link teammates can open in Claude Code. Called from `/team-onboarding`. Requires claude.ai subscription (Pro/Max/Team/Enterprise). Permission required. |
| `PushNotification` | Sends desktop notification + phone push when Remote Control is connected. Not available on Bedrock/Vertex/Foundry (Anthropic infra only). Permission: No. (v2.1.139) |
| `RemoteTrigger` | Creates/updates/runs/lists Routines on claude.ai. Backs `/schedule`. Requires Pro/Max/Team/Enterprise on Anthropic. Not on Bedrock/Vertex/Foundry. Permission: No. (v2.1.139) |
| `EnterWorktree` | `path` param to switch into an existing worktree (not just create new): `EnterWorktree(path=...)`. (v2.1.105) |
| `Write` | Detects when user edits proposed content before accepting (diffed against original). (v2.1.110) |

## Scheduled Tasks (v2.1.72+)

Session-scoped; restored on `--resume`/`--continue` if unexpired (7-day window). (v2.1.114) Tools: `CronCreate`, `CronList`, `CronDelete`. Max 50 tasks per session. 7-day auto-expiry for recurring tasks. Jitter: recurring tasks fire up to **30 minutes** after scheduled time (or up to half the interval for sub-hourly tasks; e.g. hourly job at :00 may fire up to :30). One-shot tasks at :00/:30 fire up to 90s early. Offset is derived from task ID (same task always gets same offset). Disable: `CLAUDE_CODE_DISABLE_CRON=1`.

Compare options: **Routines** (Cloud, `/schedule`): Anthropic-managed, durable, 1hr min, triggers on schedule/API call/GitHub events. Desktop: local files, 1min min. `/loop`: in-session, 1min min, session-scoped.

`loop.md` customization: `.claude/loop.md` (project) or `~/.claude/loop.md` (user) replaces built-in `/loop` maintenance prompt; edits take effect on next iteration. Content >25KB truncated. (v2.1.101)

Stop a running `/loop` between iterations with `Esc` (only affects `/loop`; tasks created via natural-language scheduling are unaffected). On Bedrock, Vertex AI, and Microsoft Foundry: `/loop <prompt>` with no interval runs on a fixed 10-minute schedule (not dynamic), and bare `/loop` with no prompt prints usage instead of starting the maintenance loop.

## Session Management

`/continue` resume last session. `/resume` pick from list. `--fork-session` branch without affecting original. `/branch` fork for exploration. `/teleport` move between surfaces. Sessions tied to directory -- use worktrees for parallel sessions on different branches.

`/goal`: set completion condition; Claude works across turns until met; use for non-interactive autonomous tasks. (v2.1.139)
Agent View (v2.1.139+, research preview): `claude agents` opens unified session list showing all running CC sessions. `/background` detaches current session as background agent and frees the terminal.

## Effort & Output

Effort levels: low/medium/high/max/xhigh. xhigh = Opus 4.7 only (v2.1.111), max = current session only. `/fast` toggles faster Opus output. `/effort` command to set level. Output styles configurable via settings. `/model` to switch models mid-session.
