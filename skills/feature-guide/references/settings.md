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
- `maxSkillDescriptionChars`: per-skill description char cap in the skill listing (default 1536). Configures the per-entry truncation applied to combined `description`+`when_to_use` text. Doc note: current live settings/skills docs name this key `skillListingMaxDescChars` — likely the same setting under a later name; unconfirmed which is authoritative, don't delete either reference pending confirmation.
- **Resolved (2026-07-11)**: `skillListingMaxDescChars` is confirmed authoritative — seen consistently across multiple independent live fetches of the skills page; `maxSkillDescriptionChars` has never appeared in a live fetch.
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
- `enableArtifact`: user-level override to re-enable the Artifact tool for yourself when a higher (e.g. managed/project) scope set `disableArtifact`.
- `teammateMode` options now include `"iterm2"` — iTerm2 native split panes (requires `it2` CLI). Previously only `"in-process"`, `"auto"`, `"tmux"`. (v2.1.186)
- `respondToBashCommands`: `false` opts out of `!` bash commands automatically triggering Claude's response loop (default `true` as of v2.1.186 — `!` commands now elicit an automatic Claude response). (v2.1.186)
- `sandbox.credentials`: controls whether sandboxed Bash commands can read credential files and secret environment variables; set to restrict access (new security boundary for sandbox mode). (v2.1.187)
- `autoMode.classifyAllShell`: `true` routes ALL Bash/PowerShell commands through the auto-mode classifier — including reads and working-dir edits normally auto-approved in auto mode. Tightens auto mode safety at the cost of slightly more latency per shell command. (v2.1.193)
- `askUserQuestionTimeout`: idle auto-continue delay for `AskUserQuestion` dialogs — `60s`/`5m`/`10m`; unset = never auto-continues. Does not apply to permission prompts. (v2.1.200)
- `disableClaudeAiConnectors`: `true` disables claude.ai MCP connectors in Claude Code (any-source-true: a project-level `false` cannot re-enable what user/policy `true` disabled). Env var equivalent: `ENABLE_CLAUDEAI_MCP_SERVERS=false`.

- `axScreenReader`: opt-in plain-text rendering mode for screen readers; equivalent to `--ax-screen-reader` CLI flag / `CLAUDE_AX_SCREEN_READER=1` env var. (v2.1.208)
- `vimInsertModeRemaps`: define Vim insert-mode key sequences (e.g. `jj` → Escape) when Vim mode is enabled.
- `CLAUDE_CODE_PROCESS_WRAPPER`: env var pointing at a corporate/enterprise launcher wrapper script around the `claude` process. (v2.1.208)
- `sandbox.filesystem.disabled`: `true` skips filesystem isolation while keeping the sandbox's network egress control active — use when you want network restrictions but not filesystem sandboxing. (v2.1.216)
- `sandbox.network.strictAllowlist`: `true` denies non-allowlisted hosts outright for sandboxed commands with no permission prompt (vs. the default ask-then-remember behavior). (v2.1.219)
- `workflowSizeGuideline`: sets the advisory Dynamic workflow size guideline (default: medium, aim for <15 agents) from any settings file; the `/config` row hides while one is set. (v2.1.219)
- `crossSessionInbound` / `dialogExpiry`: gate cross-session `SendMessage` — a message to a session running with bypassed permissions is held for approval (`crossSessionInbound`) for up to `dialogExpiry` before auto-expiring; messages to other sessions auto-deliver. See agents.md. (v2.1.224) Both now also have `/config` rows — "Messages from your other sessions" (`crossSessionInbound`) and "Dialog expiry" (`dialogExpiry`) — the inbound row hides when a higher-precedence scope (managed/`--settings`) already sets the key. (v2.1.232)
- Sandbox credential-masking (user/managed/`--settings` scopes only, requires `network.tlsTerminate`): `extract`/`onExtractNoMatch` for structured env values, `decode: "jwt"` + `maskClaims` for JWT-aware masking, `awsPairs`/`sigv4` for AWS SigV4 re-signing. `mode: "mask"` on sandbox credential files (Linux/WSL): sandboxed commands see a sentinel copy while the sandbox proxy substitutes the real value on egress; macOS falls back to `deny`. (v2.1.221/v2.1.224)
- `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` / `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`: subagent concurrency and nesting-depth caps — see agents.md. (v2.1.217/v2.1.219)
- `CLAUDE_CODE_PROJECT_DIR_NAME`: overrides the per-project transcript directory name under `~/.claude/projects/` (default derives from the working directory path). (v2.1.234)
- `spellcheck`: optional setting that underlines misspelled words in the prompt input as you type, using your installed `aspell`, `hunspell`, or `ispell`. (v2.1.235)
- `ANTHROPIC_DEFAULT_MODEL` env var: sets the model new sessions start on. Unlike `ANTHROPIC_MODEL`, a later `/model` pick overrides it and persists across restarts. (v2.1.236)
- Built-in **"Concise"** output style added to the `outputStyle` picker: Claude leads with results and skips preamble/narration while doing the work just as thoroughly. Select under Output style in `/config`. (v2.1.237)
- `keybindingFlavor`: set to `"readline"` to make Ctrl+W in the prompt input delete back to the previous whitespace, Bash/readline-style; default `"classic"` is unchanged. (v2.1.238)

Managed-only settings (`disable*`, `allow*Only`, `sandbox.*.allowManaged*Only`, plugin/marketplace policy keys like `pluginTrustMessage`/`strictKnownMarketplaces`/`blockedMarketplaces`/`channelsEnabled`/`allowedChannelPlugins`, `minimumVersion`, `wslInheritsWindowsSettings`, `subagentStatusLine`) intentionally excluded -- see `/en/settings#available-settings` for the full enterprise list.
