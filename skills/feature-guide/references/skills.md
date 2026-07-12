# Skills

File: `skills/<name>/SKILL.md` (project) or `~/.claude/skills/<name>/SKILL.md` (personal). YAML frontmatter + markdown instructions. Optional `references/` subdirectory for supporting docs.

## Progressive Disclosure (best practice)

Skill body is injected as **one message** when invoked and stays for the rest of the session. Bigger `SKILL.md` = bigger persistent context cost. Tip: keep `SKILL.md` **under 500 lines**. Move detailed reference material into separate files under the skill directory and link them from `SKILL.md`. Claude reads those files only when needed.

```
my-skill/
├── SKILL.md           # Main instructions + index (required, kept short)
├── reference.md       # Detailed docs (loaded on demand via Read)
├── examples.md        # Examples (loaded on demand)
└── scripts/
    └── helper.py      # Executed, not loaded into context
```

Reference supporting files from `SKILL.md` so Claude knows what each contains and when to read it:

```markdown
## Additional resources
- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)
```

## Frontmatter

Key fields: `name`, `description` (recommended, cap 250 chars), `when_to_use` (extra trigger context, appended to description), `argument-hint`, `arguments` (named positional args for `$name` substitution; space-separated or YAML list), `disable-model-invocation` (true = user-only), `user-invocable` (false = Claude-only), `allowed-tools`, `disallowed-tools` (remove tools from model while skill is active; v2.1.152), `model`, `effort`, `context` (fork = run in subagent), `agent` (which subagent for context:fork), `hooks`, `paths` (glob patterns for auto-activation), `shell` (bash or powershell).

`description` + `when_to_use` combined are capped at **1536 chars** in the skill listing — put the key use case first.

## Invocation

