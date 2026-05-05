---
name: bad-example-agent
description: Negative fixture — uses permissionMode which is forbidden in plugin agents.
model: sonnet
tools: Read, Grep
permissionMode: acceptEdits
---

# Bad Example Agent

This agent has `permissionMode` in its frontmatter, which is silently ignored by the
plugin loader and is therefore an error to commit. The verify hook must reject this.
