# Subagents, Custom Agents, Agent Teams, Worktrees

## Subagents

5 built-in types -- use via Agent tool with `subagent_type`:

| Type | Model | Access | Purpose |
|------|-------|--------|---------|
| `Explore` | Haiku | Read-only | Fast codebase search/analysis |
| `Plan` | Inherits | Read-only | Research for plan mode |
| `General-purpose` | Inherits | All tools | Complex multi-step tasks |
| `statusline-setup` | Sonnet | Read/Edit | `/statusline` configuration |
| `Claude Code Guide` | Haiku | Read-only | CC feature questions |

- **Doc correction (v2.1.198)**: `Explore` now inherits the main conversation's model (capped at Opus on the Claude API) instead of always running on Haiku; on Bedrock/Vertex/Foundry/Claude Platform on AWS it inherits the model directly. Define a project/user `Explore` agent with `model: haiku` to keep the old fixed-Haiku behavior.
- When invoking `Explore`, Claude specifies a thoroughness level: **quick** (targeted lookups), **medium** (balanced), or **very thorough** (comprehensive analysis).
- Resolution order: CLI `--agents` flag (1) > `.claude/agents/` (2) > `~/.claude/agents/` (3) > plugins (4)
- **Doc correction**: full resolution order is actually Managed settings (1, org-wide, deployed via managed settings) > CLI `--agents` flag (2) > `.claude/agents/` (3) > `~/.claude/agents/` (4) > plugin `agents/` (5) — the line above omits the managed tier (enterprise-only, takes precedence over all other scopes).
- `tools`/`disallowedTools` also accept MCP server-level patterns: `mcp__<server>` or `mcp__<server>__*` grants/removes every tool from that server in one entry; in `disallowedTools`, `mcp__*` removes every MCP tool from any server.
- Plugin `agents/` directories are scanned recursively, and (unlike project/user scope) a subfolder becomes part of the scoped identifier: a file at `agents/review/security.md` in plugin `my-plugin` registers as `my-plugin:review:security`. @-mention manually with `@agent-<name>` (local) or `@agent-<scoped-name>` (plugin, e.g. `@agent-my-plugin:code-reviewer`).
- Invoke: Agent tool with `subagent_type`, @-mention in interactive mode, or `claude --agent <name>`
- Resume via `SendMessage` with agent ID; stopped subagents auto-resume in the background on receipt. Explore/Plan agents are one-shot (no agent ID returned); use general-purpose or a custom subagent when resumable work is needed. Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Auto-compaction supported (`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` applies).
- **Doc correction (2026-06-29)**: `SendMessage` for subagent resumption (by agent ID) is available **without** `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Only structured team-protocol messages (teammate-to-teammate comms) require agent teams enabled.
- Subagents **cannot** spawn other subagents. **Update (v2.1.172)**: Sub-agents can now spawn sub-agents. **Foreground** subagents: unlimited depth. **Background** subagents: depth-5 cap (Agent tool not provided beyond depth 5). To enable in a custom agent: include `Agent` in its `tools` list; to prevent: omit `Agent` or add to `disallowedTools`. `Agent(type)` allowlist syntax is ignored inside a subagent context (type lists have no effect). Forks can spawn non-fork subagents but cannot spawn other forks.
- A background subagent's depth is fixed when it's first spawned; resuming it later (even from a shallower context) doesn't change that depth or let it spawn levels the depth-5 cap already prevented. (v2.1.187)
- Background vs foreground: Ctrl+B to background a running subagent. As of v2.1.186, background subagents surface permission prompts in the main session (previously auto-denied). Prompt names the requesting subagent; press Esc to deny that one tool call without stopping the subagent. (v2.1.186)
- Model override: `CLAUDE_CODE_SUBAGENT_MODEL` env var (highest priority over per-invocation model and frontmatter). Setting it to `inherit` now behaves as if unset — resolution falls through to the per-invocation `model` param, then frontmatter (v2.1.196; earlier versions forced the main conversation's model and ignored both).
- Each candidate in that resolution order (env var, per-invocation param, frontmatter) is also checked against the organization's `availableModels` allowlist; a value that resolves to an excluded model is skipped and resolution falls through to the next source, ultimately the main conversation's model.
- Subagents inherit the main conversation's extended-thinking on/off state; no per-subagent thinking setting. Before v2.1.198, subagents always ran with thinking disabled regardless of the session. (v2.1.198)
- `claude agents` CLI command lists configured agents without starting a session. In v2.1.139+ (Agent View research preview), also opens a unified session list showing all running CC sessions and their status. `claude agents --json` outputs live sessions as JSON for scripting (tmux-resurrect, status bars, session pickers). (v2.1.145)
- `claude agents` rows show `done/total` count before status detail when work is fanned out across agents. (v2.1.161)
- `claude agents --json` now also shows what each waiting session is blocked on (permission prompt, user input, etc.). (v2.1.162)
- `/background` in-session command: detaches current session as background agent (frees terminal); session appears in Agent View.
- Background agents preserve their launch permission mode and MCP configuration (v2.1.141/v2.1.143 fixes — previously reverted to defaults on wake).
- Background session persistence (v2.1.143): model and effort level are now also preserved after idle wake.
- Background sessions can now be resumed with `/resume`; they appear marked `bg` in the session list. (v2.1.144)
- `! <command>` in interactive sessions runs a shell command as a detached background session — frees the terminal; session appears in Agent View. (v2.1.154)
- **Dynamic workflows** (v2.1.154): ask Claude to create a workflow script that orchestrates work across tens to hundreds of background agents in parallel — for large migrations, codebase audits, cross-checked research. See `workflows.md` page.
- `claude agents` dispatched session config flags (v2.1.142): `--add-dir`, `--settings`, `--mcp-config`, `--plugin-dir`, `--permission-mode`, `--model`, `--effort`, `--dangerously-skip-permissions`.
- Subagent transcripts: `~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl`.
- `isolation: "worktree"` frontmatter field: subagent runs in a temporary git worktree.
- `CLAUDE_CODE_FORK_SUBAGENT=1`: enable forked subagents on external/non-Anthropic builds. (v2.1.117) The `/fork` command itself is enabled by default from v2.1.161 onward; the env var is only needed on external/non-Anthropic builds or versions before v2.1.161.
- **Background by default (v2.1.198)**: subagents now run in the background by default; Claude runs foreground only when it needs the result before continuing. Background subagents still surface every permission prompt in the main session. Background agents now also auto-commit and open a draft PR when they finish code work. (v2.1.198)
- **Explore/Plan opt-out**: `CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS=1` removes the built-in Explore/Plan subagents (Claude reads/explores directly). `CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS=1` removes all built-in agent types in non-interactive mode/Agent SDK. (v2.1.198)
- **Subagent API-error handling (v2.1.199)**: a subagent that hits a rate limit or server error now returns partial work instead of failing outright. Foreground: partial output + a cut-off note (or the `Agent terminated early due to an API error` failure if nothing was produced yet). Background: marked failed, with the error and its last output included in the message to the parent.
- **SendMessage identity check (v2.1.199)**: verifies a name still refers to the same agent reached earlier in the conversation; if a re-spawned agent reused the name, the send is refused and the error names the new target — address the earlier agent by its agent ID instead. Resets on `/clear`.
- Tools unavailable to a subagent even if listed in its `tools` field (depend on main-session UI/state): `AskUserQuestion`, `EnterPlanMode`, `ExitPlanMode` (unless the subagent's `permissionMode` is `plan`), `ScheduleWakeup`, `WaitForMcpServers`.
- `/doctor` reports same-scope duplicate subagent `name` values (v2.1.196); as of v2.1.205 it proposes renaming or removing all but one (before v2.1.205 it just opened a diagnostics screen showing which definition was active). Nested `.claude/agents/` directories: when more than one defines the same `name`, the definition closest to the working directory wins (v2.1.178).
- `isolation: worktree` subagents run their Bash/PowerShell commands inside the worktree; if the resolved cwd falls back to the main checkout (e.g. the worktree dir was removed mid-run), the command now errors instead of silently running in the main checkout. (v2.1.203)
- `--append-subagent-system-prompt <text>` (non-interactive/`-p` mode): appends text to the end of every subagent's system prompt, including nested subagents. (v2.1.205)
- Resuming a subagent starts a new run under the same agent ID; the task list now shows it as running again immediately (before v2.1.205 it kept showing the earlier failed/completed status while the resumed run was still working).
- Subagent-declared `mcpServers` (frontmatter or `--agent`) are subject to the same restrictions as the main session as of v2.1.153: `--strict-mcp-config`/`--bare`, enterprise managed MCP config, and `allowedMcpServers`/`deniedMcpServers` policies. A blocked server is skipped with a warning naming it. Managed-settings restrictions apply regardless of how the subagent is defined; `--strict-mcp-config` does not filter servers passed inline via `--agents` or the SDK `agents` option (explicit caller input).
- A `/fork`'s system prompt, tools, and model are identical to the parent, so its first request reuses the parent's prompt cache — cheaper than spawning a fresh named subagent for a task that needs the same context.
- Subagents with `SendMessage` in their tools get a "sibling roster" system reminder listing `main` and every other named agent in the session as valid `to` targets — a snapshot taken when the subagent starts, so agents named later don't appear. Only shown when at least one other agent already has a name. Requires v2.1.206+.
- When a subagent's `tools` list resolves to no tools at all (every entry misspelled or names a tool unavailable to subagents), the Agent tool now refuses to launch and returns an error naming the unresolved entries. Before v2.1.208, it launched anyway with no tools and could return an empty or confusing result. (v2.1.208)
- A completed background subagent now stays listed in `/tasks`, marked done and sorted below running work, until the session cleans up its task list; its detail view also stays open. Subagents that fail or that you stop still leave the list. Before v2.1.208, a completed subagent vanished from `/tasks` the moment it finished and its detail view closed. (v2.1.208)
- `--forward-subagent-text` CLI flag / `CLAUDE_CODE_FORWARD_SUBAGENT_TEXT=1` env var: includes subagent text and thinking blocks in `--output-format stream-json` output; before v2.1.211 only the parent session's text streamed, so a script consuming `stream-json` couldn't see subagent reasoning/output as it happened. (v2.1.211)

## Custom Agents

File: `.claude/agents/<name>.md` or `~/.claude/agents/<name>.md`. YAML frontmatter + markdown system prompt.

Key frontmatter fields: `name` (required), `description` (required), `model` (opus/sonnet/haiku/inherit), `tools`, `disallowedTools`, `memory` (user/project/local), `permissionMode`, `maxTurns`, `skills` (preload into context), `mcpServers` (scope MCP -- inline defs or name references), `hooks` (scoped lifecycle hooks), `background`, `effort` (low/medium/high/max), `isolation` (worktree), `initialPrompt`, `color` (red/blue/green/yellow/purple/orange/pink/cyan -- display color in task list and transcript).

`permissionMode` accepts `manual` as an alias for `default` (v2.1.200).

Restrict spawnable subagents: `tools: Agent(worker, researcher), Read, Bash` -- allowlist syntax.
Manage interactively: `/agents` command. **Doc correction (v2.1.198)**: `/agents` no longer opens an interactive wizard — running it prints a reminder to ask Claude or edit `.claude/agents/`/`~/.claude/agents/` directly; frontmatter and file locations are unchanged.

## Agent Teams

**Experimental** -- requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` env var or setting.