Invoked via `/skill-name` or auto-loaded when relevant. Dynamic context: `!\`command\`` runs shell before prompt (multi-line via fenced ` ```! ` block). String substitutions: `$ARGUMENTS`, `$ARGUMENTS[N]`, `$N`, `${CLAUDE_SESSION_ID}`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_EFFORT}` (current effort level: low/medium/high/xhigh/max; `ultracode` is not a distinct level — reports as `xhigh`; adapt skill instructions to active effort). (v2.1.120) `${CLAUDE_PROJECT_DIR}` — project root; resolves the same in skill body and `allowed-tools` (e.g. `Bash(${CLAUDE_PROJECT_DIR}/scripts/lint.sh *)`). (v2.1.196) Use `\$` before a digit to emit a literal `$` (e.g., `\$1` → `$1` in output; prevents argument substitution). (v2.1.163)

Stacking multiple skill invocations in one message (e.g. `/skill-a /skill-b do XYZ`) loads every named skill (up to 6) and passes the trailing text to each as arguments. (v2.1.199)

Indexed args use shell-style quoting — wrap multi-word values in quotes.

## Invocation control

| Frontmatter | You invoke | Claude invokes | Loaded into context |
|---|---|---|---|
| (default) | Yes | Yes | Description always; full body on invoke |
| `disable-model-invocation: true` | Yes | No | Description **not** loaded; full body only on user invoke |
| `user-invocable: false` | No | Yes | Description always; full body on invoke |

## Lifecycle

Once invoked, `SKILL.md` content stays in conversation. Claude does **not** re-read it on later turns — write standing instructions, not one-off steps. Auto-compaction re-attaches the most recent invocation of each skill, keeping first 5000 tokens; combined budget across re-attached skills is 25000 tokens, filled most-recent-first.

If skill stops influencing behavior, the content is usually still present — strengthen description or use hooks to enforce. Re-invoke after compaction to restore full content.

Re-invoking a skill whose rendered content is identical to the copy already in context now adds a short "already loaded" note instead of a duplicate copy; before v2.1.202, every re-invocation appended the full content again even when nothing had changed (e.g. same arguments, no new dynamic-context output). (v2.1.202)

## Other

- Bundled: `/batch`, `/debug`, `/loop`, `/code-review [--fix] [--comment] [ultra]` (renamed from `/simplify` in v2.1.147; `--fix` applies findings to working tree, `--comment` posts findings as inline GitHub PR comments, `ultra` runs cloud multi-agent review; v2.1.152; optional effort-level arg). New in v2.1.145: `/run` (launch app to verify a change), `/verify` (confirm code change without tests), `/run-skill-generator` (record build/launch recipe so `/run`+`/verify` can follow it; run once per project).
- **Doc correction (v2.1.154)**: `/simplify` is no longer just an alias for `/code-review --fix` — it's now its own skill running 4 parallel review agents (reuse, simplification, efficiency, abstraction-level) that apply fixes without hunting for correctness bugs. Use `/code-review` to find bugs; `/simplify` for cleanup-only.
- `/reload-skills` -- re-scan all skill directories without restarting (v2.1.152). For plugins use `/reload-plugins`.
- `/claude-api [migrate|managed-agents-onboard]`: Load Claude API reference for Python/TypeScript/Java/Go/Ruby/C#/PHP/cURL + Managed Agents. **Auto-activates** when code imports `anthropic` or `@anthropic-ai/sdk`. `migrate` upgrades model IDs/thinking config in existing code to a target model; `managed-agents-onboard` walks through creating a new Managed Agent from scratch.
- Description budget: `skillListingBudgetFraction` setting (e.g. `0.02` = 2% of context) or `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var (fixed char count). Per-skill cap: `maxSkillDescriptionChars` setting (default 1536 chars). Run `/doctor` to see if budget is overflowing and which skills are affected.
- **Naming confirmed (2026-07-11)**: repeated live fetches of this page consistently name the per-skill cap setting `skillListingMaxDescChars`, not `maxSkillDescriptionChars` — the latter has never appeared in a live fetch. Treat `skillListingMaxDescChars` as the authoritative name.
- Skills from `--add-dir` directories are auto-loaded with live change detection.
- `disableSkillShellExecution: true` in settings disables `` !`command` `` (managed policy). (v2.1.91)
- `disableBundledSkills: true` in settings hides all bundled skills and built-in commands from the model (no auto-invoke, no listing); manual `/skill-name` invocations still work. (v2.1.169) **Exception (v2.1.205)**: `/doctor` stays typable even when this is set (it became a bundled skill, not a built-in command, in v2.1.205). Hide it too with `DISABLE_DOCTOR_COMMAND` env var or `skillOverrides: {"doctor": "off"}`.
- Live change detection: edits take effect within current session for `~/.claude/skills/`, project `.claude/skills/`, and `--add-dir` skills. New top-level dirs require restart.
- Auto-discovery from nested `.claude/skills/` directories (monorepo support). (v2.1.178) Nested skills load **contextually** — a skill in `<dir>/.claude/skills/<name>/` only loads when Claude accesses files in `<dir>/`. Name clashes with parent-level skills are resolved as `<dir>:<name>` (e.g., `src:deploy` for a skill in `src/.claude/skills/deploy/`).
- **Refinement (v2.1.203)**: both stay available on a name clash — invoking the unqualified name loads the project-root skill, and Claude Code appends the list of directory-qualified variants with an instruction to also invoke any variant whose directory holds the files being worked on. So `/deploy` alone can still trigger the nested `apps/web:deploy` variant when relevant; type the qualified name directly to run only that one.
- `skillOverrides: "off"` also hides a skill from Remote Control and Agent SDK command listings, not just the terminal `/` menu. Invoking it by full name still errors instead of running. (v2.1.199)
- A skill entry (enterprise/personal/project) can be a symlink to a directory elsewhere on disk — Claude Code follows it and reads `SKILL.md` from the target, loading the skill once even if reachable from multiple locations.

## Restrict Claude's skill access

- Disable all: deny `Skill` tool in `/permissions`.
- Per-skill: `Skill(name)` for exact match, `Skill(name *)` for prefix match.
- Hide from Claude entirely: `disable-model-invocation: true`.
