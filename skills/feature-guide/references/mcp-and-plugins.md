# MCP, Plugins, Channels

## MCP

Servers in `.mcp.json` (project) or `~/.claude/.mcp.json` (global). Tools appear as `mcp__<server>__<tool>`. Use `ToolSearch` to discover deferred tools (only names loaded initially -- saves context). Scoping: local > project > user. Check per-server context cost with `/mcp`. MCP OAuth RFC 9728 supported (v2.1.85+). MCP prompts appear as commands: `/mcp__<server>__<prompt>`. In `.mcp.json`/`~/.claude.json`/`claude mcp add-json` configs, `type: "streamable-http"` is accepted as alias for `type: "http"` (MCP spec name). (v2.1.153)

`alwaysLoad: true` in server config: always loads all server tools at session start, bypassing tool search. Per-tool: `_meta: {"anthropic/alwaysLoad": true}`. Use sparingly — each eager tool consumes context. (v2.1.121)

`headersHelper`: shell command/script path in server config that generates dynamic request headers at connection time. Outputs JSON key-value pairs to stdout; env vars `CLAUDE_CODE_MCP_SERVER_NAME`/`CLAUDE_CODE_MCP_SERVER_URL` available. Overrides static `headers`; re-runs on reconnect. Use for non-OAuth auth (Kerberos, short-lived tokens, SSO).

`oauth.scopes`: space-separated string pinning scopes requested during OAuth flow to a security-approved subset. Overrides server-advertised scopes (takes precedence over `authServerMetadataUrl`). Leave unset to let server determine scopes.

`authServerMetadataUrl` (in `oauth` block): override OAuth discovery — bypass default RFC 9728/RFC 8414 chain and point to specific authorization server metadata URL. Requires `https://`. (v2.1.64+)

`claude mcp login <name>` / `claude mcp logout <name>`: authenticate or deauthenticate with a specific MCP server from the CLI, without opening the `/mcp` menu. `--no-browser` flag redirects auth flow to stdin — required in SSH/headless sessions. `claude mcp get`/`claude mcp remove` now suggest typo corrections and truncate long server lists. (v2.1.186)

Managed MCP policy: `allowedMcpServers`/`deniedMcpServers` in managed settings restrict users to approved servers. Match by `serverName`, `serverCommand` (exact array), or `serverUrl` (wildcard `*`). Allowlist behavior: undefined=no restriction, `[]`=full lockdown, list=whitelist. Denylist takes absolute precedence over allowlist. Option 1 (`managed-mcp.json`)=exclusive control over all servers; Option 2 (allowlists/denylists)=policy overlay allowing user-added servers within constraints. Both can coexist. (v2.1.128)

`MCP_TOOL_TIMEOUT` env var: raises per-request fetch timeout for remote MCP servers (was previously capped at 60s regardless of this setting). Set to timeout in ms. (v2.1.142)

`type: "ws"` in server config: WebSocket transport — persistent bidirectional connection for servers that push events unprompted. Configure via `claude mcp add-json`. Does NOT support `--transport` flag or OAuth. Accepts url, headers, headersHelper, timeout, alwaysLoad fields.

`list_changed` notification support: MCP servers can send `list_changed` notifications to dynamically refresh their available tools, prompts, and resources mid-session — Claude Code auto-refreshes capabilities on receipt, no disconnect/reconnect needed.

`_meta["anthropic/requiresUserInteraction"]: true` on a tool's `tools/list` entry (server-side): forces a permission prompt on every call to that tool, even in `acceptEdits`/`auto`/`bypassPermissions`, with no "don't ask again" option; `dontAsk` mode denies the call instead of prompting. Use for consent/access-grant tools where auto-approval would defeat the point. (v2.1.199)

`claude mcp list`/`claude mcp get`: as of v2.1.196, project-scoped `.mcp.json` server approvals are read only from settings files not checked into the repo, until the workspace-trust dialog is accepted — a freshly cloned repo can't self-approve its own servers via a committed `enableAllProjectMcpServers`/`enabledMcpjsonServers`.

`CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`: a tool call to a remote HTTP/SSE/WebSocket/claude.ai-connector server that sends no response or progress notification for 5 minutes now aborts instead of waiting for the full wall-clock timeout. Set in ms; `0` disables the check. Stdio servers aren't subject to it. (v2.1.187)

Plugin-provided MCP tools use the full name `mcp__plugin_<plugin-name>_<server-name>__<tool-name>` (any character outside `A-Z a-z 0-9 _ -` sanitized to `_`) — use this exact form in permission rules, a skill's `allowed-tools`, or a subagent's `tools` field, not the shorter `mcp__<server>__<tool>` form used for user-configured servers.

