# cc-native

A Claude Code plugin that keeps your agents, hooks, and skills aligned with the *current* Claude Code feature surface. CC ships features weekly — `cc-native` provides a Guide-and-Verify workflow so the configuration you author against today's Claude Code is still correct tomorrow.

## What's in the box

| Component | Type | Purpose |
|---|---|---|
| `feature-guide` | skill | Always-current edit-time reference for `.claude/` and plugin artifacts (hooks, skills, subagents, MCP, settings, plugins, modes, memory, schedules). Progressive-disclosure: skim `SKILL.md`, drill into a single matching `references/*.md`. Carries the Guide-and-Verify workflow rule inline. |
| `cc-native-reminder` | PreToolUse hook | When you Edit/Write any `.claude/` config, injects a reminder to consult the `feature-guide` skill before proceeding. |
| `cc-native-verify` | PostToolUse hook | Deterministic lint of the artifact you just wrote: JSON parse, frontmatter required-key check, hook event-name validation against the live skill enum, tools-token regex, hook script smoke test, portability warnings. Exits 0 / 1 (warn) / 2 (fail). |
| `auditor` | subagent | LLM semantic review of changed `.claude/` artifacts: goal-fit, least-privilege, cross-references, deprecation. Returns per-file `block`/`warn`/`pass`. Invoked as `cc-native:auditor`. |
| `maybe-audit` | Stop hook | Detects edits to `.claude/` files this turn and tells the main agent to invoke `cc-native:auditor` before declaring done. |

## Requirements

- **Python 3.x on PATH as `python`.** The hooks invoke `python ...` (not `python3`) so they work uniformly on Windows (where `python3` resolves to a Microsoft Store stub) and on macOS/Linux distros that map `python` → Python 3.
  - **Linux**: `apt install python-is-python3` (Debian/Ubuntu) or your distro's equivalent if `python` isn't already on PATH.
  - **macOS**: Homebrew (`brew install python`) or the python.org installer both provide `python`.
  - **Windows**: install Python 3 from python.org (NOT the Microsoft Store) and tick "Add Python to PATH".

## Install

From the official Anthropic plugin marketplace:

```bash
/plugin install cc-native@claude-plugins-official
```

Or install directly from this repo via the maintainer marketplace:

```bash
/plugin marketplace add GarySonyak/cc-native
/plugin install cc-native@gary-sonyak
```

**No further wiring needed.** The skill auto-triggers on `.claude/` edits and carries the workflow rule inline. The hooks register at startup; the auditor is invoked on demand by the Stop hook directive.

## Examples

### Example 1 — Authoring a hook with current syntax (feature-guide skill)

You ask Claude to add a Setup hook to your project. Without cc-native, Claude writes from training memory and may pick the wrong event name, wrong matcher format, or a deprecated field — Claude Code ships features weekly, training memory drifts. With cc-native, the feature-guide skill auto-triggers on the edit, Claude reads `references/hooks.md` first (single file, scoped to the artifact type), and writes the hook against the current schema. No second-guessing, no broken hooks shipped.

### Example 2 — Catching a missing required field at edit time (lint hook)

You edit `.claude/agents/reviewer.md` and forget the `description:` field in the frontmatter. The moment the file is saved, cc-native's PostToolUse lint fires `cc-native-verify.py` and exits with a hard-fail (code 2), printing exactly which required field is missing. Claude sees the error before the turn ends and fixes it without you needing to spot it during review. Catches syntax errors, missing required fields, and dangerous settings (e.g., secrets pasted into env) — purely deterministic, no LLM call.

### Example 3 — Catching semantic mismatches the lint can't see (auditor subagent)

You add a new plugin agent with `permissionMode: bypassPermissions` in the frontmatter. Syntax is valid, required fields are all present, the lint passes. But the Claude Code spec says plugin-shipped agents cannot use `permissionMode` (security restriction). When Claude finishes the turn, cc-native's Stop hook injects a directive to invoke the `cc-native:auditor` subagent. The auditor reads `references/mcp-and-plugins.md`, emits a block finding with the exact citation, and you fix it before the plugin ever ships to a user.

