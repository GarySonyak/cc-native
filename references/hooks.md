# Hooks

26+ lifecycle events, 4 hook types. Defined in settings.json under `hooks` key.

## Events by category

- Session: `SessionStart`, `SessionEnd`, `InstructionsLoaded`, `ConfigChange`, `CwdChanged`
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

Regex on tool name (PreToolUse/PostToolUse), session source (SessionStart), agent type (SubagentStart/Stop), etc. `if` field (v2.1.85+): permission rule syntax for tool name + argument filtering. Only works on tool events (PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest).

## Exit codes

`0` = proceed, `2` = block (stderr -> Claude feedback), other = proceed + log.

## Structured JSON output

`permissionDecision` (allow/deny/ask/defer) for PreToolUse; `decision: "block"` for PostToolUse/Stop; `behavior` for PermissionRequest. `defer` (PreToolUse, non-interactive `-p` only): pauses for SDK wrapper to collect input and resume. `PermissionRequest` hook can return `updatedPermissions: [{type: "setMode", mode: "acceptEdits|auto|...", destination: "session"}]` to programmatically change permission mode.

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
