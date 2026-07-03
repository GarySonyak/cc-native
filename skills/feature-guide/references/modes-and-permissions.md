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

CLI: `--permission-mode <mode>`. Setting: `permissions.defaultMode`. Scheduled tasks: use explicit `--allowedTools` in wrapper.

## Protected files & dirs

Protected files (never auto-approved in most modes): `.gitconfig`, `.gitmodules`, `.bashrc`, `.bash_profile`, `.zshrc`, `.zprofile`, `.profile`, `.zshenv`, `.zlogin`, `.bash_login`, `.ripgreprc`, `.mcp.json`, `.claude.json`, `~/.config/git/`. (`.zshenv`, `.zlogin`, `.bash_login`, `~/.config/git/` added v2.1.160.) Protected dirs: `.git`, `.vscode`, `.idea`, `.husky`, `.cargo`, and `.claude` (except `.claude/worktrees` where Claude stores its own git worktrees). Note: as of v2.1.162, `.claude/commands`, `.claude/agents`, and `.claude/skills` are now also protected — the prior exceptions were removed. `.claude-plugin` removed from protected dirs. `bypassPermissions` bypasses ALL protected paths as of v2.1.126 (only `rm -rf /` and `rm -rf ~` still prompt). (v2.1.126)

Additional protected dirs (v2.1.160): `.config/git`, `.devcontainer`, `.yarn`, `.mvn`. Additional protected files (v2.1.160 build-tool config expansion): shell dotfiles `.bash_aliases .bash_logout .zlogout .envrc`; package managers `.npmrc .yarnrc .yarnrc.yml .pnp.cjs .pnp.loader.mjs .pnpmfile.cjs bunfig.toml .bunfig.toml`; build tools `.bazelrc .bazelversion .bazeliskrc`; git hook configs `.pre-commit-config.yaml lefthook.yml lefthook.yaml .lefthook.yml .lefthook.yaml`; build wrappers `gradle-wrapper.properties maven-wrapper.properties`; dev containers `.devcontainer.json`; type checkers `pyrightconfig.json`.

`acceptEdits` auto-approves: `mkdir touch rm rmdir mv cp sed` (and env-var/process-wrapper prefixes) inside working directory. (v2.1.160) Now also prompts before writing build-tool config files that grant code execution (e.g., files analogous to `package.json` scripts).

## Deny rule glob tool names (v2.1.166)

`permissions.deny` rules now support glob patterns in the **tool-name position** (the part before the parenthesis). Example: `Web*` denies both `WebFetch` and `WebSearch` in a single rule. Previously, tool names in rules were exact-match only; globs only worked inside the argument specifier (e.g. `Bash(npm *)`). (v2.1.166)

## Tool input parameter matching (v2.1.178)

Permission rules now support matching **tool input parameter values** via `Tool(param:value)` syntax (wildcard-enabled):
- `Agent(model:opus)` — block subagents that use any Opus model
- `Agent(model:claude-3*)` — match all claude-3 variant subagents
- Distinct from the existing `Agent(Explore)` type-name form (which matches subagent type, not model parameter)

Use in `permissions.allow` or `permissions.deny` to gate specific model/parameter combinations without blocking the tool entirely. (v2.1.178)

## Auto mode subagent spawn evaluation (v2.1.178)

Auto mode now evaluates subagent spawns via the classifier **before** the subagent launches (previously only checked actions taken during the subagent's run). Dangerous delegated tasks blocked at spawn time. (v2.1.178)

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

## MCP tool consent bypass (v2.1.199)

An MCP tool marked with `_meta["anthropic/requiresUserInteraction"]` skips the classifier and always prompts directly in auto mode (no "don't ask again"); denied outright in `dontAsk` mode; still prompts even in `bypassPermissions`. See mcp-and-plugins.md.

## Security hardening (v2.1.113)

`sandbox.network.deniedDomains` setting blocks specific domains. Bash deny rules match commands wrapped in `env`/`sudo`/`watch`/`ionice`/`setsid`. `Bash(find:*)` no longer auto-approves `find -exec`/`-delete`. macOS `/private/{etc,var,tmp,home}` treated as dangerous.

## Auto mode flags

Auto mode no longer requires opt-in consent as of v2.1.152 — cycling to auto via Shift+Tab activates immediately without a consent prompt.

Auto mode on Bedrock, Vertex, and Foundry: available for Claude Sonnet 5, Opus 4.7, and Opus 4.8 — opt in with `CLAUDE_CODE_ENABLE_AUTO_MODE=1`. Sonnet 5 support added in v2.1.197. (v2.1.158)

`--enable-auto-mode` (adds to Shift+Tab cycle), `--allow-dangerously-skip-permissions` (adds bypassPermissions to cycle without activating it). Auto mode strips blanket shell rules on entry: `Bash(*)`, `PowerShell(*)`, wildcarded interpreters like `Bash(python*)`, package-manager run commands, and `Agent` allow rules. Narrow rules like `Bash(npm test)` carry over. Classifier never sees tool results (prevents injection). `PermissionDenied` hook fires on classifier denials (v2.1.88). `autoMode.environment` setting for trusted repos/buckets. Run `claude auto-mode defaults` to see full classifier rule lists.

Conversation-stated boundaries (e.g. "don't push") block classifier; lost after compaction -- use deny rules for hard guarantees.

`autoMode.hard_deny`: prose rules that block unconditionally — user intent and `allow` exceptions cannot override. Use when a boundary must survive regardless of what the user says in conversation. Default includes exfiltration and safety-bypass rules; include `"$defaults"` to extend rather than replace. (v2.1.136)

`autoMode.classifyAllShell`: set `true` to route ALL Bash/PowerShell commands through the classifier, including reads and working-dir edits normally auto-approved in auto mode. More safety overhead, more classifier latency. (v2.1.193)

## Checkpointing

Auto-snapshots before every file edit. `/rewind` (alias `/undo`) to restore previous state; as of v2.1.191 also works to jump back to state **before a `/clear`** (not just undo the last turn). `/checkpoint` to save manually. Checkpoints are local to session, separate from git. Only covers file changes -- remote actions (DB, API, deploy) cannot be checkpointed.