`${CLAUDE_PLUGIN_DATA}`: a plugin's persistent data directory, distinct from `${CLAUDE_PLUGIN_ROOT}` (the versioned install path) — state written here survives plugin updates. Available in plugin `.mcp.json`/`plugin.json` server configs and hooks.

MCP `roots/list` request now also returns the session's additional working directories (`--add-dir`), not just the directory Claude Code was launched from. (v2.1.203)

## Plugins

Bundle skills + hooks + agents + MCP servers into distributable unit. `plugin.json` manifest. Plugin `hooks.json` for hook definitions. Distribute via marketplaces. Plugin agents cannot use `hooks`, `mcpServers`, or `permissionMode` frontmatter (security restriction). Plugin `bin/` directory: executables added to Bash tool's PATH while plugin is enabled. `/reload-plugins` reloads without restarting — warns and skips the reload if it would change loaded MCP tools and invalidate the prompt cache; pass `--force` to proceed anyway. `--plugin-dir` flag for local testing. Plugin LSP servers via `.lsp.json`. Plugin default settings via `settings.json` at plugin root (`agent` and `subagentStatusLine` keys supported).

Submit to official marketplace: `claude.ai/settings/plugins/submit` or `platform.claude.com/plugins/submit`.
Doc correction: these forms route to **community-marketplace review only** — updated claude.ai form path is `claude.ai/admin-settings/directory/submissions/plugins/new` (needs Team/Enterprise + directory management access; individual authors use the Console form instead). The official marketplace (`claude-plugins-official`) is curated directly by Anthropic with no application process. Approved community submissions are pinned to a commit SHA in the `anthropics/claude-plugins-community` catalog and sync to `marketplace.json` nightly.

`monitors` manifest key: declare background monitors bundled with plugin; started automatically when plugin enabled. (v2.1.105)

Plugin `plugin.json` can declare dependencies that auto-install when plugin is enabled. (v2.1.110)

`--plugin-url <url>` flag: install a plugin directly from a URL pointing to a `.zip` archive (complements `--plugin-dir` for local dirs). (v2.1.129)

Plugin with root-level `SKILL.md` and no `skills/` subdirectory automatically surfaces as a skill (no separate `skills/` directory needed). (v2.1.142)

`claude plugin disable` now refuses if another enabled plugin declares a dependency on the target, displaying which plugin depends on it. Disable the dependent plugin first, then retry. (v2.1.143)

`claude plugin validate`: run locally before submitting to marketplace — same checks the review pipeline runs. Use before `claude.ai/settings/plugins/submit` submissions.

Community marketplace: add with `/plugin marketplace add anthropics/claude-plugins-community`, then install from it as `@claude-community`. Official marketplace (`claude-plugins-official`) is auto-available in every install.

MCP elicitation: MCP servers can request structured user input mid-task via interactive dialogs — form mode (fields defined by server) or URL mode (browser OAuth/approval). Appears automatically; no user config needed. Use `Elicitation` hook to auto-respond without showing dialog.

`defaultEnabled: false` in `plugin.json`: plugin is disabled by default; user must explicitly enable with `/plugin enable <name>`. Useful for plugins that should be opt-in rather than auto-enabled on install. (v2.1.154)

`claude plugin init <name>`: scaffolds a new plugin in `~/.claude/skills/<name>/` with `.claude-plugin/plugin.json` manifest and starter `SKILL.md`. Loads automatically at next session start. (v2.1.157)

Plugins in `.claude/skills/` directories auto-load at session start — no marketplace, install step, or `--plugin-dir` flag needed. Named as `<name>@skills-dir` in plugin list. (v2.1.157) In a **project's** `.claude/skills/` (not `~/.claude/skills/`), this requires accepting the workspace-trust dialog first.

`--plugin-url <url>` can be repeated, or passed as one quoted space-separated string, to load multiple hosted `.zip` plugins in one session (complements the single-plugin form above).

claude.ai connectors: unused connectors (never signed in to) are collapsed behind a "Show unused connectors" row in `/mcp` as of v2.1.161 — org-provisioned lists no longer fill the panel. Previously-signed-in connectors stay visible even when re-authentication is needed. (v2.1.161)

## Channels (v2.1.81+)

Push events into running sessions from MCP servers. MCP server declares a `channel` capability; sends `claude/channel/notification` events; session receives and Claude can react. Useful for CI results, monitoring alerts, chat messages pushed in while Claude works. Permissions relay via `--channels` flag.
