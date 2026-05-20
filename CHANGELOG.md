# Changelog

## [0.2.22] — 2026-05-20

- Confirmed v2.1.145. Now sending Telegram notification:

## [0.2.21] — 2026-05-19

- Telegram MCP unavailable — logging fallback per protocol:

## [0.2.20] — 2026-05-18

- Telegram MCP tool unavailable — logging via TELEGRAM-FALLBACK:

## [0.2.19] — 2026-05-17

- The Telegram MCP is not available in this session. Sending TELEGRAM-FALLBACK:

## [0.2.18] — 2026-05-16

- Telegram MCP not in scope. Logging fallback:

## [0.2.17] — 2026-05-15

- TELEGRAM-FALLBACK: docs-monitor 2026-05-15 | Run #32 | v2.1.142 detected

## [0.2.16] — 2026-05-14

- Telegram MCP is not in scope for this session (only WebFetch/Read/Write/Edit/Bash/Grep available; dontAsk blocks direct API calls). Falling back to log output per protocol:

## [0.2.15] — 2026-05-13

- TELEGRAM-FALLBACK: `docs-monitor 2026-05-13 | Run #30 | Pages checked: 15 | Changes: 0 material, 1 trivial | v2.1.140 (May 12) — bug fixes only (subagent_type case/separator matching fix; /goal hang

## [0.2.14] — 2026-05-12

- fix(hooks): add `"shell": "bash"` to SessionStart entry so `${CLAUDE_PLUGIN_ROOT}` expands; v0.2.13 hook registered but never fired in live sessions (no transcript entry, no mtime updates), matching claude-mem's working shape.

## [0.2.13] — 2026-05-12

- feat(hooks): SessionStart refs auto-refresh POC — `refresh-refs.py` pulls 9 feature-guide reference files from GitHub raw on startup; silent on failure, no TTL/atomic-writes/opt-out yet.

## [0.2.12] — 2026-05-12

- Telegram MCP unavailable — logging fallback:

## [0.2.11] — 2026-05-11

- Telegram MCP unavailable. Logging fallback:

## [0.2.10] — 2026-05-10

- Telegram MCP not in scope — logging fallback as required:

## [0.2.9] — 2026-05-09

- Telegram MCP tool is not in scope for this session. Logging TELEGRAM-FALLBACK:

## [0.2.8] — 2026-05-08

- Telegram MCP unavailable. Logging fallback:

## [0.2.7] — 2026-05-07

- **Step 6 log output:**

## [0.2.6] — 2026-05-06

- [2026-05-06] docs-monitor: 2 pages changed — changelog, settings (2 material, 1 trivial)

## [0.2.5] — 2026-05-06

- **fix(auditor)**: fourth severity invariant added to the `cc-native:auditor` system prompt — **citation must directly support the claim**. The existing Citation Requirement (in step 2) said `block`/`warn` findings must quote a specific phrase from the reference, but this only enforced that *some* phrase was quoted, not that the quoted phrase actually backed the claim. Two failure modes observed: a Linux probe audit quoted "Bundle skills + hooks + agents…" (general plugin-description text) to back a finding about marketplace manifest source-key shape, and the Windows v0.2.4 trial cited managed-mode policy text to back a finding that `enabledPlugins` is invalid at project scope. Both phrases sat near the rule the auditor wanted to allege but did not state it. The new invariant adds a self-check: read the cited phrase literally — does it, by itself, state the rule the finding alleges? If only adjacent or contextual, downgrade to `info` or remove. **Empirical motivation**: across all 7 benchmark trials (5 with real test activity), every model that loaded the plugin (Haiku 4.5, Sonnet 4.6, Opus 4.7) followed the advisory cc-native skill-load reminder, so the bottleneck on audit quality is now finding-grounding, not skill-load reliability.
- No code logic or hook changes; `agents/auditor.md` text-only. 16/16 fixture tests pass.

## [0.2.4] — 2026-05-06

- **fix(auditor)**: three small robustness fixes to the `cc-native:auditor` system prompt, all from real-world findings in Windows benchmark trial `005aa327` (Haiku 4.5 main + cc-native v0.2.2). **(a) Tolerate paraphrased `References directory:` line.** The `maybe-audit` Stop hook always emits the literal form `References directory: <abs-path>`, but the main model relays the directive in its own words when calling the auditor — Haiku produced `Reference directory:` (singular) and `Reference directory for spec files:` in trial `005aa327`. Earlier wording matched the literal form only; the auditor coped via inference but the path was fragile. The instruction now accepts singular/plural and tolerates words inserted between `directory` and the colon. **(b) Per-file `Verdict` must equal the maximum finding severity.** Trial audit #1 emitted `[block]` findings inside `Verdict: warn` for an agent file (the summary block correctly counted `Block: 2` but per-file headers labeled both as `warn`). Invariant added: any `block` finding ⇒ `Verdict: block`; any `warn` finding ⇒ `Verdict: warn`; otherwise `pass`. **(c) Self-resolved findings are `info`, not `block`/`warn`.** Trial audit #1 emitted `[block] The frontmatter key allowed-tools (hyphenated) is used here. ... This is correct spelling for skills — no issue with the field name itself.` Severity contradicted the conclusion. Invariant added: if a finding's own text concludes the artifact is correct, severity must be `info`.
- No code logic or hook changes; `agents/auditor.md` text-only. 16/16 fixture tests pass.

## [0.2.3] — 2026-05-06

- **rename(agent)**: `agents/cc-native-auditor.md` → `agents/auditor.md`. Plugin agents are namespaced by the plugin name at invocation time (`cc-native:<agent>`), so the previous filename produced the redundant id `cc-native:cc-native-auditor`. Now invoked as `cc-native:auditor`. The `name:` frontmatter field and the in-file heading were updated to match. The `maybe-audit` Stop-hook directive now references `cc-native:auditor`. The hook's transcript-scan loop guard accepts both old and new shapes (`auditor`, `cc-native:auditor`, `cc-native-auditor`, `cc-native:cc-native-auditor`) so an upgrade mid-session does not break the loop guard for an in-flight transcript. README, SKILL.md, and the three audit fixture transcripts updated; 16/16 fixture tests pass.

## [0.2.2] — 2026-05-06

- **fix(auditor)**: pass the absolute references directory through the `maybe-audit` Stop-hook directive so the `cc-native-auditor` subagent can `Read` reference files directly instead of trying to `Glob` for them from the user's project cwd. Real-world Windows install showed that 6 of 11 audit invocations across three benchmark trials reported "reference unavailable" or silently fell back to training memory — `Glob **/cc-native/**/references/<topic>.md` from a project cwd cannot reach `~/.claude/plugins/cache/...` (it's outside the project tree). The `maybe-audit` hook now reads `CLAUDE_PLUGIN_ROOT` (set by CC for plugin-hook invocations) and injects a `References directory: <abs-path>` line into the directive. The auditor's system prompt is updated to prefer this path when present, fall back to Glob otherwise, and require a `(per references/<topic>.md L<n>: "...")` citation on every schema-level finding — making "audited from the reference" verifiable.
- **tests**: two new `maybe-audit` fixtures cover the with-`CLAUDE_PLUGIN_ROOT` / without-`CLAUDE_PLUGIN_ROOT` directive shapes. 16/16 fixture tests pass.

## [0.2.1] — 2026-05-06

- **fix(hooks)**: quote `${CLAUDE_PLUGIN_ROOT}` expansion in `hooks/hooks.json` so paths with spaces (e.g. `C:\Users\Gary Sonyak\...` on Windows, or any macOS/Linux home dir containing a space) no longer split the script argument. Without quotes, `python ${CLAUDE_PLUGIN_ROOT}/hooks/x.py` became `python C:\Users\Gary Sonyak\...\hooks\x.py`, the shell tokenized on the space, and Python tried to execute `C:\Users\Gary` as a script. Affects all three hooks (PreToolUse, PostToolUse, Stop). Real-world repro from a v0.2.0 install on Windows. Pre-existing bug surfaced now because earlier dogfood was on a Linux/macOS path without spaces.

## [0.2.0] — 2026-05-06

- **fix(README, BREAKING)**: the `@~/.claude/plugins/cc-native/rules/...` install instruction was unworkable — marketplace plugins are cached at `~/.claude/plugins/cache/{marketplace}/{plugin}/{version}/` and CLAUDE.md `@`-imports do not expand `${CLAUDE_PLUGIN_ROOT}`. Workflow rule body folded into `skills/feature-guide/SKILL.md`. The rule auto-applies whenever the skill is loaded — exactly the scope it covered. No user wiring needed. `rules/cc-native-agentic.md` deleted.
- **fix(skill)**: skill description scoped to edit-time only; dropped the Q&A clause that caused unintended triggering on conversations about CC features.
- **chore**: maintainer-side `scripts/maintainer/` (docs-monitor, cron, bumper) extracted to a separate private `cc-native-maintainer` repo. Public install no longer ships `/root/...` paths or Telegram tool references.
- **fix(verify)**: secrets-warning example path genericized (`/root/.secrets/all.env` → `~/.config/secrets.env`).
- **fix(manifest)**: undocumented `category` field removed from `plugin.json`; remains in `marketplace.json` plugin entry where it IS documented.
- **chore**: OSS hygiene files added — `CONTRIBUTING.md`, `SECURITY.md`, `.github/ISSUE_TEMPLATE/{bug,feature}.md`, `.github/PULL_REQUEST_TEMPLATE.md`.

## [0.1.11] — 2026-05-06

- feat(cc-native-verify): scan `permissions.allow[]` Bash patterns for literal credentials at write-time. Two leak shapes detected: env-var prefix (`Bash(KEY=literal_value cmd:*)` where `KEY` matches PASSWORD/APIKEY/SECRET/TOKEN/etc.) and basic auth (`-u user:literal_password`). Findings escalate to error severity (exit 2) so the user sees them on the next settings.json save. False-positive guard: env-var references (`$VAR`), safe values (`true`/`false`/`production`/etc.), and non-credential keys are skipped. Direct response to a real-world audit that found 5+ baked-in secrets in user settings — would have caught all of them at the moment they landed via "Always allow."
- fix(auditor): require fresh `Read` on every audit invocation, even on follow-up audits in the same session. Earlier behavior reused stale reads from prior turns and produced wrong line numbers after edits (false negatives like "Line 29 still contains password X" when X had been deleted and lines shifted). One sentence in the system prompt; no behavior change to passing audits.
- tests: two new fixtures (`settings-secret-env.json`, `settings-secret-basic-auth.json`) cover the literal/$VAR/safe-value distinction. 14/14 fixtures pass.

## [0.1.10] — 2026-05-05

- fix(maybe-audit): move `_debug()` call below the `if not unaudited: sys.exit(0)` guard so `CC_NATIVE_DEBUG=1` only logs blocking fires, not no-op clean stops. Steady-state debugging stays useful (loop diagnoses fire when `unaudited` is populated) without flooding `/tmp/cc-native-debug.log` on every clean Stop.
- docs(references/hooks.md): cross-reference the Stop re-fire gotcha from the main "Structured JSON output" row so a top-down reader doesn't miss it. The "Plugin hook gotchas" section is still the authoritative place for the detail.
- Both fixes are direct addresses of the two `warn` findings cc-native-auditor returned on the v0.1.9 self-audit.

## [0.1.9] — 2026-05-05

- feat(maybe-audit): opt-in debug log. When `CC_NATIVE_DEBUG=1` is set, the Stop hook appends a JSON line per fire to `/tmp/cc-native-debug.log` recording `__file__`, PID, transcript path, and the unaudited list. Lets the user confirm which copy of the hook a running session actually invoked — `${CLAUDE_PLUGIN_ROOT}` is pinned at session start, so a `claude plugin update` does NOT redirect a running session to the new version's hook file. Zero cost when the env var is unset.
- docs(references/hooks.md): new "Plugin hook gotchas" section documenting (a) `${CLAUDE_PLUGIN_ROOT}` session-start pinning, (b) the `Task` vs `Agent` subagent-tool-name split between legacy CC and the SDK / newer harness, (c) Stop-hook re-firing on `decision: "block"` user-relay messages, and (d) `type: "user"` records wrapping `tool_use_result` blocks. All four were root causes of the v0.1.6 → v0.1.8 loop spiral; codifying them in the reference keeps the next person from re-deriving them under fire.

## [0.1.8] — 2026-05-05

- fix(maybe-audit): two compounding loop bugs found and fixed via live dogfood.
  - **Subagent tool name**: hook only matched `name == "Task"`, but the SDK / newer harness records subagent invocations as `name == "Agent"`. Auditor calls were therefore never detected. Now accepts both via `SUBAGENT_TOOLS = {"Task", "Agent"}`.
  - **Loop-guard anchor**: v0.1.6 / v0.1.7 anchored "audit already ran" detection on the most recent real user-message index. That created a self-sustaining loop because every hook block elicits a user relay of the block message — counted as a real user turn, so the auditor always looked stale. Redesigned to anchor on the auditor itself: `_scan_transcript()` now returns only config edits whose transcript index is **after** the most recent auditor invocation. Naturally re-blocks on genuinely new edits and stays silent once an audit has happened.
  - Two new fixtures: `loop-fixed-agent.jsonl` (Agent-tool invocation, must NOT block) and `edit-after-audit.jsonl` (fresh edit after a prior audit, MUST block — verifies the new anchor doesn't over-suppress). Also retained the original Task-tool fixture for backwards compatibility. 12/12 fixtures green.

## [0.1.7] — 2026-05-05

- fix(maybe-audit): the v0.1.6 loop guard was logically correct but counted every `type: "user"` transcript record as a real user-turn boundary. Claude Code wraps tool_use_result blocks in synthetic `user` records, so `last_user_idx` slid forward on every tool call, making `auditor_idx > last_user_idx` always False and re-blocking on every Stop. New `_is_real_user_turn()` predicate excludes records that carry a top-level `toolUseResult` key or whose `message.content` contains a `tool_result` block. Regression covered by `tests/fixtures/transcripts/loop-fixed.jsonl` (auditor invoked, then tool result — must NOT re-block) and `needs-audit.jsonl` (no auditor — must block). Found by user re-hitting the loop after `/reload-plugins` brought v0.1.6 live.

## [0.1.6] — 2026-05-05

- fix(maybe-audit): the Stop hook now detects when the `cc-native-auditor` subagent has already been invoked since the last user message and stays silent on subsequent Stops in the same turn. Before this fix, the hook re-fired indefinitely whenever the user kept the turn open without resolving every flagged block (e.g., test artifacts intentionally left flawed, or findings the user explicitly accepts), because the transcript scan kept rediscovering the same prior edits. Found via dogfood session.
- fix(auditor): hardened the `cc-native-auditor` system prompt. The auditor now MUST `Read` the matching `references/<topic>.md` file before issuing any schema- or feature-shape finding on that artifact. Previously the prompt suggested consulting the reference but didn't enforce it, so the auditor would hallucinate marketplace-manifest schema details (claiming `url` source isn't documented, claiming `owner` isn't a marketplace field, inventing a `monitors` plugin field). Mapping table added so the auditor knows exactly which reference to read for each artifact type.

## [0.1.5] — 2026-05-05

- fix(marketplace): switch plugin `source` from `github` shorthand to explicit `url` form (`https://github.com/GarySonyak/cc-native.git`). Reason: Claude Code's plugin-install path on the `github` source defaults to SSH (`git@github.com:owner/repo.git`) and does not gracefully fall back to HTTPS the way the marketplace-add path does, so HTTPS-only users (no SSH keys configured for github.com) get `Permission denied (publickey)` on install. The `url` source clones over the literal URL string, which forces HTTPS and works for every user regardless of SSH setup.

