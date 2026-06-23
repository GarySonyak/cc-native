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
- `autoMode.hard_deny`: array of prose rules blocking unconditionally — user intent and `allow` exceptions do not apply. Include `"$defaults"` to preserve built-in exfiltration/safety-bypass blocks. For tool-pattern blocks before the classifier, use `permissions.deny`. (v2.1.136)
- `alwaysThinkingEnabled`: enable extended thinking by default for all sessions.
- `outputStyle`: set a named output style to adjust system prompt (e.g. "Explanatory").
- `httpHookAllowedEnvVars`: allowlist of env var names HTTP hooks may interpolate into headers.
- `showThinkingSummaries`: show extended thinking summaries in interactive sessions (default: false).
- `DISABLE_UPDATES` env var: block all update paths; useful for managed/locked deployments. (v2.1.118)
- `prUrlTemplate`: custom code-review URLs (v2.1.119).
- `skillOverrides`: globally control skill auto-invocation — `off` (model sees no skills), `user-invocable-only` (model sees only user-invocable skills), `name-only` (model sees skill names but not descriptions). Scoped to user/project settings. (v2.1.129)
- `worktree.baseRef`: `fresh` (branch worktrees from `origin/<default>`) or `head` (branch from local `HEAD`). Controls worktree base commit. (v2.1.133)
- `skillListingBudgetFraction`: fraction of context window reserved for skill descriptions in the skill listing (e.g. `0.02` = 2%). Complements `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var. Low-priority skill descriptions are dropped first when budget overflows; run `/doctor` to diagnose.
- `maxSkillDescriptionChars`: per-skill description char cap in the skill listing (default 1536). Configures the per-entry truncation applied to combined `description`+`when_to_use` text.
- `worktree.bgIsolation`: `"none"` lets background agents edit the main working copy directly instead of running in a worktree. Use when direct file access outweighs isolation benefits for background tasks. (v2.1.143)

- `fallbackModel`: list of up to three fallback models tried in order when the primary model is overloaded or unavailable; CC also retries once on the first fallback for unexpected non-retryable errors. (v2.1.166)
- `disableBundledSkills`: `true` hides bundled skills (`/code-review`, `/batch`, `/debug`, `/loop`, etc.) and built-in commands from the model — they won't auto-invoke or appear in skill listings. User can still run them manually with `/skill-name`. (v2.1.169)
- `--safe-mode` CLI flag (equiv: `CLAUDE_CODE_SAFE_MODE=1` env var): disables all customizations at startup — CLAUDE.md, plugins, skills, hooks, and MCP servers are all skipped. Use for troubleshooting to isolate whether a custom config is causing a problem. Not a settings key; must be passed at launch. (v2.1.169)
- `workflowKeywordTriggerEnabled`: `false` prevents the "ultracode" effort keyword from triggering automatic Workflow tool orchestration (default: `true`). Use to disable ultracode's multi-agent escalation while keeping the effort level keyword. (v2.1.157)
- `disableWorkflows`: `true` disables the Workflow tool entirely — dynamic workflow scripts cannot be created or run. Useful for locked-down environments that should not spawn background agent workflows.

- `advisorModel`: advisor model alias (`opus`, `sonnet`, `fable`) or full model ID; Claude consults this model at key decision points mid-task. Experimental, Anthropic API only. Fable 5 requires v2.1.170+. Disable with `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`. (v2.1.98+)
- `enforceAvailableModels`: `true` constrains the Default model selection to the `availableModels` allowlist (not just manual `/model` picks). Ensures the session starting model also respects the model allowlist.
- `cleanupPeriodDays`: number of days to retain subagent transcript files at `~/.claude/projects/{project}/{sessionId}/subagents/`. Default: 30.

- `sandbox.allowAppleEvents`: `true` permits sandboxed Bash processes to send Apple Events on macOS (required for AppleScript and some GUI automations in sandbox mode). (v2.1.181)
- `disableArtifact`: `true` disables the Artifact tool — prevents publishing session output as interactive pages on claude.ai. (v2.1.183)
- `teammateMode` options now include `"iterm2"` — iTerm2 native split panes (requires `it2` CLI). Previously only `"in-process"`, `"auto"`, `"tmux"`. (v2.1.186)
- `respondToBashCommands`: `false` opts out of `!` bash commands automatically triggering Claude's response loop (default `true` as of v2.1.186 — `!` commands now elicit an automatic Claude response). (v2.1.186)

Managed-only settings (`disable*`, `allow*Only`, `sandbox.*.allowManaged*Only`, plugin/marketplace policy keys like `pluginTrustMessage`/`strictKnownMarketplaces`/`blockedMarketplaces`/`channelsEnabled`/`allowedChannelPlugins`, `minimumVersion`, `wslInheritsWindowsSettings`, `subagentStatusLine`) intentionally excluded -- see `/en/settings#available-settings` for the full enterprise list.
