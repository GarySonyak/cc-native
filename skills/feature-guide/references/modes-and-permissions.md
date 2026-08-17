# Plan Mode, Permission Modes, Auto Mode, Checkpointing

## Plan Mode

Read-only exploration -- no edits allowed. Outputs plan file to `.claude/plans/`. Exit with `ExitPlanMode` when ready. On exit: choose auto, acceptEdits, or manual review for implementation. Cycle modes with **Shift+Tab**: default -> acceptEdits -> plan (auto only enters cycle with `--enable-auto-mode`). Enter plan mode for one request with `/plan <description>`. Accepting a plan auto-names the session from plan content (unless already named via `--name` or `/rename`). Press `Ctrl+G` to edit the proposed plan in your text editor before Claude proceeds.

## Permission Modes

6 modes -- cycle with **Shift+Tab** (default -> acceptEdits -> plan). Auto appears in cycle only with `--enable-auto-mode` flag and Team/Enterprise/API plan:

| Mode | Behavior |
|------|----------|
| `default` | Read files freely, ask for edits/bash |
| `acceptEdits` | Read + edit freely, ask for bash |
| `plan` | Read-only, no edits |
| `auto` | Background classifier replaces prompts. Team/Enterprise/API: Sonnet 4.6, Opus 4.6, or Opus 4.7. Max plan: Opus 4.7 only. Fallback after 3 consecutive or 20 total blocks. (v2.1.111) |
| `dontAsk` | Only pre-approved tools; explicit `ask` rules also denied (never in cycle) |
| `bypassPermissions` | Skip all checks (only if started with it) |

`default` mode's UI label is now **Manual** in the CLI, `claude --help`, VS Code, and JetBrains; the config value stays `default`, and `manual` is now an accepted alias anywhere a mode value is set (`--permission-mode manual`, `defaultMode: "manual"`, subagent `permissionMode: manual` frontmatter). Requires v2.1.200+. (v2.1.200)

Remote Control mode reporting (v2.1.202): the permission-mode dropdown on claude.ai/mobile now shows the local session's actual mode live, including mode changes made from the terminal — except `bypassPermissions`, which a session never reports remotely. Before v2.1.202, Remote Control sessions didn't report their mode at all, so the app's dropdown could show a stale or wrong mode; permission prompts themselves always reflected the session's real mode regardless.

Claude Code on the web (cloud sessions) only offers **Accept edits**, **Plan**, and **Auto** — Bypass permissions isn't available. "Accept edits" there actually maps to `default` mode: the cloud sandbox pre-approves file edits regardless of mode, so the dropdown label differs from the underlying mode value. Cloud sessions ignore `defaultMode: "bypassPermissions"`/`"dontAsk"` from checked-in settings and silently start in the mode the dropdown shows instead.

CLI: `--permission-mode <mode>`. Setting: `permissions.defaultMode`. Scheduled tasks: use explicit `--allowedTools` in wrapper.

**Doc update**: current live docs describe the auto mode model requirement more simply — Anthropic API: Opus 4.6 or later, or Sonnet 4.6 or later (so this now includes Opus 4.8 too); Bedrock/Vertex/Foundry/Claude apps gateway: only Sonnet 5, Opus 4.7, Opus 4.8. No plan-tier distinction is called out anymore. The Team/Enterprise/API row above may be stale for the Anthropic-API case now that newer models qualify.

