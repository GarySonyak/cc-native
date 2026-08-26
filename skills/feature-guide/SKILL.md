---
name: feature-guide
description: TRIGGER when designing, editing, or generating any Claude Code config under .claude/ or .mcp.json (agents, skills, hooks, settings, commands, output-styles, schedules, rules, loop.md) or plugin manifests under .claude-plugin/. Read the matching file in references/ before editing — do not work from training memory; CC features change weekly.
---

# Claude Code Native Architecture

Quick reference for CC's native features. Source: code.claude.com/docs/en/. Updated by docs-monitor agent.
Last updated: 2026-08-26

## Workflow rule (always-on while this skill is loaded)

**Always use the Guide-and-Verify workflow** when designing, editing, or generating any Claude Code configuration artifact. Skipping it is a regression in process, not a shortcut.

### GUIDE Phase — Before generating code or producing a plan

**Before generating or editing a Claude Code config artifact, AND before producing an implementation plan or design document** you MUST:

1. Read the **single matching reference file** for the artifact type from the table below — not the whole skill. Mapping:
   - `agents/` → `references/agents.md`
   - `skills/` → `references/skills.md`
   - `hooks/`, `settings.json` (hooks block) → `references/hooks.md`
   - `commands/` → `references/tools-and-scheduling.md`
   - `output-styles/` → `references/skills.md` (output style section)
   - `schedules/` → `references/tools-and-scheduling.md`
   - `.mcp.json`, plugin manifests → `references/mcp-and-plugins.md`
   - permission modes (auto, plan, acceptEdits, bypassPermissions) → `references/modes-and-permissions.md`
   - memory, context, transcripts → `references/memory-and-context.md`
   - any field newly available or recently changed → `references/changelog.md`
2. Plan-phase Guide is non-optional. A plan that proposes a deprecated feature, an incorrect hook event, or a forbidden frontmatter field must be caught before any code is written. If you are entering plan mode or are a sub-agent producing a design, read the matching reference BEFORE drafting the plan, not after.

**When the work crosses plugin boundaries** (modifying a plugin manifest, adding a marketplace entry, changing version, adding hooks/skills/agents to a plugin) you MUST also:

- Re-read `references/mcp-and-plugins.md` for plugin agent constraints (`permissionMode`/`hooks`/`mcpServers` are forbidden in plugin agent frontmatter).
- Verify version-bump implications: changes only ship to users when `version` in `plugin.json` is bumped.

### VERIFY Phase — After generating code

The `cc-native` plugin runs two automated verifications:

1. **Deterministic lint** (`hooks/cc-native-verify.py`, PostToolUse) — exits 0 pass, 1 warnings, 2 hard fail.
2. **Semantic audit** (`agents/auditor.md`, invoked via Stop hook directive as `cc-native:auditor`) — returns per-file verdicts: `block` / `warn` / `pass`.

You MUST:

1. **Read phase** — re-read the modified files (the verify hook may have already flagged them).
2. **Lint check** — if `cc-native-verify` exited with code 2, fix the errors before continuing. Code 1 warnings should also be addressed unless explicitly out of scope.
3. **Audit check** — when the Stop hook injects an `additionalContext` directive instructing audit, invoke the `cc-native:auditor` subagent via the `Task` tool with the listed file paths. Do not skip this step on the grounds that the lint passed — semantic issues (wrong hook event for the goal, over-broad tools, dangling cross-references) are exactly what the lint cannot catch.
4. **Block on findings** — you are prohibited from declaring done if:
   - any `cc-native-verify` exit-2 errors remain
   - the `cc-native:auditor` returned any `block`-severity finding
5. **Fix in code** — based on the rule's rationale (verifier message or auditor finding text), edit the file. Do not silence the warning by changing the lint config.
6. **Re-verify** — after fixes, the next Edit/Write triggers `cc-native-verify` again automatically; for the auditor, re-invoke with the same file list.

### Why this exists

Claude Code feature surface changes weekly. Without these guard rails, agents drift: they author a hook with an event name that was renamed three releases ago, frontmatter that's silently ignored by the plugin loader, or a skill description that never triggers. The lint catches mechanical errors; the auditor catches intent errors; this skill provides the always-current ground truth. This rule forces the loop to close.

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
| New commands and recent version notes (v2.1.116 → v2.1.246) | [references/changelog.md](references/changelog.md) |

## Routing tips

- "How does X work in CC?" → look up X in the table, read that one file.
- "What changed in version Y?" → `references/changelog.md`.
- "Which setting controls Z?" → `references/settings.md`, then maybe a topic file.
- "How do I structure a skill?" → `references/skills.md` (covers progressive disclosure).
- Multi-topic questions: read the matching files, do **not** preload others.
