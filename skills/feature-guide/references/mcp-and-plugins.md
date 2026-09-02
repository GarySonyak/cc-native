# MCP, Plugins, Channels

## MCP

Servers in `.mcp.json` (project) or `~/.claude/.mcp.json` (global). Tools appear as `mcp__<server>__<tool>`. Use `ToolSearch` to discover deferred tools (only names loaded initially -- saves context). Scoping: local > project > user. Check per-server context cost with `/mcp`. MCP OAuth RFC 9728 supported (v2.1.85+). MCP prompts appear as commands: `/mcp__<server>__<prompt>`. In `.mcp.json`/`~/.claude.json`/`claude mcp add-json` configs, `type: "streamable-http"` is accepted as alias for `type: "http"` (MCP spec name). (v2.1.153)

**MCP client runtimes (v1/v2, previously undocumented)**: Claude Code v2.1.232+ defaults to a v2 runtime (MCP TypeScript SDK 2.0, adds protocol revision 2026-07-28), picked once at startup and kept for the session; it falls back to v1 on Bedrock/Claude Platform on AWS/Google Cloud's Agent Platform/Microsoft Foundry (unless a host sets `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST`), when signed in through a Claude apps gateway, or with feature-flag fetching off. On v2, Claude Code asks each server whether it supports the newer revision and uses it with those that do; `list_changed` notifications for those servers arrive over a held-open stream instead of polling (reopens up to 3x within 10s, then backs off up to ~6hrs); a channel server on the newer revision can't carry channel messages so it isn't registered as a channel; an MCP OAuth sign-in whose response names an unexpected issuer now fails. Override with `MCP_SDK_GENERATION=v1|v2` and `MCP_PROTOCOL_NEGOTIATION=auto|legacy`.

`alwaysLoad: true` in server config: always loads all server tools at session start, bypassing tool search. Per-tool: `_meta: {"anthropic/alwaysLoad": true}`. Use sparingly — each eager tool consumes context. (v2.1.121)

`headersHelper`: shell command/script path in server config that generates dynamic request headers at connection time. Outputs JSON key-value pairs to stdout; env vars `CLAUDE_CODE_MCP_SERVER_NAME`/`CLAUDE_CODE_MCP_SERVER_URL` available. Overrides static `headers`; re-runs on reconnect. Use for non-OAuth auth (Kerberos, short-lived tokens, SSO).

`oauth.scopes`: space-separated string pinning scopes requested during OAuth flow to a security-approved subset. Overrides server-advertised scopes (takes precedence over `authServerMetadataUrl`). Leave unset to let server determine scopes.

`authServerMetadataUrl` (in `oauth` block): override OAuth discovery — bypass default RFC 9728/RFC 8414 chain and point to specific authorization server metadata URL. Requires `https://`. (v2.1.64+)

`--callback-port` fixes the local OAuth callback port (default: random) to match a pre-registered `http://localhost:PORT/callback` redirect URI some servers require. v2.1.229 regressed this to send `http://127.0.0.1:PORT/callback` instead, breaking sign-in for servers that exact-match the registered URI (e.g. Slack); fixed in v2.1.231, which restored the `localhost` form. (v2.1.231)

`claude mcp login <name>` / `claude mcp logout <name>`: authenticate or deauthenticate with a specific MCP server from the CLI, without opening the `/mcp` menu. `--no-browser` flag redirects auth flow to stdin — required in SSH/headless sessions. `claude mcp get`/`claude mcp remove` now suggest typo corrections and truncate long server lists. (v2.1.186)

Managed MCP policy: `allowedMcpServers`/`deniedMcpServers` in managed settings restrict users to approved servers. Match by `serverName`, `serverCommand` (exact array), or `serverUrl` (wildcard `*`). Allowlist behavior: undefined=no restriction, `[]`=full lockdown, list=whitelist. Denylist takes absolute precedence over allowlist. Option 1 (`managed-mcp.json`)=exclusive control over all servers; Option 2 (allowlists/denylists)=policy overlay allowing user-added servers within constraints. Both can coexist. (v2.1.128)

