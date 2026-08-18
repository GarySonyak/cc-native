# Hooks

26+ lifecycle events, 4 hook types. Defined in settings.json under `hooks` key.

## Events by category

- Session: `SessionStart`, `SessionEnd`, `Setup` (matcher: `init`/`maintenance` -- fires on `--init-only`/`--init`/`--maintenance` flags), `InstructionsLoaded`, `ConfigChange`, `CwdChanged`, `DirectoryAdded` (fires after `/add-dir` or SDK `register_repo_root` registers a new working directory mid-session; matcher: `slash_command`/`register_repo_root`) (v2.1.219)
- User input: `UserPromptSubmit`, `UserPromptExpansion` (fires when user command expands; can block), `Elicitation`, `ElicitationResult`
- Tool: `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch` (fires after full parallel tool batch, before next model call; no matcher -- always fires) (v2.1.121)
- Notification: `Notification`
- Subagent: `SubagentStart`, `SubagentStop`
- Task: `TaskCreated`, `TaskCompleted`, `TeammateIdle`
- File: `FileChanged`
- Worktree: `WorktreeCreate`, `WorktreeRemove`
- Context: `PreCompact`, `PostCompact`
- Stop: `Stop`, `StopFailure`
- Display: `MessageDisplay` (v2.1.152) -- fires when assistant message text is about to be displayed; hook can transform or suppress the text before it reaches the terminal
- Auto mode: `PermissionDenied` (v2.1.88 -- fires after auto mode classifier denial, including denials with no classifier verdict at all; return `{retry: true}` to let model retry — Claude Code ignores `retry` specifically when the classifier produced no verdict)

## Hook types

`command` (shell), `http` (webhook), `prompt` (single-turn LLM eval), `agent` (multi-turn with tools, up to 50 tool-use turns, default 60s timeout), `mcp_tool` (invoke MCP tool directly, v2.1.118). Command hooks: optional `args: string[]` field runs command in exec mode (bypasses shell — no interpolation, avoids injection); without `args`, command string is passed to shell. (v2.1.139)

Common per-hook fields: `type` (required), `if` (permission rule filter, tool events only), `timeout` (seconds, default 600 for command/http/mcp_tool; UserPromptSubmit lowers to 30, MessageDisplay to 10, `prompt` type to 30, `agent` type to 60), `statusMessage` (custom spinner text shown while hook runs), `once` (bool: fire only once per session; only honored in skill/agent frontmatter hooks). Command hook async fields: `async: true` — runs hook in background without blocking the model loop; `asyncRewake: true` — implies `async`, and additionally wakes Claude when the background hook exits code 2; hook's stderr (or stdout if stderr is empty) is shown to Claude as a system reminder so it can react to long-running background failures. Command hooks also accept `shell: "bash"|"powershell"` (default bash) to run that specific hook via PowerShell regardless of the global `CLAUDE_CODE_USE_POWERSHELL_TOOL` setting. HTTP hooks (`type: "http"`) take `url` (required), `headers`, and `allowedEnvVars` (env var names whose values `$VAR`/`${VAR}` in `headers` may resolve to; unlisted vars resolve empty).

Path placeholders usable in any hook command/args: `${CLAUDE_PROJECT_DIR}` (project root), `${CLAUDE_PLUGIN_ROOT}` (plugin's versioned install path), `${CLAUDE_PLUGIN_DATA}` (plugin's persistent data directory — survives plugin updates, unlike `CLAUDE_PLUGIN_ROOT`).

`PermissionRequest` hooks don't fire in non-interactive mode (`-p` flag) since there's no dialog to answer — use `PreToolUse` for automated permission decisions there instead. Exception: background subagents can't show a prompt even in an interactive session's non-interactive-mode call path — Claude Code still runs the matching hooks, and if none of them return a decision, the call is denied by default.

`prompt`-type `PreToolUse`/`PostToolUse` hooks returning `"ok": false`: by default the turn ends and `reason` shows as a warning line in chat; set `continueOnBlock: true` to instead feed `reason` back to Claude as the tool error/deny reason so it can adjust and continue. Before v2.1.210, a `PreToolUse` prompt-hook deny always returned the reason to Claude as the tool error and the turn continued (the opposite default). `SessionEnd` hooks of any type share one combined 1.5s timeout budget across all of them; setting a longer per-hook `timeout` raises that shared budget, capped at 60s.

**Bash `if` matching mechanics**: leading env-var assignments are stripped before matching (`Bash(git *)` matches `FOO=bar git push`); each subcommand of a compound command (`&&`, `;`, `|`) is checked separately (`Bash(git *)` matches `npm test && git push`); commands nested in `$()` or backticks are also checked (`Bash(rm *)` matches `echo $(rm -rf /)`, but not `echo $(date)` since no subcommand matches). A single-segment `dir/**` pattern in `if:` now matches only `<cwd>/dir` (was any-depth before v2.1.214) — write `**/dir/**` for any-depth matching; matches the same fix to `permissions.allow` rules (see modes-and-permissions.md). The `if` filter fails open (hook still runs) when the Bash command can't be parsed into subcommands — it's best-effort, so use permission rules, not `if`, for a hard allow/deny guarantee.

