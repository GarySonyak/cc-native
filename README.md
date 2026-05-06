# cc-native

A Claude Code plugin that keeps your agents, hooks, and skills aligned with the *current* Claude Code feature surface. CC ships features weekly — `cc-native` provides a Guide-and-Verify workflow so the configuration you author against today's Claude Code is still correct tomorrow.

## What's in the box

| Component | Type | Purpose |
|---|---|---|
| `feature-guide` | skill | Always-current edit-time reference for `.claude/` and plugin artifacts (hooks, skills, subagents, MCP, settings, plugins, modes, memory, schedules). Progressive-disclosure: skim `SKILL.md`, drill into a single matching `references/*.md`. Carries the Guide-and-Verify workflow rule inline. |
| `cc-native-reminder` | PreToolUse hook | When you Edit/Write any `.claude/` config, injects a reminder to consult the `feature-guide` skill before proceeding. |
| `cc-native-verify` | PostToolUse hook | Deterministic lint of the artifact you just wrote: JSON parse, frontmatter required-key check, hook event-name validation against the live skill enum, tools-token regex, hook script smoke test, portability warnings. Exits 0 / 1 (warn) / 2 (fail). |
| `cc-native-auditor` | subagent | LLM semantic review of changed `.claude/` artifacts: goal-fit, least-privilege, cross-references, deprecation. Returns per-file `block`/`warn`/`pass`. |
| `maybe-audit` | Stop hook | Detects edits to `.claude/` files this turn and tells the main agent to invoke `cc-native-auditor` before declaring done. |

## Requirements

- **Python 3.x on PATH as `python`.** The hooks invoke `python ...` (not `python3`) so they work uniformly on Windows (where `python3` resolves to a Microsoft Store stub) and on macOS/Linux distros that map `python` → Python 3.
  - **Linux**: `apt install python-is-python3` (Debian/Ubuntu) or your distro's equivalent if `python` isn't already on PATH.
  - **macOS**: Homebrew (`brew install python`) or the python.org installer both provide `python`.
  - **Windows**: install Python 3 from python.org (NOT the Microsoft Store) and tick "Add Python to PATH".

## Install

From the official Anthropic plugin marketplace (once approved):

```bash
/plugin install cc-native@claude-plugins-official
```

Or install directly from this repo via the maintainer marketplace:

```bash
/plugin marketplace add GarySonyak/cc-native
/plugin install cc-native@gary-sonyak
```

**No further wiring needed.** The skill auto-triggers on `.claude/` edits and carries the workflow rule inline. The hooks register at startup; the auditor is invoked on demand by the Stop hook directive.

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

`cc-native-auditor` is a Sonnet subagent with `Read, Grep, Glob, Bash(diff:*)` only — read-only tools. It produces verdicts; it never edits your files. If you fork the plugin and add tools to that agent, the workflow rule no longer applies — verify your fork explicitly.

## Local development

```bash
git clone git@github.com:GarySonyak/cc-native.git
cd cc-native
make test                                    # runs hook fixtures
claude --plugin-dir "$(pwd)"                 # start a session with this plugin loaded
```

Test invariants: `make test` exercises the verify hook against 14 fixtures (good + bad pairs for agents and settings, hook-script smoke tests, secret-detection cases for `permissions.allow[]`), the reminder hook against config and non-config paths, and the Stop hook (`maybe-audit`) against varied transcript states.

## Versioning

Semver. PATCH bumps come from the docs-monitor cron when CC docs change; MINOR/MAJOR are reserved for changes to the plugin code itself. Pinned `version` in `plugin.json` means you only receive new content when we bump — pushing commits alone is not enough (this is a Claude Code plugin loader rule).

## License

MIT — see `LICENSE`.