`MCP_TOOL_TIMEOUT` env var: raises per-request fetch timeout for remote MCP servers (was previously capped at 60s regardless of this setting). Set to timeout in ms. (v2.1.142)

`type: "ws"` in server config: WebSocket transport — persistent bidirectional connection for servers that push events unprompted. Configure via `claude mcp add-json`. Does NOT support `--transport` flag or OAuth. Accepts url, headers, headersHelper, timeout, alwaysLoad fields.

`list_changed` notification support: MCP servers can send `list_changed` notifications to dynamically refresh their available tools, prompts, and resources mid-session — Claude Code auto-refreshes capabilities on receipt, no disconnect/reconnect needed. If the refresh request itself fails, Claude Code keeps the server's previously discovered tools/prompts/resources until a later refresh succeeds; before v2.1.214, a failed refresh replaced them with an empty list.

`_meta["anthropic/requiresUserInteraction"]: true` on a tool's `tools/list` entry (server-side): forces a permission prompt on every call to that tool, even in `acceptEdits`/`auto`/`bypassPermissions`, with no "don't ask again" option; `dontAsk` mode denies the call instead of prompting. Use for consent/access-grant tools where auto-approval would defeat the point. (v2.1.199)

`claude mcp list`/`claude mcp get`: as of v2.1.196, project-scoped `.mcp.json` server approvals are read only from settings files not checked into the repo, until the workspace-trust dialog is accepted — a freshly cloned repo can't self-approve its own servers via a committed `enableAllProjectMcpServers`/`enabledMcpjsonServers`.

`CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`: a tool call to a remote HTTP/SSE/WebSocket/claude.ai-connector server that sends no response or progress notification for 5 minutes now aborts instead of waiting for the full wall-clock timeout. Set in ms; `0` disables the check. Stdio servers aren't subject to it. (v2.1.187)
**Update (v2.1.203)**: stdio servers are now also subject to the idle timeout (30-minute default window, vs 5 minutes for HTTP/SSE/WebSocket/connector servers) — supersedes the "stdio servers aren't subject to it" note above. A per-server `timeout` (in `.mcp.json`) of ≥1000ms also floors the idle window so it never fires sooner than that value.

Reserved MCP server names (rejected for user-configured servers): `workspace`, `claude-in-chrome`, `computer-use`, `Claude Preview`, `Claude Browser` (the last reserved as of v2.1.205 ahead of a Desktop pane rename — previously available to user servers).

Plugin-provided MCP tools use the full name `mcp__plugin_<plugin-name>_<server-name>__<tool-name>` (any character outside `A-Z a-z 0-9 _ -` sanitized to `_`) — use this exact form in permission rules, a skill's `allowed-tools`, or a subagent's `tools` field, not the shorter `mcp__<server>__<tool>` form used for user-configured servers.

`${CLAUDE_PLUGIN_DATA}`: a plugin's persistent data directory, distinct from `${CLAUDE_PLUGIN_ROOT}` (the versioned install path) — state written here survives plugin updates. Available in plugin `.mcp.json`/`plugin.json` server configs and hooks.

MCP `roots/list` request now also returns the session's additional working directories (`--add-dir`), not just the directory Claude Code was launched from; Claude Code sends `notifications/roots/list_changed` when that set changes. (v2.1.203)

Stdio servers receive `CLAUDE_PROJECT_DIR` (project root) in their spawned process env — same value hooks get — so a server can resolve project-relative paths without depending on cwd. In `.mcp.json` `command`/`args`, reference it as `${CLAUDE_PROJECT_DIR:-.}` (needs a default since the var isn't set in CC's own env); plugin-provided configs can use `${CLAUDE_PROJECT_DIR}` directly.

