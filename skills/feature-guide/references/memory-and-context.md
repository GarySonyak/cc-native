# Memory & Instructions, Context Management

## Memory & Instructions

4-tier hierarchy (most specific wins): `./CLAUDE.local.md` (local, gitignored) > `./CLAUDE.md` or `./.claude/CLAUDE.md` (project, team-shared) > `~/.claude/CLAUDE.md` (user) > managed policy (`/Library/Application Support/ClaudeCode/CLAUDE.md` macOS, `/etc/claude-code/CLAUDE.md` Linux/WSL, `C:\Program Files\ClaudeCode\CLAUDE.md` Windows — cannot be excluded). Files are concatenated, not overridden; closer-to-cwd loads last. `.claude/rules/*.md`: scoped via `paths:` frontmatter, otherwise always loaded. HTML block comments stripped before injection (saves tokens). `claudeMdExcludes` setting skips files by path/glob (cannot exclude managed policy).

`claudeMd` key in `managed-settings.json`: embed CLAUDE.md content directly in the managed settings file instead of deploying a separate CLAUDE.md. Only honored in managed/policy settings (not project or local). Same precedence as a managed CLAUDE.md file.

`.claude/rules/` entries can be symlinks — link a shared rules directory or individual file into multiple projects (e.g. `ln -s ~/shared-claude-rules .claude/rules/shared`) to keep one canonical copy. Symlinks resolve and load normally; circular symlinks are detected and handled gracefully.

### Auto memory (v2.1.59+)

The main conversation's auto memory is **not** loaded into subagents — the one exception is a fork (`/fork`/`/subtask`, or a `context: fork` skill), which inherits the parent conversation and system prompt and so gets the parent's auto memory too. A subagent's own `memory:` field (if set in its frontmatter) is a separate, independent directory.

Claude writes notes to `~/.claude/projects/<project>/memory/MEMORY.md` automatically. First 200 lines or 25KB loaded at session start. Topic files (e.g. `debugging.md`) not auto-loaded -- Claude reads on demand. Toggle: `autoMemoryEnabled` in settings or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`. Custom location: `autoMemoryDirectory` setting (must be absolute or `~/`-prefixed). `/memory` command to browse and edit. All worktrees in same git repo share one auto memory directory.
- **Correction**: `autoMemoryDirectory` IS read from any settings scope including project `.claude/settings.json`/`.claude/settings.local.json` — the earlier "not accepted from project settings" note was wrong for the current docs. When set at project/local scope it's honored only after accepting the workspace-trust dialog for that folder (same gate as hooks), not blocked outright.
- Memory file frontmatter now includes an ISO `modified` timestamp, written automatically when Claude updates a memory file. (v2.1.214)
- After every `MEMORY.md` write, Claude Code checks the file against the 200-line/25KB read limit: near the limit it reminds Claude to shorten the index; over the limit the write still succeeds but Claude Code returns an error telling Claude to rewrite the index, since content past the limit won't load next session. The check only measures what actually loads — YAML frontmatter and block HTML comments are stripped before measuring (v2.1.211; before that, raw file size was measured and could false-trigger on frontmatter/comments alone). (v2.1.210)

### CLAUDE.md tips

Target under 200 lines; use `@path/to/file` imports; `/init` generates initial file (set `CLAUDE_CODE_NEW_INIT=1` for interactive flow — **correction**: value is `1`, not `true`). `--add-dir` directories don't load CLAUDE.md by default -- set `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` to load `CLAUDE.md`/`.claude/CLAUDE.md`/`.claude/rules/*.md`/`CLAUDE.local.md` from them. AGENTS.md: CC reads CLAUDE.md, import AGENTS.md with `@AGENTS.md` for cross-agent compatibility.

Path-scoped `.claude/rules/*.md` (`paths:` frontmatter) trigger when Claude reads a matching file, including through a symlinked path back to the project directory (e.g. a symlinked checkout). (v2.1.198)

A `paths` glob containing an unreadable `[` bracket expression (e.g. `photos [2024/**`) now matches nothing instead of erroring — escape a literal `[` as `\[` if needed. Before v2.1.207, one invalid pattern made the Read tool fail for every file the rule was evaluated against, not just skip matching. (v2.1.207)

Brace expansion in a rule's `paths` list (e.g. `src/**/*.{ts,tsx}`) shares one budget of 1,000 expanded patterns and 4 MiB across the whole list; a pattern that would exceed the budget is used unexpanded (its literal braces then match no files). Before v2.1.217, a `paths` value with many brace groups could stall or OOM-crash the CLI at startup. (v2.1.217)

Excluding `project` from `--setting-sources` skips rules without `paths` frontmatter (loaded at launch). Before v2.1.211, on-demand rules — path-scoped rules and rules in nested `.claude/rules/` directories — still loaded even with `project` excluded; now they're skipped too. (v2.1.211)

`/doctor` (v2.1.206) proposes trims for a checked-in CLAUDE.md: cuts content Claude can derive from the codebase (directory layouts, dependency lists, architecture overviews), keeps pitfalls/rationale/conventions that differ from tool defaults.

The first time a project-level memory file (CLAUDE.md/CLAUDE.local.md) uses an `@import` that resolves outside the working directory (e.g. `@~/.claude/my-project-instructions.md`), Claude Code shows a one-time approval dialog listing the external files; declining disables those imports for the session without asking again. User-scope files (`~/.claude/CLAUDE.md`, `~/.claude/rules/`) skip the dialog since they're self-authored.

`/import [codex|gemini] [--dry-run] [--yes]`: brings another coding agent's config into Claude Code — appends its instruction files (e.g. `AGENTS.md`) to the matching `CLAUDE.md` and carries over MCP servers, commands, subagents, and skills, one-time. (v2.1.213)

`@path` imports recurse up to 4 hops deep. Import parsing skips Markdown code spans/fenced code blocks — wrap a path in backticks (`` `@README` ``) to mention it without importing it.

`/init` already reads Cursor rules (`.cursor/rules/`/`.cursorrules`) and Copilot rules (`.github/copilot-instructions.md`) by default, folding relevant parts into the generated CLAUDE.md. With `CLAUDE_CODE_NEW_INIT=1` set, it additionally reads `AGENTS.md`, `.devin/rules/`, `.windsurf/rules/`/`.windsurfrules`, and `.clinerules`.

## Context Management

`/compact` to summarize and free context. `/compact <focus>` to preserve specific topics. Deferred tools via `ToolSearch` -- only names loaded initially. `/context` to visualize usage. Skills load description only until invoked. Subagents get own fresh context (main conversation not bloated). `/btw` for side questions (no tools, answer discarded).

Project-root CLAUDE.md survives `/compact` — Claude re-reads it from disk and re-injects it after the summary. Nested CLAUDE.md files (subdirectories) are **not** auto re-injected; they only reload the next time Claude reads a file in that subdirectory. An instruction that "disappears" after compaction was either conversation-only (never written to a file) or lives in a not-yet-reloaded nested CLAUDE.md.
