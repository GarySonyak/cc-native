# Memory & Instructions, Context Management

## Memory & Instructions

4-tier hierarchy (most specific wins): `./CLAUDE.local.md` (local, gitignored) > `./CLAUDE.md` or `./.claude/CLAUDE.md` (project, team-shared) > `~/.claude/CLAUDE.md` (user) > managed policy (`/Library/Application Support/ClaudeCode/CLAUDE.md` macOS, `/etc/claude-code/CLAUDE.md` Linux/WSL, `C:\Program Files\ClaudeCode\CLAUDE.md` Windows — cannot be excluded). Files are concatenated, not overridden; closer-to-cwd loads last. `.claude/rules/*.md`: scoped via `paths:` frontmatter, otherwise always loaded. HTML block comments stripped before injection (saves tokens). `claudeMdExcludes` setting skips files by path/glob (cannot exclude managed policy).

`claudeMd` key in `managed-settings.json`: embed CLAUDE.md content directly in the managed settings file instead of deploying a separate CLAUDE.md. Only honored in managed/policy settings (not project or local). Same precedence as a managed CLAUDE.md file.

### Auto memory (v2.1.59+)

Claude writes notes to `~/.claude/projects/<project>/memory/MEMORY.md` automatically. First 200 lines or 25KB loaded at session start. Topic files (e.g. `debugging.md`) not auto-loaded -- Claude reads on demand. Toggle: `autoMemoryEnabled` in settings or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`. Custom location: `autoMemoryDirectory` setting (must be absolute or `~/`-prefixed). `/memory` command to browse and edit. All worktrees in same git repo share one auto memory directory.
- **Correction**: `autoMemoryDirectory` IS read from any settings scope including project `.claude/settings.json`/`.claude/settings.local.json` — the earlier "not accepted from project settings" note was wrong for the current docs. When set at project/local scope it's honored only after accepting the workspace-trust dialog for that folder (same gate as hooks), not blocked outright.

### CLAUDE.md tips

Target under 200 lines; use `@path/to/file` imports; `/init` generates initial file (set `CLAUDE_CODE_NEW_INIT=1` for interactive flow — **correction**: value is `1`, not `true`). `--add-dir` directories don't load CLAUDE.md by default -- set `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` to load `CLAUDE.md`/`.claude/CLAUDE.md`/`.claude/rules/*.md`/`CLAUDE.local.md` from them. AGENTS.md: CC reads CLAUDE.md, import AGENTS.md with `@AGENTS.md` for cross-agent compatibility.

Path-scoped `.claude/rules/*.md` (`paths:` frontmatter) trigger when Claude reads a matching file, including through a symlinked path back to the project directory (e.g. a symlinked checkout). (v2.1.198)

## Context Management

`/compact` to summarize and free context. `/compact <focus>` to preserve specific topics. Deferred tools via `ToolSearch` -- only names loaded initially. `/context` to visualize usage. Skills load description only until invoked. Subagents get own fresh context (main conversation not bloated). `/btw` for side questions (no tools, answer discarded).

Project-root CLAUDE.md survives `/compact` — Claude re-reads it from disk and re-injects it after the summary. Nested CLAUDE.md files (subdirectories) are **not** auto re-injected; they only reload the next time Claude reads a file in that subdirectory. An instruction that "disappears" after compaction was either conversation-only (never written to a file) or lives in a not-yet-reloaded nested CLAUDE.md.