`defaultMode: "auto"` is ignored when set in `.claude/settings.json` or `.claude/settings.local.json` (v2.1.142+, so a repo can't grant itself auto mode) — set it in `~/.claude/settings.json` (or managed settings) instead.

`acceptEdits` mode also auto-approves PowerShell `Set-Content`, `Add-Content`, `Clear-Content`, and `Remove-Item` (plus common aliases) on in-scope paths, mirroring its Bash filesystem-command allowlist, when the PowerShell tool is enabled.

## Protected files & dirs

Protected files (never auto-approved in most modes): `.gitconfig`, `.gitmodules`, `.bashrc`, `.bash_profile`, `.zshrc`, `.zprofile`, `.profile`, `.zshenv`, `.zlogin`, `.bash_login`, `.ripgreprc`, `.mcp.json`, `.claude.json`, `~/.config/git/`. (`.zshenv`, `.zlogin`, `.bash_login`, `~/.config/git/` added v2.1.160.) Protected dirs: `.git`, `.vscode`, `.idea`, `.husky`, `.cargo`, and `.claude` (except `.claude/worktrees` where Claude stores its own git worktrees). Note: as of v2.1.162, `.claude/commands`, `.claude/agents`, and `.claude/skills` are now also protected — the prior exceptions were removed. `.claude-plugin` removed from protected dirs. `bypassPermissions` bypasses ALL protected paths as of v2.1.126 (only `rm -rf /` and `rm -rf ~` still prompt). (v2.1.126)

Additional protected dirs (v2.1.160): `.config/git`, `.devcontainer`, `.yarn`, `.mvn`. Additional protected files (v2.1.160 build-tool config expansion): shell dotfiles `.bash_aliases .bash_logout .zlogout .envrc`; package managers `.npmrc .yarnrc .yarnrc.yml .pnp.cjs .pnp.loader.mjs .pnpmfile.cjs bunfig.toml .bunfig.toml`; build tools `.bazelrc .bazelversion .bazeliskrc`; git hook configs `.pre-commit-config.yaml lefthook.yml lefthook.yaml .lefthook.yml .lefthook.yaml`; build wrappers `gradle-wrapper.properties maven-wrapper.properties`; dev containers `.devcontainer.json`; type checkers `pyrightconfig.json`.

`permissions.allow` rules do **not** pre-approve protected-path writes — the safety check runs before allow rules are evaluated, so e.g. `Edit(.claude/**)` in settings has no effect on the table above. In modes that prompt, the `.claude/` write prompt offers "Yes, and allow Claude to edit its own settings for this session", which pre-approves later `.claude/` writes for that session only.

`acceptEdits` auto-approves: `mkdir touch rm rmdir mv cp sed` (and env-var/process-wrapper prefixes) inside working directory. (v2.1.160) Now also prompts before writing build-tool config files that grant code execution (e.g., files analogous to `package.json` scripts).

## Deny rule glob tool names (v2.1.166)

`permissions.deny` rules now support glob patterns in the **tool-name position** (the part before the parenthesis). Example: `Web*` denies both `WebFetch` and `WebSearch` in a single rule. Previously, tool names in rules were exact-match only; globs only worked inside the argument specifier (e.g. `Bash(npm *)`). (v2.1.166)

## Tool input parameter matching (v2.1.178)

Permission rules now support matching **tool input parameter values** via `Tool(param:value)` syntax (wildcard-enabled):
- `Agent(model:opus)` — block subagents that use any Opus model
- `Agent(model:claude-3*)` — match all claude-3 variant subagents
- Distinct from the existing `Agent(Explore)` type-name form (which matches subagent type, not model parameter)

Use in `permissions.allow` or `permissions.deny` to gate specific model/parameter combinations without blocking the tool entirely. (v2.1.178)

`Cd(path)` permission rule restricts or disables which directories `/cd` can move a session into (v2.1.169+).

## Auto mode subagent spawn evaluation (v2.1.178)

Auto mode now evaluates subagent spawns via the classifier **before** the subagent launches (previously only checked actions taken during the subagent's run). Dangerous delegated tasks blocked at spawn time. (v2.1.178) Full picture (3 checkpoints): (1) task description evaluated before spawn (v2.1.178, above); (2) each action the subagent takes is checked against the same rules as the parent session, with any `permissionMode` in its frontmatter ignored; (3) on completion the classifier reviews the subagent's full action history, and prepends a security warning to its results if that review flags a concern.

## Auto mode safety defaults expanded (v2.1.183)

New built-in blocks added to the classifier (extend existing default block list; use `autoMode.environment` to configure trusted repos/infra):
- **Force push** (`git push --force`) and **direct push to `main`** — blocked when not explicitly requested. (v2.1.183)
- **Destructive git state resets**: `git reset --hard`, `git checkout -- .`, `git restore .`, `git clean -fd`, `git stash drop`, `git stash clear` — presumed to discard uncommitted changes. (v2.1.183)
- **Amending non-session commits**: `git commit --amend` when the HEAD commit was not created in the current session. (v2.1.183)
- **Infrastructure destroy commands**: `terraform destroy`, `pulumi destroy`, `cdk destroy`, `terragrunt destroy`, and applying any plan that destroys resources. (v2.1.183)

## Auto mode safety defaults further expanded (v2.1.195)

`Claude Code v2.1.195+` blocks more categories by default (extends v2.1.183 list; use `autoMode.environment` to configure trusted targets):

**Additional blocks:**
- Writing to secret managers; changing DNS records or TLS certificates
- Merging a PR no human has approved; approving Claude's own PR; disabling CI checks
- Posting comments that are commands to automation (e.g. `atlantis apply`, bot `/deploy` or `/merge`)
- Toggling, ramping, or deleting production feature flags
- Applying IaC changes to a protected scope, or draining/removing cluster nodes
- Writes to a shared compute cluster beyond the named resource (label selector, `--all`)
- Creating DaemonSets or admission webhooks (run on every node / intercept cluster traffic)
- Interactive shells or port-forwards into a sensitive remote target
- Opening a tunnel or reverse shell reachable from the public internet
- Printing a live credential or token to transcript or file
- Accessing or copying from a PII / regulated-data location
- Routing a package install around internal registry to a public one
- Running commands with safety-disarming flags (e.g. `--insecure`)
- Claude in Chrome browser actions sending page content, cookies, or credentials off-origin

**Additional allows (v2.1.195):**
- Deleting exact jobs Claude created earlier in the same session
- Reading, reviewing, or writing security-related code, configs, threat models
- Messages between agents in the same multi-agent session
- Sending data to trusted domains/buckets/services listed in `autoMode.environment`
- Claude in Chrome navigation to trusted internal domain, localhost, or named URL

## Auto mode safety defaults further expanded (v2.1.198)

Extends the v2.1.195 list:
- `git commit --amend` also blocked when the HEAD commit was already pushed. A message-only reword (`--amend -m`, nothing newly staged, on a commit Claude created this session) is still allowed.
- New blocks: deleting files in `/tmp`/`$TMPDIR`/a shared scratch dir by wildcard, glob, or age filter (rather than a specific named path); sharing unauthorized sensitive details with people or shared systems; sending keystrokes to Claude Code's own tmux pane (self-permission escalation).
- Sandbox network verdicts are now cached per host+port instead of re-classified on every connection. An allow is invalidated when new content enters the conversation; a deny is dropped at turn end interactively, or reused for the rest of the run in non-interactive/SDK sessions.

## Auto mode safety defaults further expanded (v2.1.200)

Extends the v2.1.198/v2.1.195 lists:
- New blocks: tampering with tests/assertions that guard security behavior (auth, access control, input validation, sandboxing); deleting/tearing down a stateful resource Claude didn't create this session, when unnamed and no more specific rule applies; repointing an API base URL, proxy, webhook receiver, or registry mirror at an unfit third-party host (including example files like `.env.example`); retargeting `git remote set-url`/`git remote add` push destination unless the new remote was named; pushing secrets or other confidential material to a repo known to be public; opening a PR against a different repo/org, `gh repo fork`, or pushing to a third-party repo, unless that target was named.
- Outbound-content rule extended: PR/issue bodies, commit messages, and comments now count as outbound content for the v2.1.198 unauthorized-sensitive-sharing block when the repo is outside the trust boundary or public (including your own org's public repos).

## Auto mode safety defaults further expanded (v2.1.203/v2.1.205)

Refines and extends the v2.1.200 list:
- **Default-branch push refined (v2.1.203)**: a plain push to the repository's default branch is **not** blocked on its own. It's blocked only when it carries sensitive content (secrets, personal/entrusted data), changes concealed or misdescribed relative to what was asked, content ported in or first read from outside the repo, or routes around a PR/review/check that was requested. Clearing a flagged push requires naming the flagged content or the bypassed review, not just the push itself. Before v2.1.203, *any* direct push to the default branch was blocked outright (see v2.1.183 entry above — now superseded by this refinement). `permissions.deny` rules still apply in every mode regardless and can block default-branch pushes outright if desired.
- **Sensitive local content into outbound artifacts (v2.1.203)**: content from a sensitive local store, or a file whose name/path/type marks it sensitive, is blocked from entering a commit, push, PR/issue body, gist/paste, or package publish unless both the source and the destination are named. Covers session transcripts and conversation logs, credential/config dot-folders (SSH keys, cloud credentials, browser profiles, shell history), and user-data exports. The destination repo being private does not clear this block.
- **Public-repo personal-data block refined (v2.1.203)**: a dotfiles repo's own subject matter is now an exception to the personal/entrusted-data block; content reaching any public surface from a private repo is blocked the same way regardless of destination visibility. Before v2.1.203, personal data was grouped with confidential material and blocked only when not part of that repo's own work.
- **Session transcript tampering (v2.1.205)**: new default block on tampering with the session's own transcript/conversation-log files — closes a self-modification gap adjacent to the v2.1.198 "keystrokes to Claude's own tmux pane" block.

## Auto mode push/secrets scope widened to any branch (v2.1.211)

Both refinements below supersede the v2.1.203 "default branch" scoping in the entry above (doc-gap backfill — missed in the 2026-07-16 run's v2.1.211 pass):
- **Allowed**: pushing to any branch of the repository you're working in now runs without a prompt, not just the default branch — including the default branch itself. A non-default branch whose name marks it as a deploy/publish target (e.g. `production`, `gh-pages`) isn't covered; the classifier still judges those on their own terms, and the push's content is still checked against the other rules. Before v2.1.211, only the branch you started on, branches Claude created, and routine default-branch pushes were allowed by default.
- **Blocked**: a commit or push that would send secrets/sensitive data outside the repo, or widen what a deploy exposes, is now blocked on **any** branch and even in a public repo — not scoped to the default branch anymore. Clearing it requires naming the execution effect (not just the commit/push). Before v2.1.211, this check applied only to the default branch.

## Auto mode classifier trust boundary (v2.1.200)

The classifier trusts your working directory and the remotes configured when the session started. A remote added or repointed mid-session (`git remote add`/`git remote set-url`) is **not** trusted for push-destination checks until you name it explicitly; before v2.1.200, mid-session remotes were trusted like pre-existing ones.

Auto mode on signed-in Claude apps gateway sessions also requires `CLAUDE_CODE_ENABLE_AUTO_MODE=1` (same opt-in as Bedrock/Vertex/Foundry) — it's a separate provider class, not reachable via the Anthropic API opt-in-by-default path.

## MCP tool consent bypass (v2.1.199)

An MCP tool marked with `_meta["anthropic/requiresUserInteraction"]` skips the classifier and always prompts directly in auto mode (no "don't ask again"); denied outright in `dontAsk` mode; still prompts even in `bypassPermissions`. See mcp-and-plugins.md.

## Circuit-breaker hardened against substitution wrapping (v2.1.208)

The `rm -rf /` / `rm -rf ~` circuit-breaker prompt (fires instead of going to the classifier, in both auto mode and `bypassPermissions`) now also fires when the removal is wrapped in command substitution (`$(...)`, backticks) or process substitution (`<(...)`) anywhere in the command, e.g. `echo "$(rm -rf ~)"`. Before v2.1.208, wrapped forms went to the classifier instead of prompting, sidestepping the breaker. (v2.1.208)

## Auto mode no longer overrides hook `ask` decisions (v2.1.211)

Auto mode's classifier no longer silently overrides a `PreToolUse` hook's explicit `permissionDecision: "ask"` for unsandboxed Bash commands — before v2.1.211, the classifier could allow a command outright even when a hook had already decided it needed a prompt, effectively downgrading the hook's decision. The hook `ask` now takes precedence, consistent with `hooks.md`'s "most restrictive decision wins" rule. (v2.1.211)

## Deprecated permission-rule tool names (v2.1.210)

Claude Code now warns at startup if `permissions.allow`/`deny`/`ask` rules reference `Write()`, `NotebookEdit()`, or `Glob()` — these are deprecated rule targets in favor of `Edit()`/`Read()`. Existing rules still work but should be migrated. (v2.1.210)

## Security hardening (v2.1.214)

Bash/PowerShell permission-check bypass fixes: PowerShell 5.1 permission-check bypass closed; Bash checks now fail closed on file-descriptor redirect forms parsed differently by bash vs. the permission analyzer; commands over **10,000 characters** now always prompt instead of silently auto-approving; zsh variable subscripts/modifiers inside `[[ ]]` comparisons (previously treated as inert text) now prompt; certain `help`/`man` invocations that could run unsafe options, command substitutions, or backslash paths no longer auto-approve. Remote-session permission prompts can no longer proceed before the local confirmation dialog answers. `docker`/Podman `docker`-shim commands carrying daemon-redirect flags (`--url`, `--connection`, `--identity`, Podman remote mode) now require a permission prompt (previously ran unprompted).

**Single-segment `dir/**` glob scope fix (v2.1.214)**: an `allow` rule like `Edit(src/**)` previously matched a `src/` directory anywhere in the tree; it now matches only `<cwd>/src/**`. `deny`/`ask` rules are unaffected and keep matching at any depth. Write `**/dir/**` in an allow rule to intentionally match any depth. The same single-segment-vs-any-depth change applies to hook `if:` conditions — see hooks.md.

## Auto mode classifier model & cost (v2.1.210, doc-gap backfill)

The classifier runs on Claude Sonnet 5 by default regardless of your `/model` selection (an Anthropic server-side override takes precedence); falls back to the session's own model when that's Sonnet 4.6 or when `availableModels` excludes Sonnet 5, or to an Opus model when the session runs on Fable 5 (provider's default Opus off the Anthropic API). Resolved once, on the session's first auto-mode request. Auto mode model requirement now also includes **Fable 5** on every provider (Anthropic API/Claude Platform on AWS: Opus 4.6+/Sonnet 4.6+/Fable 5; Bedrock/Vertex/Foundry/Claude apps gateway: Sonnet 5, Opus 4.7, Opus 4.8, Fable 5). (confirmed 2026-07-18)

## Security & auto-mode hardening (v2.1.218-223)

- **Bash/PowerShell bypass fixes**: crafted commands hiding parts of themselves from permission checks (v2.1.223); tab/invisible-Unicode padding hiding command text from the approval dialog (v2.1.223); zsh `[[ ]]` regex conditionals executing hidden commands (v2.1.221); PowerShell paths containing quote characters mishandled (v2.1.221); workflow scripts using dynamic `import()` to escape the workflow sandbox (v2.1.223); an agent definition's `bypassPermissions` mode ignoring the org's bypass-permissions-disable policy (v2.1.223).
- **Auto mode now adjudicates more directly instead of dialog-prompting**: dangerous-`rm`, background-`&`, and suspicious-Windows-path checks go straight to the classifier instead of opening a permission dialog; plan-mode-with-auto no longer prompts for Bash the static analyzer can't prove read-only — the classifier judges it instead. (v2.1.218)
- **Cross-session `SendMessage` evaluated by the classifier** before dispatch, same as other auto-mode-gated actions. (v2.1.222)
- Worktree isolation hardened: worktree-isolated sessions/subagents could previously run destructive git commands against the main checkout; isolation now covers file edits and Bash in every session type. (v2.1.222)

## Security hardening (v2.1.113)

`sandbox.network.deniedDomains` setting blocks specific domains. Bash deny rules match commands wrapped in `env`/`sudo`/`watch`/`ionice`/`setsid`. `Bash(find:*)` no longer auto-approves `find -exec`/`-delete`. macOS `/private/{etc,var,tmp,home}` treated as dangerous.

## Auto mode flags

Auto mode no longer requires opt-in consent as of v2.1.152 — cycling to auto via Shift+Tab activates immediately without a consent prompt.

Auto mode on Bedrock, Vertex, and Foundry: available for Claude Sonnet 5, Opus 4.7, and Opus 4.8 — opt in with `CLAUDE_CODE_ENABLE_AUTO_MODE=1`. Sonnet 5 support added in v2.1.197. (v2.1.158)

**Doc update (v2.1.207)**: the `CLAUDE_CODE_ENABLE_AUTO_MODE=1` opt-in above is superseded — auto mode is now available **by default** on Bedrock/Vertex/Foundry (and signed-in Claude apps gateway sessions), no env var needed. Use the existing `permissions.disableAutoMode: "disable"` managed setting to turn it off org-wide. The env var is still accepted for compatibility but has no effect from v2.1.207 onward. **Confirmed (2026-07-14)**: the live permission-modes page has now caught up and states this directly — the same-day doc lag flagged on 2026-07-11/12/13 is resolved.

`--enable-auto-mode` (adds to Shift+Tab cycle), `--allow-dangerously-skip-permissions` (adds bypassPermissions to cycle without activating it). Administrators can lock auto mode off entirely with `permissions.disableAutoMode: "disable"` in managed settings — overrides `CLAUDE_CODE_ENABLE_AUTO_MODE` and hides auto mode from the cycle for everyone. Auto mode strips blanket shell rules on entry: `Bash(*)`, `PowerShell(*)`, wildcarded interpreters like `Bash(python*)`, package-manager run commands, and `Agent` allow rules. Narrow rules like `Bash(npm test)` carry over. Classifier never sees tool results (prevents injection). `PermissionDenied` hook fires on classifier denials (v2.1.88). `autoMode.environment` setting for trusted repos/buckets. Run `claude auto-mode defaults` to see full classifier rule lists. `claude auto-mode reset` restores the default auto-mode configuration (prompts for confirmation; `--yes` skips it). (v2.1.212)

Conversation-stated boundaries (e.g. "don't push") block classifier; lost after compaction -- use deny rules for hard guarantees.

`autoMode.hard_deny`: prose rules that block unconditionally — user intent and `allow` exceptions cannot override. Use when a boundary must survive regardless of what the user says in conversation. Default includes exfiltration and safety-bypass rules; include `"$defaults"` to extend rather than replace. (v2.1.136)

`autoMode.classifyAllShell`: set `true` to route ALL Bash/PowerShell commands through the classifier, including reads and working-dir edits normally auto-approved in auto mode. More safety overhead, more classifier latency. (v2.1.193)

## Upcoming: auto mode becomes the default

**Starting 2026-08-14**, `auto` becomes the default permission mode for *new* sessions on Pro, Max, and Team plans (announced 2026-08-10, live docs). Existing sessions and any `defaultMode` you already set yourself are unaffected unless you accept a one-time switch prompt; an org-managed default is also unaffected. Enterprise is not mentioned in the rollout. See the blog announcement linked from the live permission-modes page for details. **Confirmed live (2026-08-17)**: rolled out as scheduled — requires Claude Code v2.1.228+ on macOS/Linux/WSL or v2.1.233+ on native Windows (earlier versions still default to Manual); the built-in default stays `default` (not `auto`) when `disableAutoMode:"disable"` is set, feature-flag fetching is off or this is the first session after install/upgrade, in `-p`/Agent SDK sessions, on Bedrock/Vertex/Foundry/Claude Platform on AWS/a signed-in Claude apps gateway session, or on an Enterprise plan/Console API key — confirming Enterprise is excluded. A one-time notice appears the first time the built-in default starts a session in auto mode; if `~/.claude/settings.json` already sets a different `defaultMode`, Claude Code asks once whether to switch to auto and keeps your setting if you decline.

## Cowork tab has its own permission-modes system

Desktop's Cowork tab does **not** use the 6 modes above. It has a separate, independently-enabled permission-modes system with no mode selector shown at all until a mode beyond Cowork's default is enabled for your account — don't assume `defaultMode`/`permissions.defaultMode` settings apply there.

## Checkpointing

Auto-snapshots before every file edit. `/rewind` (alias `/undo`) to restore previous state; as of v2.1.191 also works to jump back to state **before a `/clear`** (not just undo the last turn). `/checkpoint` to save manually. Checkpoints are local to session, separate from git. Only covers file changes -- remote actions (DB, API, deploy) cannot be checkpointed.