### Example 4 — Building a new plugin from scratch (full Guide-and-Verify loop)

You ask Claude: *"Create a new plugin that runs a formatter on every Edit."* The feature-guide skill loads, Claude reads `references/mcp-and-plugins.md` for the manifest schema and `references/hooks.md` for the hook event names. Claude writes `.claude-plugin/plugin.json`, `hooks/hooks.json`, and the formatter script. The lint hook validates the JSON and required fields. The auditor subagent then reviews the artifacts semantically — confirming the hook event is appropriate for the goal, the matcher pattern targets the right tools, and `${CLAUDE_PLUGIN_ROOT}` is used correctly for the script path. You get a plugin that's correct on the first try, not one that fails review three days later.

### Example 5 — Refreshing an existing config after a Claude Code release

A new Claude Code version ships a setting like `skillOverrides` (real example from v2.1.129). You ask Claude to add it to your project. The feature-guide skill — kept current by a daily docs-monitor and refreshed at every session start — already knows about the new setting. Claude reads `references/settings.md`, sees the field's valid values (`off` / `user-invocable-only` / `name-only`), writes the setting correctly the first time, and the auditor confirms the value is one of the documented options. No *"this field doesn't exist yet"* or *"let me try a few syntaxes"* cycles.

## Who benefits

Plugin authors building agents, hooks, or skills that need to stay correct as Claude Code's feature surface evolves. Agent-team maintainers who want a single guard rail catching deprecated frontmatter, wrong hook events, and over-broad tool grants before they ship. Anyone editing `.claude/` artifacts often enough that drift between training-memory CC and live CC has burned them at least once.

## How freshness works

`cc-native` ships with **bundled, frozen** doc references inside `skills/feature-guide/references/`. The reference files are refreshed by a separate maintainer-side cron repo that diffs the live `code.claude.com` pages daily. Material changes trigger an auto-bump of the PATCH version and a push to GitHub.

End users get freshness through Claude Code's built-in plugin auto-update — when the marketplace version bumps, CC notifies you to run `/reload-plugins`. Zero per-user infrastructure, zero network calls per skill consultation, works offline.

> Note: auto-update is on by default for the official Anthropic marketplace. For third-party marketplaces (including the dogfood install path above), enable auto-update via `/plugin → Marketplaces → Enable auto-update`, or run `/plugin update cc-native@gary-sonyak` manually.

## Trade-offs

- **The verify hook is strict.** A red exit on first install usually means an existing artifact in your `.claude/` is out of date with current CC features (e.g. an agent using `permissionMode` inside a plugin). That's the point — the hook is doing its job.
- **The auditor uses Sonnet.** Each audit costs a small number of tokens. The Stop hook only fires the directive when the turn actually edited a `.claude/` file, so the cost is bounded by how often you edit config.
- **The skill triggers on edit-time only by design;** for Q&A invoke it explicitly with `@feature-guide`.

## Security note about the auditor

`cc-native:auditor` is a Sonnet subagent with `Read, Grep, Glob, Bash(diff:*)` only — read-only tools. It produces verdicts; it never edits your files. If you fork the plugin and add tools to that agent, the workflow rule no longer applies — verify your fork explicitly.

## Local development

```bash
git clone git@github.com:GarySonyak/cc-native.git
cd cc-native
make test                                    # runs hook fixtures
claude --plugin-dir "$(pwd)"                 # start a session with this plugin loaded
```

Test invariants: `make test` exercises the verify hook against 16 fixtures (good + bad pairs for agents and settings, hook-script smoke tests, secret-detection cases for `permissions.allow[]`), the reminder hook against config and non-config paths, and the Stop hook (`maybe-audit`) against varied transcript states including the v0.2.2 references-path injection.

## Versioning

Semver. PATCH bumps come from the docs-monitor cron when CC docs change; MINOR/MAJOR are reserved for changes to the plugin code itself. Pinned `version` in `plugin.json` means you only receive new content when we bump — pushing commits alone is not enough (this is a Claude Code plugin loader rule).

## License

MIT — see `LICENSE`.