## [0.1.4] — 2026-05-05

- chore(metadata): tighten manifests to documented schema ahead of marketplace submission. `marketplace.json` now declares a top-level `description` (was missing — flagged by `claude plugin validate`), drops the undocumented `owner.url` field, drops the `version` field on the plugin entry to avoid the silent-override pitfall the docs warn about ("`plugin.json` value always wins"), and mirrors `author`, `homepage`, `repository`, and `license` into the plugin entry so they appear on the marketplace listing card.
- chore(metadata): `plugin.json` drops the undocumented `author.url` field. The author block now matches the documented `{name, email?}` schema.

No behavior change. All hooks, skills, agents, and the audit subagent are unchanged.

## [0.1.3] — 2026-05-05

- chore(metadata): sync `keywords` between `plugin.json` and `marketplace.json` (marketplace was advertising 3, manifest had 7) and add the `audit` keyword to reflect the auditor subagent. Marketplace listings are populated from `marketplace.json`, so this widens discoverability for users searching `skills`, `hooks`, `agents`, `docs`, `linting`, or `audit`.
- chore(metadata): mirror `category: "developer-tools"` from `marketplace.json` into `plugin.json` so both manifests agree.

Pre-submission cleanup ahead of the official Anthropic marketplace form (https://claude.ai/settings/plugins/submit). No behavior change.

## [0.1.2] — 2026-05-05

- fix(windows): `hooks.json` now invokes `python` instead of `python3`. On Windows the `python3` command resolves to the Microsoft Store install stub (which exits non-zero) — every hook was silently failing on Windows installs.
- fix(windows): `cc-native-reminder.py`, `cc-native-verify.py`, and `maybe-audit.py` now normalize incoming `file_path` values (`\` → `/`) so the POSIX-style `CONFIG_PATTERNS` and the `/.claude/<kind>/` literal checks in `_check_artifact_type` match Windows tool inputs.
- fix(windows): `_validate_hook_script` skips the POSIX `S_IXUSR` exec-bit check on `os.name == "nt"` (Windows files don't carry POSIX exec bits — the warning was firing on every hook).
- fix: hook smoke-test in `_validate_hook_script` now uses `sys.executable` instead of hardcoded `python3`, so it runs under whatever interpreter invoked the verify hook.
- improve: hardcoded-user-path portability check expanded — was only flagging `/root/...`, now also catches `/home/<user>/...`, `/Users/<user>/...`, and `C:\Users\<user>\...` (renamed `ROOT_PATH_RE` → `HARDCODED_USER_PATH_RE`).

## [0.1.1] — 2026-05-05

- fix: workflow rule scope had typo `.claube-plugin/` (missed marketplace.json edits).
- fix: `maybe-audit.py` now uses `decision: "block"` instead of undocumented Stop `additionalContext`; also traverses `MultiEdit` `edits[]` array (previously only top-level `file_path`).
- fix: `_check_artifact_type` no longer false-matches `references/*.md` inside installed skills as SKILL.md (was firing "missing frontmatter" errors on edits to skill reference files).
- fix: `cc-native-verify` warns when the live hook-event enum is unloadable, instead of silently passing invalid event names.
- improve: `.claude-plugin/` paths now in `CONFIG_PATTERNS` so plugin-manifest edits trigger the reminder/verify hooks.
- improve: auditor's skill-unavailable fallback now returns `warn` (was `info`) so the main agent sees that the audit was incomplete.

## [0.1.0] — 2026-05-05

- Initial scaffold (private dogfood release).
- `feature-guide` skill (renamed from `cc-native`) with progressive-disclosure references for hooks, skills, agents, MCP, plugins, settings, modes, memory, schedules, and a changelog.
- `cc-native-reminder` PreToolUse hook injects a feature-guide directive on `.claude/` edits.
- `cc-native-verify` PostToolUse deterministic lint with hook event-name validation against the live skill enum.
- `cc-native-auditor` Sonnet subagent for semantic review of changed artifacts.
- `maybe-audit` Stop hook signals the main agent to invoke the auditor.
- `rules/cc-native-agentic.md` Guide-and-Verify workflow rule.
- Maintainer-only `scripts/maintainer/` with docs-monitor agent + cron + bumper for daily reference refresh and auto-PATCH bumps.
- Test fixtures and Makefile (`make test` exercises all three hooks).
