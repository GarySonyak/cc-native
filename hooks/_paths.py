"""Shared regex set for matching Claude Code configuration file paths.

Used by both PreToolUse (cc-native-reminder.py) and PostToolUse (cc-native-verify.py)
hooks. Keep this list in sync with the skill's reference docs.
"""

CONFIG_PATTERNS = [
    r"/\.claude/agents/",
    r"/\.claude/skills/",
    r"/\.claude/commands/",
    r"/\.claude/output-styles/",
    r"/\.claude/hooks/",
    r"/\.claude/schedules/",
    r"/\.claude/rules/",
    r"/\.claude/settings[^/]*\.json$",
    r"/\.claude/CLAUDE\.md$",
    r"/\.claude/loop\.md$",
    r"(^|/)\.mcp\.json$",
    r"(^|/)\.claude-plugin/",
]
