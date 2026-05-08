# Key Settings (notable additions since 2026-03-31)

- `autoUpdatesChannel`: "stable" (tested ~1wk old) or "latest" (default) release channel.
- `availableModels`: restrict which models users can select via /model, --model, ANTHROPIC_MODEL.
- `attribution`: customize git commit/PR co-author byline (replaces deprecated `includeCoAuthoredBy`).
- `allowedHttpHookUrls`: allowlist URL patterns for HTTP hooks (supports * wildcard).
- `includeGitInstructions`: false removes built-in git workflow instructions from system prompt.
- `language`: set Claude response language globally (e.g. "japanese", "french").
- `plansDirectory`: customize where plan files stored (default: ~/.claude/plans).
- `useAutoModeDuringPlan`: plan mode uses auto mode semantics when available (default: true).
- `worktree.symlinkDirectories`: symlink large dirs (node_modules etc) into worktrees to save disk.
- `worktree.sparsePaths`: sparse checkout specific paths in worktrees for faster startup.
- `fastModePerSessionOptIn`: true = fast mode not persistent, must enable per session with /fast.
- `forceRemoteSettingsRefresh`: managed only -- blocks startup until remote settings fetched. (v2.1.92)
- `modelOverrides`: map Anthropic model IDs to provider-specific IDs (Bedrock ARNs etc).
- `feedbackSurveyRate`: probability 0-1 for session quality survey (0 to suppress entirely).
- `defaultShell`: "powershell" routes input-box `!` commands through PowerShell (requires `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`).
- `effortLevel`: persist effort level across sessions (low/medium/high); default now "high" for Team/Enterprise/API/Bedrock/Vertex/Foundry. (v2.1.94)
- `agent`: run main session thread as a named subagent (applies its system prompt, tool restrictions, model).
- `autoMode`: customize auto mode classifier -- `environment`, `allow`, `soft_deny` arrays; not read from shared project settings. Include `"$defaults"` in allow/deny arrays to add custom rules alongside built-in lists (v2.1.118).
- `alwaysThinkingEnabled`: enable extended thinking by default for all sessions.
- `outputStyle`: set a named output style to adjust system prompt (e.g. "Explanatory").
- `httpHookAllowedEnvVars`: allowlist of env var names HTTP hooks may interpolate into headers.
- `showThinkingSummaries`: show extended thinking summaries in interactive sessions (default: false).
- `DISABLE_UPDATES` env var: block all update paths; useful for managed/locked deployments. (v2.1.118)
- `prUrlTemplate`: custom code-review URLs (v2.1.119).
- `skillOverrides`: globally control skill auto-invocation — `off` (model sees no skills), `user-invocable-only` (model sees only user-invocable skills), `name-only` (model sees skill names but not descriptions). Scoped to user/project settings. (v2.1.129)
- `worktree.baseRef`: `fresh` (branch worktrees from `origin/<default>`) or `head` (branch from local `HEAD`). Controls worktree base commit. (v2.1.133)

Managed-only settings (`disable*`, `allow*Only`, `sandbox.*.allowManaged*Only`, plugin/marketplace policy keys like `pluginTrustMessage`/`strictKnownMarketplaces`/`blockedMarketplaces`/`channelsEnabled`/`allowedChannelPlugins`, `minimumVersion`, `wslInheritsWindowsSettings`, `subagentStatusLine`) intentionally excluded -- see `/en/settings#available-settings` for the full enterprise list.