Architecture: lead + teammates + shared task list + mailbox. Active tools: `SendMessage`, `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate`. Tasks support dependencies (blocked until deps complete). Display: in-process (up/down arrows to select teammate, Enter to view transcript and message, x to stop, Ctrl+T toggle task list) or split-pane (tmux/iTerm2). One team per session, no nesting. Token cost scales linearly with team size. Subagent definitions reusable as teammate types.

**v2.1.178**: `TeamCreate`/`TeamDelete` tools removed. Spawning a teammate is now sufficient to form a team — no setup step. Team name auto-derived as `session-<first-8-chars-of-session-id>`. `team_name` on Agent tool input is accepted but ignored. `team_name` field in `TaskCreated`, `TaskCompleted`, and `TeammateIdle` hook payloads is **deprecated** (carries session-derived name). Team config directory removed automatically when session exits.

Display mode: `teammateMode` setting (`~/.claude/settings.json`) -- default changed to `"in-process"` (v2.1.179; was `"auto"`). Options: `"in-process"`, `"auto"` (split panes when already in tmux/iTerm2, else in-process), `"tmux"`, `"iterm2"` (iTerm2 native panes, requires `it2` CLI; v2.1.186). Override per-session: `claude --teammate-mode auto`. Split pane requires tmux or iTerm2 with it2 CLI. Idle teammate rows auto-hide after 30s and reappear on next turn (v2.1.181).
Teammates inherit the lead's effort level; in split-pane mode this applies from v2.1.186 (earlier split-pane sessions did not pass the lead's effort to teammates). (v2.1.186)