## Matchers

Regex on event metadata: tool name (`PreToolUse`/`PostToolUse`/`PostToolUseFailure`/`PermissionRequest`/`PermissionDenied`), session source (`SessionStart`), agent type (`SubagentStart`/`SubagentStop`), MCP server name (`Elicitation`/`ElicitationResult`), notification type (`Notification`), command name (`UserPromptExpansion`), `manual`/`auto` (`PreCompact`/`PostCompact`), `init`/`maintenance` (`Setup`). Exact-string match when matcher uses only letters/digits/`_`/`|`/`-`/spaces/`,`. As of v2.1.191, `,` is interchangeable with `|` as a list separator (e.g., `Edit,Write` ≡ `Edit|Write`). (v2.1.191) As of v2.1.195, matchers with hyphens (e.g., `mcp__brave-search`, `code-reviewer`) also exact-match correctly; before v2.1.195, hyphenated tool names were incorrectly treated as regex substring patterns. Per-event notes below cover `ConfigChange`/`InstructionsLoaded`/`SessionEnd`/`StopFailure`/`FileChanged` matcher values. `if` field (v2.1.85+): permission rule syntax for tool name + argument filtering. Only works on tool events (PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, and — previously uncaptured — PermissionDenied); adding it to any other event prevents the hook from running.

## Exit codes

`0` = proceed, `2` = block (stderr -> Claude feedback), other = proceed + log.

`PreToolUse`/`PostToolUse` fire on every tool call except `EndConversation`, which skips both. Hook output (stdout/stderr shown to Claude) is capped at 10,000 characters.

## Structured JSON output

Universal fields on any hook's JSON output: `continue` (bool), `stopReason` (message shown when `continue: false`), `systemMessage` (warning text shown to the user), `suppressOutput` (bool), `terminalSequence`.

`permissionDecision` (allow/deny/ask/defer) for PreToolUse; `UserPromptSubmit` hookSpecificOutput accepts `sessionTitle: "name"` to set session name and `additionalContext: "..."` to inject context. `decision: "block"` for `UserPromptSubmit`, `UserPromptExpansion`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `Stop` (see "Plugin hook gotchas" — `decision: "block"` triggers a synthetic user-relay message that re-invokes the model and can re-fire the Stop hook), `SubagentStop`, `ConfigChange`, `PreCompact`; `behavior` for PermissionRequest. `defer` (PreToolUse, non-interactive `-p` only): pauses for SDK wrapper to collect input and resume. `PermissionRequest` hook can return `updatedPermissions: [{type: "setMode", mode: "acceptEdits|auto|...", destination: "session"}]` to programmatically change permission mode.

- `updatedInput: { ... }` — in PreToolUse hookSpecificOutput; replaces the tool's input before execution (e.g., sanitize a command or swap a file path). Only the fields you include are replaced; omitted fields keep their original values.
- `continueOnBlock: true` — in PostToolUse/PostToolUseFailure JSON output; blocks the tool result but keeps the agent loop running (default: loop stops on block). (v2.1.139)
- `terminalSequence: "<escape-string>"` — in any hook JSON output; CC emits this as a terminal escape sequence (useful for desktop notifications, bell, etc.). (v2.1.141)

## Location hierarchy

managed policy > user `settings.json` > project `settings.json` > local `settings.local.json` > plugin `hooks.json` > skill/agent frontmatter.

Browse: `/hooks`. Disable all: `disableAllHooks: true`.

## Event-specific notes

