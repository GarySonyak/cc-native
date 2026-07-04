# Tools Reference, Scheduled Tasks, Effort, Sessions

## Tools Reference (key additions)

| Tool | Notes |
|------|-------|
| `AskUserQuestion` | Presents multiple-choice questions to user to gather requirements or clarify ambiguity. Permission: No. Dialogs (and permission prompts, incl. plan approval) no longer auto-continue after 60s idle by default — v2.1.198/199 auto-continued unless `CLAUDE_AFK_TIMEOUT_MS` was set; opt back in via `/config`. (v2.1.200) |
| `ListMcpResourcesTool` | Lists resources exposed by connected MCP servers. Permission: No. |
| `ReadMcpResourceTool` | Reads a specific MCP resource by URI. Permission: No. |
| `LSP` | Code intelligence (type errors, go-to-def, find refs). Requires code intelligence plugin + language server binary. |
| `PowerShell` | Opt-in on all platforms (Windows, Linux, macOS, WSL). Set `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`. Windows: auto-detects pwsh.exe (PS 7+) vs powershell.exe (PS 5.1). Linux/macOS/WSL: requires `pwsh` (PS 7+). PowerShell profiles not loaded; sandboxing not supported on Windows. PowerShell commands auto-approvable in permission mode. (v2.1.114/v2.1.119) |
| `CronCreate/List/Delete` | Scheduled tasks within session. |
| `TaskOutput` | Deprecated -- use `Read` on output file path instead. |
| `TeamCreate` / `TeamDelete` | **Removed in v2.1.178.** Spawning a teammate with the Agent tool is now sufficient to form a team — no `TeamCreate` step needed. `TeamDelete` also removed; teams are auto-cleaned when the session exits. `SendMessage` and Task tools remain for team coordination. |
| `TaskStop` | Kill a running background task by ID. |
| `TodoWrite` | Disabled by default as of v2.1.142; Task tools (`TaskCreate`/`TaskGet`/`TaskList`/`TaskUpdate`) are now the default. Set `CLAUDE_CODE_ENABLE_TASKS=0` to re-enable `TodoWrite` (disables Task tools). |
| `ScheduleWakeup` | Internal — Claude calls this automatically at end of each self-paced `/loop` iteration to schedule the next one (1min–1hr). Not user-invocable directly. Pending wakeup visible in `session_crons` field of Stop hook input. Not available on Bedrock/Vertex/Foundry. |
| `Bash` | `$CLAUDE_CODE_SESSION_ID` is injected into every Bash tool subprocess — scripts can use it for logging or output correlation. (v2.1.132) Failed Bash commands in a parallel batch no longer cancel other calls in the same batch. (v2.1.161) |
| `Monitor` | Run command in background; each output line fed back to Claude mid-conversation. Watch logs, poll CI, tail files. (v2.1.98) |
| `ShareOnboardingGuide` | Uploads `ONBOARDING.md` and returns a share link teammates can open in Claude Code. Called from `/team-onboarding`. Requires claude.ai subscription (Pro/Max/Team/Enterprise). Permission required. |
| `PushNotification` | Sends desktop notification + phone push when Remote Control is connected. Not available on Bedrock/Vertex/Foundry (Anthropic infra only). Permission: No. (v2.1.139) |
| `RemoteTrigger` | Creates/updates/runs/lists Routines on claude.ai. Backs `/schedule`. Requires Pro/Max/Team/Enterprise on Anthropic. Not on Bedrock/Vertex/Foundry. Permission: No. (v2.1.139) |
| `EnterWorktree` | `path` param to switch into an existing worktree (not just create new): `EnterWorktree(path=...)`. (v2.1.105) |
| `WaitForMcpServers` | Waits for MCP servers still connecting in background; only appears when tool search is disabled (ToolSearch handles the wait otherwise). Claude calls it automatically. Permission: No. (v2.1.142) |
| `Read` | Oversized whole-file reads return a `PARTIAL view` (first page + notice showing remaining size + how to paginate with `offset`/`limit`). Reads with explicit `offset`/`limit` that still exceed limit return an error. Images/PDFs/notebooks handled natively. (v2.1.145) |
| `Workflow` | Runs a dynamic workflow — a script Claude writes that orchestrates many background subagents and returns one consolidated result. Permission: Yes. (v2.1.154) |
| `Write` | Detects when user edits proposed content before accepting (diffed against original). (v2.1.110) |
| `Artifact` | Publishes an HTML or Markdown file as a private, interactive page on claude.ai, shareable within your organization. Requires Team/Enterprise plan + `/login` auth; not available on Bedrock/Vertex/Foundry. Permission: Yes. (v2.1.183) |
| Advisor (API server tool) | Pairs main model with stronger advisor at key decision points (before committing to approach, on recurring errors, before declaring done). API-level (not CC-implemented); no permission rule name, hook matcher, or `tools:` field reference. Experimental, Anthropic API only. Supported pairings: any main model ≥ Haiku 4.5 can use Opus/Sonnet/Fable advisor; Fable main requires Fable advisor (v2.1.170+). Enable: `/advisor [opus|sonnet|fable]`, `advisorModel` setting, or `--advisor` flag. Disable: `/advisor off` or `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`. (v2.1.98+) |