Idle teammate rows stay visible while any teammate/subagent is still working; once everyone is idle, rows hide after 30s (v2.1.181-198 hid each row 30s after its own turn, even while others were busy). More than 3 idle teammates collapse into one "N idle agents" row (Enter to expand). A teammate whose turn ends on an API error notifies the lead with the error text instead of appearing to finish normally; a message from the lead or another teammate wakes an in-process teammate waiting to retry a failed API request. (v2.1.198/v2.1.199)

Require plan approval: tell lead to "require plan approval before they make changes" -- teammate stays in read-only plan mode until lead approves. Lead makes approval decisions autonomously.

Team state stored locally: `~/.claude/teams/{session-name}/config.json`, `~/.claude/tasks/{session-name}/` (where `session-name` = `session-<first-8-chars-of-session-id>`). Do not hand-author these files. Task list directories persist on disk even after session ends (retention governed by `cleanupPeriodDays`).

Mailbox entries are validated on read: a malformed entry is dropped with an error while valid messages still deliver; before v2.1.207 a single malformed mailbox entry caused a repeated error every second and blocked delivery for that mailbox until the file was deleted manually. (v2.1.207)

Limitations: **no nested teams** (teammates cannot spawn their own teammates — only the lead can); **no background subagents from in-process teammates** (a teammate's own subagents always run in the foreground; requesting a background one errors, since it can't outlive the lead's process); **no session resumption** for in-process teammates (`/resume`/`/rewind` don't restore them — tell the lead to respawn). When spawning a teammate from a [subagent definition](#custom-agents), only `tools`/`model` apply and the body is appended as additional instructions — the definition's `skills`/`mcpServers` frontmatter fields are ignored; teammates load skills/MCP servers from project/user settings like a regular session.

## Worktrees

`isolation: "worktree"` on Agent tool (or subagent frontmatter) for git-isolated parallel work. Worktree auto-cleaned if no changes; branch returned if changes made. Also available via `EnterWorktree`/`ExitWorktree` tools. Use for parallel sessions, A/B experimentation, or `/batch` skill.
