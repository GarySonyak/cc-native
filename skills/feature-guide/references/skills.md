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

Key fields: `name`, `description` (recommended, cap 250 chars), `when_to_use` (extra trigger context, appended to description), `argument-hint`, `arguments` (named positional args for `$name` substitution; space-separated or YAML list), `disable-model-invocation` (true = user-only), `user-invocable` (false = Claude-only), `allowed-tools`, `model`, `effort`, `context` (fork = run in subagent), `agent` (which subagent for context:fork), `hooks`, `paths` (glob patterns for auto-activation), `shell` (bash or powershell).

`description` + `when_to_use` combined are capped at **1536 chars** in the skill listing — put the key use case first.

## Invocation

Invoked via `/skill-name` or auto-loaded when relevant. Dynamic context: `!\`command\`` runs shell before prompt (multi-line via fenced ` ```! ` block). String substitutions: `$ARGUMENTS`, `$ARGUMENTS[N]`, `$N`, `${CLAUDE_SESSION_ID}`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_EFFORT}` (current effort level: low/medium/high/xhigh/max; adapt skill instructions to active effort). (v2.1.120)

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

## Other

- Bundled: `/batch`, `/debug`, `/loop`, `/code-review` (renamed from `/simplify` in v2.1.147; optional effort-level arg; `/simplify` alias retained temporarily). New in v2.1.145: `/run` (launch app to verify a change), `/verify` (confirm code change without tests), `/run-skill-generator` (record build/launch recipe so `/run`+`/verify` can follow it; run once per project).
- `/claude-api [migrate|managed-agents-onboard]`: Load Claude API reference for Python/TypeScript/Java/Go/Ruby/C#/PHP/cURL + Managed Agents. **Auto-activates** when code imports `anthropic` or `@anthropic-ai/sdk`. `migrate` upgrades model IDs/thinking config in existing code to a target model; `managed-agents-onboard` walks through creating a new Managed Agent from scratch.
- Description budget: `skillListingBudgetFraction` setting (e.g. `0.02` = 2% of context) or `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var (fixed char count). Per-skill cap: `maxSkillDescriptionChars` setting (default 1536 chars). Run `/doctor` to see if budget is overflowing and which skills are affected.
- Skills from `--add-dir` directories are auto-loaded with live change detection.
- `disableSkillShellExecution: true` in settings disables `` !`command` `` (managed policy). (v2.1.91)
- Live change detection: edits take effect within current session for `~/.claude/skills/`, project `.claude/skills/`, and `--add-dir` skills. New top-level dirs require restart.
- Auto-discovery from nested `.claude/skills/` directories (monorepo support).

## Restrict Claude's skill access

- Disable all: deny `Skill` tool in `/permissions`.
- Per-skill: `Skill(name)` for exact match, `Skill(name *)` for prefix match.
- Hide from Claude entirely: `disable-model-invocation: true`.
