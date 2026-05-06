# Security policy

## Reporting a vulnerability

Email **gary.sonyak@gmail.com** or use GitHub's [private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) on this repo.

**Please do not file public GitHub issues for security reports.**

You should expect an acknowledgment within **7 days**. Coordinated disclosure timelines are negotiated case-by-case.

## Scope

cc-native is a Claude Code plugin that lints and audits `.claude/` config artifacts. It does **not** execute arbitrary user code; the verify hook reads JSON/YAML/markdown and runs a smoke probe (`echo '{}' | python <hook>`) against user-authored hook scripts.

The most likely vulnerability classes are:

- A malicious or malformed `.claude/` artifact that bypasses the verify hook and lands in the user's config silently.
- A hook smoke-probe that executes attacker-controlled code with broader effects than the documented `echo '{}' | …` envelope.
- Reference pages under `skills/feature-guide/references/` that misstate Claude Code behavior in a way that produces unsafe configs.

Reports against any of these are in scope. General Claude Code or Anthropic API issues should go to Anthropic directly.
