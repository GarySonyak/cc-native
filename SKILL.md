---
name: cc-native
description: Reference for Claude Code native features — agentic loop, plan mode, subagents, skills, hooks, MCP, plugins, permission modes, scheduled tasks, settings. Use when answering questions about how Claude Code itself works or designing CC-native automation (hooks, skills, agents, MCP).
paths:
  - ".claude/**"
  - ".mcp.json"
---

# Claude Code Native Architecture

Quick reference for CC's native features. Source: code.claude.com/docs/en/. Updated by docs-monitor agent.
Last updated: 2026-04-29

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
| New commands and recent version notes (v2.1.116 → v2.1.126) | [references/changelog.md](references/changelog.md) |

## Routing tips

- "How does X work in CC?" → look up X in the table, read that one file.
- "What changed in version Y?" → `references/changelog.md`.
- "Which setting controls Z?" → `references/settings.md`, then maybe a topic file.
- "How do I structure a skill?" → `references/skills.md` (covers progressive disclosure).
- Multi-topic questions: read the matching files, do **not** preload others.