## Scheduled Tasks (v2.1.72+)

Session-scoped; restored on `--resume`/`--continue` if unexpired (7-day window). (v2.1.114) Tools: `CronCreate`, `CronList`, `CronDelete`. Max 50 tasks per session. 7-day auto-expiry for recurring tasks. Jitter: recurring tasks fire up to **30 minutes** after scheduled time (or up to half the interval for sub-hourly tasks; e.g. hourly job at :00 may fire up to :30). One-shot tasks at :00/:30 fire up to 90s early. Offset is derived from task ID (same task always gets same offset). Disable: `CLAUDE_CODE_DISABLE_CRON=1`.

Compare options: **Routines** (Cloud, `/schedule`): Anthropic-managed, durable, 1hr min, triggers on schedule/API call/GitHub events. Desktop: local files, 1min min. `/loop`: in-session, 1min min, session-scoped.

`loop.md` customization: `.claude/loop.md` (project) or `~/.claude/loop.md` (user) replaces built-in `/loop` maintenance prompt; edits take effect on next iteration. Content >25KB truncated. (v2.1.101)

Stop a running `/loop` between iterations with `Esc` (only affects `/loop`; tasks created via natural-language scheduling are unaffected). On Bedrock, Vertex AI, and Microsoft Foundry: `/loop <prompt>` with no interval runs on a fixed 10-minute schedule (not dynamic), and bare `/loop` with no prompt prints usage instead of starting the maintenance loop.

**Scheduled skill invocation control (v2.1.196):** A `/loop` scheduled fire can pass a skill as the prompt (e.g. `/loop 20m /review-pr 1234`), but only skills Claude is allowed to auto-invoke actually execute. The following are passed as plain text instead: built-in commands (`/permissions`, `/model`, `/clear`, etc.); skills with `disable-model-invocation: true`; skills withheld by `skillOverrides` or a `Skill` deny rule; MCP prompts (`/mcp__<server>__<prompt>`). Skills exposed by MCP servers (not MCP prompts) still run. (v2.1.196)

## Session Management

`/continue` resume last session. `/resume` pick from list. `--fork-session` branch without affecting original. `/branch` fork for exploration. `/teleport` move between surfaces. Sessions tied to directory -- use worktrees for parallel sessions on different branches.

`/goal`: set completion condition; Claude works across turns until met; use for non-interactive autonomous tasks. (v2.1.139)
Agent View (v2.1.139+, research preview): `claude agents` opens unified session list showing all running CC sessions. `/background` detaches current session as background agent and frees the terminal. Background sessions can now be resumed with `/resume` (marked `bg` in the list). (v2.1.144)

## Effort & Output

Effort levels: low/medium/high/max/xhigh. xhigh = Opus 4.8 default for hardest tasks (v2.1.154); was Opus 4.7-only in v2.1.111. `ultracode` = xhigh reasoning + automatic Workflow tool orchestration; triggers multi-agent workflow on hard tasks. (v2.1.154) `/fast` toggles faster Opus output (fast mode: 2x standard rate for 2.5x speed, v2.1.154). `/effort` command to set level. Output styles configurable via settings. `/model` saves selection as default for new sessions automatically (v2.1.153). `! <command>` in interactive sessions runs shell command as detached background session — appears in Agent View. (v2.1.154)
