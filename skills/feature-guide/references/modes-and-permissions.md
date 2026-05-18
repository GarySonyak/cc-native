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

Protected files (never auto-approved in most modes): `.gitconfig`, `.gitmodules`, `.bashrc`, `.bash_profile`, `.zshrc`, `.zprofile`, `.profile`, `.ripgreprc`, `.mcp.json`, `.claude.json`. Protected dirs: `.git`, `.vscode`, `.idea`, `.husky`, and `.claude` (except `.claude/commands`, `.claude/agents`, `.claude/skills`, `.claude/worktrees` where Claude routinely creates content). Note: `.claude-plugin` removed from protected dirs. `bypassPermissions` bypasses ALL protected paths as of v2.1.126 (only `rm -rf /` and `rm -rf ~` still prompt). (v2.1.126)

`acceptEdits` auto-approves: `mkdir touch rm rmdir mv cp sed` (and env-var/process-wrapper prefixes) inside working directory.

## Security hardening (v2.1.113)

`sandbox.network.deniedDomains` setting blocks specific domains. Bash deny rules match commands wrapped in `env`/`sudo`/`watch`/`ionice`/`setsid`. `Bash(find:*)` no longer auto-approves `find -exec`/`-delete`. macOS `/private/{etc,var,tmp,home}` treated as dangerous.

## Auto mode flags

`--enable-auto-mode` (adds to Shift+Tab cycle), `--allow-dangerously-skip-permissions` (adds bypassPermissions to cycle without activating it). Auto mode strips blanket shell rules on entry: `Bash(*)`, `PowerShell(*)`, wildcarded interpreters like `Bash(python*)`, package-manager run commands, and `Agent` allow rules. Narrow rules like `Bash(npm test)` carry over. Classifier never sees tool results (prevents injection). `PermissionDenied` hook fires on classifier denials (v2.1.88). `autoMode.environment` setting for trusted repos/buckets. Run `claude auto-mode defaults` to see full classifier rule lists.

Conversation-stated boundaries (e.g. "don't push") block classifier; lost after compaction -- use deny rules for hard guarantees.

`autoMode.hard_deny`: prose rules that block unconditionally — user intent and `allow` exceptions cannot override. Use when a boundary must survive regardless of what the user says in conversation. Default includes exfiltration and safety-bypass rules; include `"$defaults"` to extend rather than replace. (v2.1.136)

## Checkpointing

Auto-snapshots before every file edit. `/rewind` to restore previous state. `/checkpoint` to save manually. Checkpoints are local to session, separate from git. Only covers file changes -- remote actions (DB, API, deploy) cannot be checkpointed.
