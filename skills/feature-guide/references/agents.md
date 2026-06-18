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

- Resolution order: CLI `--agents` flag (1) > `.claude/agents/` (2) > `~/.claude/agents/` (3) > plugins (4)
- Invoke: Agent tool with `subagent_type`, @-mention in interactive mode, or `claude --agent <name>`
- Resume via `SendMessage` with agent ID; stopped subagents auto-resume in the background on receipt. Explore/Plan agents are one-shot (no agent ID returned); use general-purpose or a custom subagent when resumable work is needed. Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Auto-compaction supported (`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` applies).
- Subagents **cannot** spawn other subagents. **Update (v2.1.172)**: Sub-agents can now spawn sub-agents. **Foreground** subagents: unlimited depth. **Background** subagents: depth-5 cap (Agent tool not provided beyond depth 5). To enable in a custom agent: include `Agent` in its `tools` list; to prevent: omit `Agent` or add to `disallowedTools`. `Agent(type)` allowlist syntax is ignored inside a subagent context (type lists have no effect). Forks can spawn non-fork subagents but cannot spawn other forks.
- Background vs foreground: Ctrl+B to background a running subagent.
- Model override: `CLAUDE_CODE_SUBAGENT_MODEL` env var (highest priority over per-invocation model and frontmatter).
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
- `CLAUDE_CODE_FORK_SUBAGENT=1`: enable forked subagents on external/non-Anthropic builds. (v2.1.117)

## Custom Agents

File: `.claude/agents/<name>.md` or `~/.claude/agents/<name>.md`. YAML frontmatter + markdown system prompt.

Key frontmatter fields: `name` (required), `description` (required), `model` (opus/sonnet/haiku/inherit), `tools`, `disallowedTools`, `memory` (user/project/local), `permissionMode`, `maxTurns`, `skills` (preload into context), `mcpServers` (scope MCP -- inline defs or name references), `hooks` (scoped lifecycle hooks), `background`, `effort` (low/medium/high/max), `isolation` (worktree), `initialPrompt`, `color` (red/blue/green/yellow/purple/orange/pink/cyan -- display color in task list and transcript).

Restrict spawnable subagents: `tools: Agent(worker, researcher), Read, Bash` -- allowlist syntax.
Manage interactively: `/agents` command.

## Agent Teams

**Experimental** -- requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` env var or setting.

Architecture: lead + teammates + shared task list + mailbox. Active tools: `SendMessage`, `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate`. Tasks support dependencies (blocked until deps complete). Display: in-process (Shift+Down) or split-pane (tmux/iTerm2). One team per session, no nesting. Token cost scales linearly with team size. Subagent definitions reusable as teammate types.

**v2.1.178**: `TeamCreate`/`TeamDelete` tools removed. Spawning a teammate is now sufficient to form a team — no setup step. Team name auto-derived as `session-<first-8-chars-of-session-id>`. `team_name` on Agent tool input is accepted but ignored. `team_name` field in `TaskCreated`, `TaskCompleted`, and `TeammateIdle` hook payloads is **deprecated** (carries session-derived name). Team config directory removed automatically when session exits.

Display mode: `teammateMode` setting (`~/.claude/settings.json`) -- `"auto"` (default), `"in-process"`, `"tmux"`. Override per-session: `claude --teammate-mode in-process`. Split pane requires tmux or iTerm2 with it2 CLI.

Require plan approval: tell lead to "require plan approval before they make changes" -- teammate stays in read-only plan mode until lead approves. Lead makes approval decisions autonomously.

Team state stored locally: `~/.claude/teams/{session-name}/config.json`, `~/.claude/tasks/{session-name}/` (where `session-name` = `session-<first-8-chars-of-session-id>`). Do not hand-author these files. Task list directories persist on disk even after session ends (retention governed by `cleanupPeriodDays`).

## Worktrees

`isolation: "worktree"` on Agent tool (or subagent frontmatter) for git-isolated parallel work. Worktree auto-cleaned if no changes; branch returned if changes made. Also available via `EnterWorktree`/`ExitWorktree` tools. Use for parallel sessions, A/B experimentation, or `/batch` skill.