`ENABLE_TOOL_SEARCH` env var controls MCP tool deferral: unset (default — all tools deferred; falls back to upfront-load on Google Cloud's Agent Platform or a non-first-party `ANTHROPIC_BASE_URL` proxy), `true` (force deferred everywhere, requires `tool_reference`-capable model — not Haiku), `auto`/`auto:N` (threshold mode — load upfront if schemas fit within N% of context window, default 10%), `false` (all tools loaded upfront). Also settable via `settings.json` `env`.

MCP resources are referenced with `@server:protocol://resource/path` (e.g. `@github:issue://123`), same as file @-mentions; fuzzy-searchable in the @ autocomplete alongside files.

An untracked `.claude/settings.local.json`'s `.mcp.json` server approvals now apply only after you accept the workspace-trust dialog for that folder or a parent directory (your own config home — `~/` or `CLAUDE_CONFIG_DIR` — is exempt from this gate). Before v2.1.207, an untracked `settings.local.json` approved servers even in a folder you'd never trusted. Approvals from `~/.claude/settings.json`, managed settings, and `--settings` always apply regardless of trust state. (v2.1.207)

A plugin-provided `headersHelper` can no longer reference the plugin's `${user_config.*}` values — the command runs through a shell, so Claude Code reports the server as misconfigured instead of substituting the value; put `${user_config.KEY}` in the server's static `headers` field instead (not shell-parsed), or have the helper script read its own environment/config file. Before v2.1.207, `headersHelper` substituted `${user_config.*}` values directly. (v2.1.207)

A remote server whose config has an empty `url` now shows as `not configured` in `/mcp`, `claude mcp list`, and `/plugin`, with no connection attempted — useful for a plugin placeholder entry you fill in later. Before v2.1.208, an empty `url` was reported as a configuration issue with a misleading prompt to reconnect. (v2.1.208)

An MCP tool call running longer than 2 minutes now moves to the background automatically, same as a long-running Bash command, so the session stays usable while it finishes. Configure the threshold or disable with `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS` (ms; not yet reflected on the live MCP reference page as of this run — captured from the changelog). (v2.1.212)

`mcp_server_errors` field in the headless `stream-json` init event lists `--mcp-config` entries skipped by config validation; terminal runs print a startup warning instead. `claude mcp list`/`/mcp` now show HTTP status + error text when a server fails to connect, plus a warning for config values with hidden leading/trailing whitespace. (v2.1.219)

`.mcp.json` supports env var expansion in `command`, `args`, `env`, `url`, and `headers`: `${VAR}` expands to the env var's value, `${VAR:-default}` falls back to `default` when unset. An unset var with no default still loads (unexpanded `${VAR}` text used as-is) but `claude mcp list` shows a missing-variable warning.

A remote (HTTP/SSE) server you've used before can show `cached` status in `/mcp` (e.g. `cached 2h ago · connects on first use`) instead of connecting at startup — Claude Code reuses the prior session's tool list and connects on first actual tool call. Set `MCP_DISCOVERY_CACHE=1` to force it on, or `0` to force every server to connect at startup instead. (v2.1.221) **Default flipped (v2.1.238)**: the discovery cache is now off by default unless a gradual rollout has enabled it for your account (before v2.1.238 it was on by default).

`claude mcp list`/`claude mcp get` now show a disabled server as `⊘ Disabled` instead of connecting to it for a health check. (v2.1.238)

Per-server `timeout` (ms, in `.mcp.json`) is a hard wall-clock cap per tool call and floors the idle-timeout window; it's distinct from `MCP_TOOL_TIMEOUT`, whose unset default is ~28 hours. HTTP/SSE/connector servers also have a separate 60s per-request timer (time to first response byte) that only a `timeout`/`MCP_TOOL_TIMEOUT` of ≥60s raises; stdio/WebSocket servers have no per-request timer.

`claude mcp serve`: runs Claude Code itself as an MCP server other applications (e.g. Claude Desktop) can connect to via stdio.

`MAX_MCP_OUTPUT_TOKENS` env var: raises the MCP tool-output token limit (default 25,000). `MCP_TIMEOUT` env var: configures a server's startup timeout (ms).

SSE transport (`--transport sse`) is documented as deprecated in favor of HTTP; existing SSE servers still work.

## Plugins

A url marketplace/catalog entry's `headersHelper` can mint HTTP headers (e.g. a short-lived token) for catalog and same-origin archive fetches; it runs only when you install/update that plugin, shown once before `claude plugin install`/`update` prompt `[y/N]` (or `-y` non-interactively). MCP `headersHelper` in a project `.mcp.json`, or an inline MCP server in a project/`--add-dir` agent file, now also requires that folder's trust dialog to have been accepted (including under `claude -p`); it runs without inherited credential env vars — user/managed/claude.ai-scope `headersHelper`s now run from the Claude config dir instead. (v2.1.238)

Cloud sessions: plugins synced from your claude.ai account now show as `name@synced` in `/plugin` and work with `claude plugin enable/disable <name>@synced`; a synced plugin never overrides a same-named plugin you installed yourself. (v2.1.239)

Plugin commands declared in a marketplace entry can no longer point outside the plugin directory — such paths are now rejected with a path-traversal error. (v2.1.251) **Extended (v2.1.257)**: the same check now covers every declared plugin component path (command, agent, skill, hooks, etc.) that resolves through a symlink pointing outside the plugin's own directory.

**`archive` plugin source (v2.1.224)**: install a plugin from a `.zip` over HTTPS with no git or npm required, with optional SHA-256 pinning for integrity. Complements `--plugin-dir`/`--plugin-url` for local/hosted testing.

**Marketplace `command` source (v2.1.229)**: a marketplace entry can point at a local command (e.g. run by an IDE) that prints the plugin's directory path; re-resolved every session and applied without a restart. `mode: "link"` uses the printed path in place, like a local symlink source. Constraints: `command` must be printable ASCII, ≤500 chars, no runs of 4+ spaces (so users can review it); shown once for explicit accept (`--yes` non-interactively) and every later re-run reuses only the accepted string; never installed as a dependency of another plugin. Admins can block org-wide with `disableCommandPluginSources` (also blocked by default when `allowManagedHooksOnly` is set).

GitLab (and other git hosts) is supported as a plugin marketplace source via the generic `url` type (full URL incl. scheme, e.g. `https://gitlab.com/team/plugin.git`) — has worked for a while. **v2.1.232 changelog also lists "GitLab support in plugin marketplaces with bare URLs"** as a new, more direct form — not yet reflected on the live plugin-marketplaces page as of this run; re-confirm mechanics next run. **Confirmed (2026-08-17), from the v2.1.232 changelog entry itself**: bare `gitlab.com` repo URLs (including nested subgroups, e.g. `gitlab.com/group/subgroup/repo`) now clone the same way bare `github.com` URLs already did — no scheme or `.git` suffix needed; clone auth-failure hints now name your actual git host instead of assuming GitHub.

Plugins installed via `/plugin install` now activate immediately when safe, instead of always requiring `/reload-plugins`. Plugins now accept `"."` as a `skills` path (the root-level-`SKILL.md` validation error suggests this too). `claude plugin validate` now warns when a marketplace or plugin name would be rejected by Claude Desktop's managed marketplace sync. Agent markdown files reject names containing `:` (reserved for plugin namespacing). (v2.1.221/v2.1.218)

Bundle skills + hooks + agents + MCP servers into distributable unit. `plugin.json` manifest. Plugin `hooks.json` for hook definitions. Distribute via marketplaces. Plugin agents cannot use `hooks`, `mcpServers`, or `permissionMode` frontmatter (security restriction). Plugin `bin/` directory: executables added to Bash tool's PATH while plugin is enabled; cannot be included in a plugin distributed through claude.ai organization settings. `/reload-plugins` reloads without restarting — warns and skips the reload if it would change loaded MCP tools and invalidate the prompt cache; pass `--force` to proceed anyway. `--plugin-dir` flag for local testing; repeatable to load multiple plugins in one session (`--plugin-dir ./a --plugin-dir ./b`); also accepts a path to a `.zip` archive of the plugin directory, not just a directory. (v2.1.128) A `--plugin-dir` plugin sharing a name with an installed marketplace plugin takes precedence for that session only (test local changes without uninstalling). Cannot override a plugin that managed settings force-enables or force-disables. Plugin LSP servers via `.lsp.json`. Plugin default settings via `settings.json` at plugin root (`agent` and `subagentStatusLine` keys supported). `subagentStatusLine` payload now also includes the active reasoning effort level, so a custom agent-row renderer can show model + effort together. (v2.1.214)

Submit to official marketplace: `claude.ai/settings/plugins/submit` or `platform.claude.com/plugins/submit`.
Doc correction: these forms route to **community-marketplace review only** — updated claude.ai form path is `claude.ai/admin-settings/directory/submissions/plugins/new` (needs Team/Enterprise + directory management access; individual authors use the Console form instead). The official marketplace (`claude-plugins-official`) is curated directly by Anthropic with no application process. Approved community submissions are pinned to a commit SHA in the `anthropics/claude-plugins-community` catalog and sync to `marketplace.json` nightly.

`monitors` manifest key: declare background monitors bundled with plugin; started automatically when plugin enabled. (v2.1.105)

Plugin `plugin.json` can declare dependencies that auto-install when plugin is enabled. (v2.1.110)

`--plugin-url <url>` flag: install a plugin directly from a URL pointing to a `.zip` archive (complements `--plugin-dir` for local dirs). (v2.1.129)

Plugin with root-level `SKILL.md` and no `skills/` subdirectory automatically surfaces as a skill (no separate `skills/` directory needed). (v2.1.142)

`claude plugin disable` now refuses if another enabled plugin declares a dependency on the target, displaying which plugin depends on it. Disable the dependent plugin first, then retry. (v2.1.143)

`claude plugin validate`: run locally before submitting to marketplace — same checks the review pipeline runs. Use before `claude.ai/settings/plugins/submit` submissions. Prints `✔ Validation passed` (or `✔ Validation passed with warnings`); warnings don't fail validation unless `--strict` is passed, which treats them as errors.

Community marketplace: add with `/plugin marketplace add anthropics/claude-plugins-community`, then install from it as `@claude-community`. Official marketplace (`claude-plugins-official`) is auto-available in every install.

MCP elicitation: MCP servers can request structured user input mid-task via interactive dialogs — form mode (fields defined by server) or URL mode (browser OAuth/approval). Appears automatically; no user config needed. Use `Elicitation` hook to auto-respond without showing dialog.

`defaultEnabled: false` in `plugin.json`: plugin is disabled by default; user must explicitly enable with `/plugin enable <name>`. Useful for plugins that should be opt-in rather than auto-enabled on install. (v2.1.154)

`claude plugin init <name>`: scaffolds a new plugin in `~/.claude/skills/<name>/` with `.claude-plugin/plugin.json` manifest and starter `SKILL.md`. Loads automatically at next session start. (v2.1.157)

Plugins in `.claude/skills/` directories auto-load at session start — no marketplace, install step, or `--plugin-dir` flag needed. Named as `<name>@skills-dir` in plugin list. (v2.1.157) In a **project's** `.claude/skills/` (not `~/.claude/skills/`), this requires accepting the workspace-trust dialog first.

`--plugin-url <url>` can be repeated, or passed as one quoted space-separated string, to load multiple hosted `.zip` plugins in one session (complements the single-plugin form above).

After editing a skill and running `/reload-plugins`, the reload summary's skill count only tallies `commands/`-style directories — it can print `0 skills` even though the skill you just edited reloaded correctly. Not a failure signal; check `/plugin-name:skill-name` directly to confirm.

claude.ai connectors: unused connectors (never signed in to) are collapsed behind a "Show unused connectors" row in `/mcp` as of v2.1.161 — org-provisioned lists no longer fill the panel. Previously-signed-in connectors stay visible even when re-authentication is needed. (v2.1.161)

## Channels (v2.1.81+)

Push events into running sessions from MCP servers. MCP server declares a `channel` capability; sends `claude/channel/notification` events; session receives and Claude can react. Useful for CI results, monitoring alerts, chat messages pushed in while Claude works. Permissions relay via `--channels` flag.
