# Hooks

26+ lifecycle events, 4 hook types. Defined in settings.json under `hooks` key.

## Events by category

- Session: `SessionStart`, `SessionEnd`, `Setup` (matcher: `init`/`maintenance` -- fires on `--init-only`/`--init`/`--maintenance` flags), `InstructionsLoaded`, `ConfigChange`, `CwdChanged`
- User input: `UserPromptSubmit`, `UserPromptExpansion` (fires when user command expands; can block), `Elicitation`, `ElicitationResult`
- Tool: `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch` (fires after full parallel tool batch, before next model call; no matcher -- always fires) (v2.1.121)
- Notification: `Notification`
- Subagent: `SubagentStart`, `SubagentStop`
- Task: `TaskCreated`, `TaskCompleted`, `TeammateIdle`
- File: `FileChanged`
- Worktree: `WorktreeCreate`, `WorktreeRemove`
- Context: `PreCompact`, `PostCompact`
- Stop: `Stop`, `StopFailure`
- Auto mode: `PermissionDenied` (v2.1.88 -- fires after auto mode classifier denial; return `{retry: true}` to let model retry)

## Hook types

`command` (shell), `http` (webhook), `prompt` (single-turn LLM eval), `agent` (multi-turn with tools, up to 50 tool-use turns, default 60s timeout), `mcp_tool` (invoke MCP tool directly, v2.1.118).

## Matchers

Regex on event metadata: tool name (`PreToolUse`/`PostToolUse`/`PostToolUseFailure`/`PermissionRequest`/`PermissionDenied`), session source (`SessionStart`), agent type (`SubagentStart`/`SubagentStop`), MCP server name (`Elicitation`/`ElicitationResult`), notification type (`Notification`), command name (`UserPromptExpansion`), `manual`/`auto` (`PreCompact`/`PostCompact`), `init`/`maintenance` (`Setup`). Exact-string match when matcher uses only letters/digits/`_`/`|`. Per-event notes below cover `ConfigChange`/`InstructionsLoaded`/`SessionEnd`/`StopFailure`/`FileChanged` matcher values. `if` field (v2.1.85+): permission rule syntax for tool name + argument filtering. Only works on tool events (PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest).

## Exit codes

`0` = proceed, `2` = block (stderr -> Claude feedback), other = proceed + log.

## Structured JSON output

`permissionDecision` (allow/deny/ask/defer) for PreToolUse; `decision: "block"` for `UserPromptSubmit`, `UserPromptExpansion`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `Stop` (see "Plugin hook gotchas" — `decision: "block"` triggers a synthetic user-relay message that re-invokes the model and can re-fire the Stop hook), `SubagentStop`, `ConfigChange`, `PreCompact`; `behavior` for PermissionRequest. `defer` (PreToolUse, non-interactive `-p` only): pauses for SDK wrapper to collect input and resume. `PermissionRequest` hook can return `updatedPermissions: [{type: "setMode", mode: "acceptEdits|auto|...", destination: "session"}]` to programmatically change permission mode.

## Location hierarchy

managed policy > user `settings.json` > project `settings.json` > local `settings.local.json` > plugin `hooks.json` > skill/agent frontmatter.

Browse: `/hooks`. Disable all: `disableAllHooks: true`.

## Event-specific notes

- `CwdChanged`: fires when Claude cd's. Write to `CLAUDE_ENV_FILE` to persist env vars.
- `FileChanged`: matcher specifies filenames to watch (pipe-separated). Configures which files are watched AND filters hook execution.
- `ConfigChange`: matcher filters by config type: `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills`.
- `InstructionsLoaded`: matcher filters by load reason: `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact`.
- `SessionEnd`: matcher filters by reason: `clear`, `resume`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other`.
- `TeammateIdle`: exit code 2 to send feedback and keep teammate working (agent teams).
- `TaskCreated`/`TaskCompleted`: exit code 2 to prevent and send feedback.
- `PreCompact`: exit code 2 to block compaction (v2.1.105).
- `StopFailure`: matcher filters by error type: `rate_limit`, `authentication_failed`, `billing_error`, `invalid_request`, `server_error`, `max_output_tokens`, `unknown`.
- `PostToolUse`/`PostToolUseFailure`: include `duration_ms` (v2.1.119); `PostToolUse` can replace tool output for any tool (v2.1.121).
- All hooks: `effort.level` field in JSON input contains the active effort level (low/medium/high/xhigh/max). `$CLAUDE_EFFORT` env var also set for command hooks. Use to conditionally adjust hook behavior per effort. (v2.1.133)
- `WorktreeCreate`: command hooks return path on stdout; HTTP hooks return `hookSpecificOutput.worktreePath`. Hook failure or missing path fails worktree creation.
- `SessionStart`/`Setup`: `hookSpecificOutput.additionalContext` injects text into Claude's context. `SessionStart` also accepts plain stdout (single hook); `Setup` concatenates `additionalContext` from multiple hooks.

## Plugin hook gotchas

- **`${CLAUDE_PLUGIN_ROOT}` is pinned at session start.** When a session boots, the harness resolves `${CLAUDE_PLUGIN_ROOT}` to the currently-active plugin install path and stores it in the running process. `claude plugin update` writes a new `installPath` to `installed_plugins.json` but does NOT re-resolve the env var — hooks invoked via `python ${CLAUDE_PLUGIN_ROOT}/hooks/foo.py` continue running the OLD version's file until either `/reload-plugins` runs or the session restarts. To hot-patch a hook in a live session, overwrite the file at the version path active when the session started, not the latest installed version. Diagnostic: log `__file__` from inside the hook on first fire and compare to the latest `installPath` in `installed_plugins.json`.
- **Subagent-spawn tool is named `Agent` in the SDK / newer harness, not `Task`.** Older Claude Code recorded subagent invocations as `tool_use{name: "Task"}` in the transcript; the SDK and recent CC builds use `name: "Agent"`. A hook that detects subagent calls must accept both names (e.g., `SUBAGENT_TOOLS = {"Task", "Agent"}`) — assuming only `"Task"` will silently miss every subagent invocation in newer harnesses.
- **Stop hook re-fires on `decision: "block"` user-relay messages.** When a Stop hook returns `{"decision": "block", "reason": "..."}`, Claude Code injects the reason as a synthetic user message and runs the model again. That synthetic message is recorded as `type: "user"` in the transcript, so any loop guard that anchors "since the last real user turn" will treat the relay as a fresh boundary and re-fire indefinitely. Anchor loop guards on the corrective action (e.g., the subagent invocation) instead, or filter relay messages explicitly.
- **`type: "user"` records also wrap tool results.** Claude Code stores `tool_use_result` blocks inside synthetic `user` records (top-level `toolUseResult` key, or `message.content` containing a `tool_result` block). Counting every `type: "user"` line as a real user turn slides the boundary forward on every tool call. If you must detect real user turns, exclude records carrying tool results.
