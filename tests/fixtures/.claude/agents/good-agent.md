---
name: example-agent
description: A minimal valid plugin agent used as a positive fixture for cc-native-verify.
model: sonnet
tools: Read, Grep, Glob
---

# Example Agent

This agent is a minimal valid example. Frontmatter has `name` and `description` (required),
plus `model` and `tools` (optional). It does NOT use `permissionMode`, `hooks`, or `mcpServers`
which would make it invalid in a plugin context.
