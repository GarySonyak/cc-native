# Memory & Instructions, Context Management

## Memory & Instructions

Hierarchy: `~/.claude/CLAUDE.md` (global) > `project/CLAUDE.md` (project) > `.claude/rules/*.md` (scoped or always-loaded). Rules with `paths:` frontmatter are scoped to those files; without `paths:` = always loaded. HTML block comments stripped before injection (saves tokens). `claudeMdExcludes` setting to skip CLAUDE.md files by path/glob.

### Auto memory (v2.1.59+)

Claude writes notes to `~/.claude/projects/<project>/memory/MEMORY.md` automatically. First 200 lines or 25KB loaded at session start. Topic files (e.g. `debugging.md`) not auto-loaded -- Claude reads on demand. Toggle: `autoMemoryEnabled` in settings or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`. Custom location: `autoMemoryDirectory` setting (not accepted from project settings.json -- security: prevents shared project redirecting writes). `/memory` command to browse and edit. All worktrees in same git repo share one auto memory directory.

### CLAUDE.md tips

Target under 200 lines; use `@path/to/file` imports; `/init` generates initial file (set `CLAUDE_CODE_NEW_INIT=true` for interactive flow). AGENTS.md: CC reads CLAUDE.md, import AGENTS.md with `@AGENTS.md` for cross-agent compatibility.

## Context Management

`/compact` to summarize and free context. `/compact <focus>` to preserve specific topics. Deferred tools via `ToolSearch` -- only names loaded initially. `/context` to visualize usage. Skills load description only until invoked. Subagents get own fresh context (main conversation not bloated). `/btw` for side questions (no tools, answer discarded).
