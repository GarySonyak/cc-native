---
name: cc-native
description: TRIGGER for any question about Claude Code features — hooks, skills, subagents, agent teams, MCP, plugins, permission modes, plan mode, auto mode, scheduled tasks, settings, agentic loop, worktrees, checkpointing, memory, context management. Read the matching file in references/ before answering — do not answer from training memory; CC features change weekly. Also TRIGGER when designing or editing CC config under .claude/ or .mcp.json.
---

# Claude Code Native Architecture

Quick reference for CC's native features. Source: code.claude.com/docs/en/. Updated by docs-monitor agent.
Last updated: 2026-05-05

## Agentic Loop (always-loaded summary)

Three phases: **gather context** (Read/Grep/Glob) → **take action** (Edit/Write/Bash) → **verify results** (run tests, re-read). Phases blend together. Never skip verify. Claude decides what each step requires based on what it learned from the previous step.

## How to use this skill

Read **only the reference file that matches the question** — do not read all of them. Each file is self-contained and stands alone.

| Topic | Reference file |
|-------|----------------|
| Subagents, custom agents, agent teams, worktrees | [references/agents.md](references/agents.md) |
| Skills (frontmatter, progressive disclosure, lifecycle, invocation control) | [references/skills.md](references/skills.md) |
| Hooks (events, types, matchers, exit codes, JSON output) | [references/hooks.md](references/hooks.md) |
| MCP servers, plugins, channels | [references/mcp-and-plugins.md](references/mcp-and-plugins.md) |
| Plan mode, permission modes, auto mode, checkpointing | [references/modes-and-permissions.md](references/modes-and-permissions.md) |
| Memory hierarchy, CLAUDE.md, auto memory, context management | [references/memory-and-context.md](references/memory-and-context.md) |
| Tools reference, scheduled tasks (`CronCreate`, `/schedule`, `/loop`), session management, effort levels | [references/tools-and-scheduling.md](references/tools-and-scheduling.md) |
| Notable settings keys | [references/settings.md](references/settings.md) |
| New commands and recent version notes (v2.1.116 → v2.1.128) | [references/changelog.md](references/changelog.md) |

## Routing tips

- "How does X work in CC?" → look up X in the table, read that one file.
- "What changed in version Y?" → `references/changelog.md`.
- "Which setting controls Z?" → `references/settings.md`, then maybe a topic file.
- "How do I structure a skill?" → `references/skills.md` (covers progressive disclosure).
- Multi-topic questions: read the matching files, do **not** preload others.