- `SessionStart`: matcher values: `startup` (fresh launch), `resume` (--resume/--continue), `clear` (/clear), `compact` (post-compaction reload), `fork` (session begins as a fork of another session — before v2.1.214 this reported as `resume`). hookSpecificOutput also accepts `watchPaths: ["path/to/watch", ...]` to register additional file paths for `FileChanged` events (paths watched only while session is running); `reloadSkills: true` to trigger a skill directory re-scan at session start (v2.1.153); `sessionTitle: "name"` to set the session name at startup (v2.1.153).
- `CwdChanged`: fires when Claude cd's. Write to `CLAUDE_ENV_FILE` to persist env vars.
- `FileChanged`: matcher specifies filenames to watch (pipe-separated). Configures which files are watched AND filters hook execution.
- `ConfigChange`: matcher filters by config type: `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills`.
- `InstructionsLoaded`: matcher filters by load reason: `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact`.
- `SessionEnd`: matcher filters by reason: `clear`, `resume`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other`.
- `Notification`: matcher filters by notification type: `permission_prompt` (tool-use approval needed), `idle_prompt` (Claude waiting for next message), `auth_success` (authentication completed), `elicitation_dialog` (MCP server opened elicitation form), `elicitation_url_dialog` (MCP server asks you to open a browser URL), `elicitation_complete` (form submitted/dismissed), `elicitation_response` (response sent back to server), `agent_needs_input`/`agent_completed` (background session needs input / finishes or fails; fire only while Agent View is open, v2.1.198). Empty matcher fires on all notification types.
- `TeammateIdle`: exit code 2 to send feedback and keep teammate working (agent teams).
- `TaskCreated`/`TaskCompleted`: exit code 2 to prevent and send feedback.
- `PreCompact`: exit code 2 to block compaction (v2.1.105).
- `StopFailure`: matcher filters by error type: `rate_limit`, `overloaded`, `authentication_failed`, `oauth_org_not_allowed`, `billing_error`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, `unknown`.
- `Stop` block cap: Claude Code overrides a `Stop` hook after it blocks **8 times in a row** without progress (ends the turn with a warning instead). Check the `stop_hook_active` input field and exit 0 early if `true` to avoid tripping the cap on legitimate re-checks. Raise the cap with `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`.
- `PostToolUse`/`PostToolUseFailure`: include `duration_ms` (v2.1.119); `PostToolUse` can replace tool output for any tool (v2.1.121).
- All hooks: `effort.level` field in JSON input contains the active effort level (low/medium/high/xhigh/max). `$CLAUDE_EFFORT` env var also set for command hooks. Use to conditionally adjust hook behavior per effort. (v2.1.133)
- All hooks: `prompt_id` — UUID for the current user prompt, included in every hook's JSON input; correlate multiple hook firings (PreToolUse, PostToolUse, etc.) back to the same user turn. (v2.1.196)
- All hooks (env vars): `CLAUDE_CODE_REMOTE` = `"true"` in remote environments; `CLAUDE_CODE_BRIDGE_SESSION_ID` = Remote Control session ID. (v2.1.199+)
- `WorktreeCreate`: command hooks return path on stdout; HTTP hooks return `hookSpecificOutput.worktreePath`. Hook failure or missing path fails worktree creation.
- `SessionStart`/`Setup`: `hookSpecificOutput.additionalContext` injects text into Claude's context. `SessionStart` also accepts plain stdout (single hook); `Setup` concatenates `additionalContext` from multiple hooks.
- **`Stop`/`SubagentStop` hooks can return `hookSpecificOutput.additionalContext` (v2.1.163/164)**: these events join SessionStart/Setup/UserPromptSubmit in supporting the nested `hookSpecificOutput: { hookEventName: "...", additionalContext: "..." }` format to inject context. Note: the top-level `additionalContext` field in hook JSON output is available to all hooks (general); the nested `hookSpecificOutput.additionalContext` path is event-specific.

## Multiple hooks on the same event

All hooks matching an event run in parallel to completion before Claude Code merges results; one hook's `deny` doesn't stop sibling hooks from running their side effects. For `PreToolUse`, the most restrictive `permissionDecision` wins in the order `deny` > `defer` > `ask` > `allow`. A hook `"allow"` never overrides a `deny`/`ask` permission **rule** from settings (including managed settings) — hooks can tighten but not loosen what the rule system already decided. When multiple `PreToolUse` hooks return `updatedInput`, the last one to finish is applied (non-deterministic since hooks run in parallel) — avoid having more than one hook rewrite the same tool's input.

## Plugin hook gotchas

- **`${CLAUDE_PLUGIN_ROOT}` is pinned at session start.** When a session boots, the harness resolves `${CLAUDE_PLUGIN_ROOT}` to the currently-active plugin install path and stores it in the running process. `claude plugin update` writes a new `installPath` to `installed_plugins.json` but does NOT re-resolve the env var — hooks invoked via `python ${CLAUDE_PLUGIN_ROOT}/hooks/foo.py` continue running the OLD version's file until either `/reload-plugins` runs or the session restarts. To hot-patch a hook in a live session, overwrite the file at the version path active when the session started, not the latest installed version. Diagnostic: log `__file__` from inside the hook on first fire and compare to the latest `installPath` in `installed_plugins.json`.
- **Subagent-spawn tool is named `Agent` in the SDK / newer harness, not `Task`.** Older Claude Code recorded subagent invocations as `tool_use{name: "Task"}` in the transcript; the SDK and recent CC builds use `name: "Agent"`. A hook that detects subagent calls must accept both names (e.g., `SUBAGENT_TOOLS = {"Task", "Agent"}`) — assuming only `"Task"` will silently miss every subagent invocation in newer harnesses.
- **Stop hook re-fires on `decision: "block"` user-relay messages.** When a Stop hook returns `{"decision": "block", "reason": "..."}`, Claude Code injects the reason as a synthetic user message and runs the model again. That synthetic message is recorded as `type: "user"` in the transcript, so any loop guard that anchors "since the last real user turn" will treat the relay as a fresh boundary and re-fire indefinitely. Anchor loop guards on the corrective action (e.g., the subagent invocation) instead, or filter relay messages explicitly.
- **`type: "user"` records also wrap tool results.** Claude Code stores `tool_use_result` blocks inside synthetic `user` records (top-level `toolUseResult` key, or `message.content` containing a `tool_result` block). Counting every `type: "user"` line as a real user turn slides the boundary forward on every tool call. If you must detect real user turns, exclude records carrying tool results.
