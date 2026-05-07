# Tools Reference, Scheduled Tasks, Effort, Sessions

## Tools Reference (key additions)

| Tool | Notes |
|------|-------|
| `LSP` | Code intelligence (type errors, go-to-def, find refs). Requires code intelligence plugin + language server binary. |
| `PowerShell` | Opt-in on all platforms (Windows, Linux, macOS, WSL). Set `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`. Windows: auto-detects pwsh.exe (PS 7+) vs powershell.exe (PS 5.1). Linux/macOS/WSL: requires `pwsh` (PS 7+). PowerShell profiles not loaded; sandboxing not supported on Windows. PowerShell commands auto-approvable in permission mode. (v2.1.114/v2.1.119) |
| `CronCreate/List/Delete` | Scheduled tasks within session. |
| `TaskOutput` | Deprecated -- use `Read` on output file path instead. |
| `TeamCreate` / `TeamDelete` | Create/disband agent teams. Only available when `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. |
| `TaskStop` | Kill a running background task by ID. |
| `TodoWrite` | Non-interactive mode / Agent SDK only. Interactive sessions use TaskCreate/TaskList/TaskUpdate. |
| `Bash` | `$CLAUDE_CODE_SESSION_ID` is injected into every Bash tool subprocess — scripts can use it for logging or output correlation. (v2.1.132) |
| `Monitor` | Run command in background; each output line fed back to Claude mid-conversation. Watch logs, poll CI, tail files. (v2.1.98) |
| `EnterWorktree` | `path` param to switch into an existing worktree (not just create new): `EnterWorktree(path=...)`. (v2.1.105) |
| `Write` | Detects when user edits proposed content before accepting (diffed against original). (v2.1.110) |

## Scheduled Tasks (v2.1.72+)

Session-scoped; restored on `--resume`/`--continue` if unexpired (7-day window). (v2.1.114) Tools: `CronCreate`, `CronList`, `CronDelete`. Max 50 tasks per session. 7-day auto-expiry for recurring tasks. Jitter: recurring tasks up to 10% late (capped 15min); one-shot at :00/:30 fire up to 90s early. Disable: `CLAUDE_CODE_DISABLE_CRON=1`.

Compare options: **Routines** (Cloud, `/schedule`): Anthropic-managed, durable, 1hr min, triggers on schedule/API call/GitHub events. Desktop: local files, 1min min. `/loop`: in-session, 1min min, session-scoped.

`loop.md` customization: `.claude/loop.md` (project) or `~/.claude/loop.md` (user) replaces built-in `/loop` maintenance prompt; edits take effect on next iteration. Content >25KB truncated. (v2.1.101)

Stop a running `/loop` between iterations with `Esc` (only affects `/loop`; tasks created via natural-language scheduling are unaffected). On Bedrock, Vertex AI, and Microsoft Foundry: `/loop <prompt>` with no interval runs on a fixed 10-minute schedule (not dynamic), and bare `/loop` with no prompt prints usage instead of starting the maintenance loop.

## Session Management

`/continue` resume last session. `/resume` pick from list. `--fork-session` branch without affecting original. `/branch` fork for exploration. `/teleport` move between surfaces. Sessions tied to directory -- use worktrees for parallel sessions on different branches.

## Effort & Output

Effort levels: low/medium/high/max/xhigh. xhigh = Opus 4.7 only (v2.1.111), max = current session only. `/fast` toggles faster Opus output. `/effort` command to set level. Output styles configurable via settings. `/model` to switch models mid-session.
