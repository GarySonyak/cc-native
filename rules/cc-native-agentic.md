# Claude Code Native — Agentic Workflow (MUST FOLLOW)

**Always use the Guide-and-Verify workflow** when designing, editing, or generating any Claude Code configuration artifact. Skipping it is a regression in process, not a shortcut.

## Scope resolution

This rule applies whenever the work touches any of:

- `.claude/agents/` — subagent definitions
- `.claude/skills/` — skill definitions
- `.claude/commands/` — slash command definitions
- `.claude/output-styles/` — output style definitions
- `.claude/hooks/` — hook scripts
- `.claude/schedules/` — scheduled task wrappers
- `.claude/rules/` — workflow rules
- `.claude/settings.json`, `.claude/settings.local.json`, `.claude/CLAUDE.md`, `.claude/loop.md`
- `.mcp.json` (any directory)
- Plugin manifests (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`)

If the work does not touch any of those, this rule does not apply — skip silently.

## GUIDE Phase — Before generating code or producing a plan

**Before generating or editing a Claude Code config artifact, AND before producing an implementation plan or design document** you MUST:

1. Invoke the `cc-native:feature-guide` skill (the skill provides progressive-disclosure references at `skills/feature-guide/references/*.md`).
2. Read the **single matching reference file** for the artifact type — not the whole skill. Mapping:
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
3. Plan-phase Guide is non-optional. A plan that proposes a deprecated feature, an incorrect hook event, or a forbidden frontmatter field must be caught before any code is written. If you are entering plan mode or are a sub-agent producing a design, call the Guide tools BEFORE drafting the plan, not after.

**When the work crosses plugin boundaries** (modifying a plugin manifest, adding a marketplace entry, changing version, adding hooks/skills/agents to a plugin) you MUST also:

- Re-read `references/mcp-and-plugins.md` for plugin agent constraints (`permissionMode`/`hooks`/`mcpServers` are forbidden in plugin agent frontmatter).
- Verify version-bump implications: changes only ship to users when `version` in `plugin.json` is bumped.

## VERIFY Phase — After generating code

The `cc-native` plugin runs two automated verifications:

1. **Deterministic lint** (`hooks/cc-native-verify.py`, PostToolUse) — exits 0 pass, 1 warnings, 2 hard fail.
2. **Semantic audit** (`agents/cc-native-auditor.md`, invoked via Stop hook directive) — returns per-file verdicts: `block` / `warn` / `pass`.

You MUST:

1. **Read phase** — re-read the modified files (the verify hook may have already flagged them).
2. **Lint check** — if `cc-native-verify` exited with code 2, fix the errors before continuing. Code 1 warnings should also be addressed unless explicitly out of scope.
3. **Audit check** — when the Stop hook injects an `additionalContext` directive instructing audit, invoke the `cc-native-auditor` subagent via the `Task` tool with the listed file paths. Do not skip this step on the grounds that the lint passed — semantic issues (wrong hook event for the goal, over-broad tools, dangling cross-references) are exactly what the lint cannot catch.
4. **Block on findings** — you are prohibited from declaring done if:
   - any `cc-native-verify` exit-2 errors remain
   - the auditor returned any `block`-severity finding
5. **Fix in code** — based on the rule's rationale (verifier message or auditor finding text), edit the file. Do not silence the warning by changing the lint config.
6. **Re-verify** — after fixes, the next Edit/Write triggers `cc-native-verify` again automatically; for the auditor, re-invoke with the same file list.

## Why this exists

Claude Code feature surface changes weekly. Without these guard rails, agents drift: they author a hook with an event name that was renamed three releases ago, frontmatter that's silently ignored by the plugin loader, or a skill description that never triggers. The lint catches mechanical errors; the auditor catches intent errors; the skill provides the always-current ground truth. This rule forces the loop to close.
