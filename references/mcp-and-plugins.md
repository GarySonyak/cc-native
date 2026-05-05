# MCP, Plugins, Channels

## MCP

Servers in `.mcp.json` (project) or `~/.claude/.mcp.json` (global). Tools appear as `mcp__<server>__<tool>`. Use `ToolSearch` to discover deferred tools (only names loaded initially -- saves context). Scoping: local > project > user. Check per-server context cost with `/mcp`. MCP OAuth RFC 9728 supported (v2.1.85+). MCP prompts appear as commands: `/mcp__<server>__<prompt>`.

`alwaysLoad: true` in server config: always loads all server tools at session start, bypassing tool search. Per-tool: `_meta: {"anthropic/alwaysLoad": true}`. Use sparingly — each eager tool consumes context. (v2.1.121)

## Plugins

Bundle skills + hooks + agents + MCP servers into distributable unit. `plugin.json` manifest. Plugin `hooks.json` for hook definitions. Distribute via marketplaces. Plugin agents cannot use `hooks`, `mcpServers`, or `permissionMode` frontmatter (security restriction). Plugin `bin/` directory: executables added to Bash tool's PATH while plugin is enabled. `/reload-plugins` reloads without restarting. `--plugin-dir` flag for local testing. Plugin LSP servers via `.lsp.json`. Plugin default settings via `settings.json` at plugin root (`agent` and `subagentStatusLine` keys supported).

Submit to official marketplace: `claude.ai/settings/plugins/submit` or `platform.claude.com/plugins/submit`.

`monitors` manifest key: declare background monitors bundled with plugin; started automatically when plugin enabled. (v2.1.105)

Plugin `plugin.json` can declare dependencies that auto-install when plugin is enabled. (v2.1.110)

## Channels (v2.1.81+)

Push events into running sessions from MCP servers. MCP server declares a `channel` capability; sends `claude/channel/notification` events; session receives and Claude can react. Useful for CI results, monitoring alerts, chat messages pushed in while Claude works. Permissions relay via `--channels` flag.
