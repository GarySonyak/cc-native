#!/bin/bash
# docs-monitor-cron — Daily CC docs monitor for the cc-native plugin maintainer.
# Edits /root/cc-native/skills/feature-guide/references/* via the docs-monitor agent,
# bumps PATCH version on material change, commits, and pushes to origin.
#
# Designed to run on Gary's machine ONLY. Not shipped in the plugin.
set -u
PLUGIN_REPO="/root/cc-native"
LOG="/root/.claude/logs/docs-monitor.log"
TG_ENV="/root/.claude/channels/telegram/.env"
AGENT_FILE="${PLUGIN_REPO}/scripts/maintainer/docs-monitor.md"
LIVE_AGENT="/root/.claude/agents/docs-monitor.md"
BUMPER="${PLUGIN_REPO}/scripts/maintainer/bump-patch.py"
SNAPSHOTS_DIR="/root/docs-snapshots"

mkdir -p /root/.claude/logs "$SNAPSHOTS_DIR"

# Load Telegram credentials (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
if [ -f "$TG_ENV" ]; then
  # shellcheck disable=SC1090
  source "$TG_ENV"
fi
CHAT_ID="${TELEGRAM_CHAT_ID:-}"

echo "=== $(date -u '+%Y-%m-%d %H:%M UTC') ===" >> "$LOG"

# Sync the live agent definition with the tracked maintainer copy so cron sees the
# same file the repo holds. This is idempotent.
if [ -f "$AGENT_FILE" ]; then
  cp -f "$AGENT_FILE" "$LIVE_AGENT"
fi

START_TS=$(date +%s)
OUTPUT=$(cd "$PLUGIN_REPO" && printf '%s' "Follow the workflow in ${AGENT_FILE}. Fetch all CC doc pages, compare against snapshots in ${SNAPSHOTS_DIR}/, edit reference files in ${PLUGIN_REPO}/skills/feature-guide/references/ as needed, report changes via Telegram (chat_id: ${CHAT_ID})." | \
  CLAUDECODE="" timeout 1500 /root/.local/bin/claude -p \
  --agent docs-monitor \
  --permission-mode dontAsk \
  --allowedTools "WebFetch(domain:code.claude.com),WebFetch(domain:docs.claude.com),Read,Write,Edit,Bash(md5sum:*),Bash(diff:*),Bash(mkdir:*),Bash(date:*),Grep,mcp__plugin_telegram_telegram__reply" \
  2>&1)
DURATION=$(( $(date +%s) - START_TS ))
if [ "$DURATION" -ge 60 ]; then
  DUR_STR="$((DURATION / 60))m$((DURATION % 60))s"
else
  DUR_STR="${DURATION}s"
fi

# Replace the agent's "n/a" duration placeholder with the wrapper-measured value.
OUTPUT=$(printf '%s' "$OUTPUT" | sed -E "s#^(Run \#[0-9]+ \| [0-9-]+ )\| n/a#\1| ${DUR_STR}#")

if [ -n "$OUTPUT" ]; then
  echo "$OUTPUT" >> "$LOG"
  TG_MSG="$OUTPUT"
else
  FALLBACK="[$(date -u '+%Y-%m-%d')] docs-monitor: completed but produced no summary (duration ${DUR_STR})"
  echo "$FALLBACK" >> "$LOG"
  TG_MSG="$FALLBACK"
fi

# --- Bump+commit+push tail (only on material change to references/) ---
cd "$PLUGIN_REPO" || { echo "[wrapper] cannot cd to $PLUGIN_REPO" >> "$LOG"; exit 1; }

if git diff --quiet -- skills/feature-guide/references/ skills/feature-guide/SKILL.md; then
  echo "[wrapper] no reference changes — skipping bump+push" >> "$LOG"
else
  if [ -x "$BUMPER" ] || [ -f "$BUMPER" ]; then
    SUMMARY_FILE="$(mktemp /tmp/docs-monitor-summary.XXXXXX)"
    printf '%s' "$TG_MSG" | head -c 200 > "$SUMMARY_FILE"
    if python3 "$BUMPER" --summary-file "$SUMMARY_FILE" >> "$LOG" 2>&1; then
      git add -A
      RUN_NUM="$(date -u '+%Y%m%d')"
      if git -c user.name="docs-monitor" -c user.email="docs-monitor@cc-native.local" \
          commit -m "docs(refs): patch update from docs-monitor run ${RUN_NUM}" >> "$LOG" 2>&1; then
        if git push origin HEAD >> "$LOG" 2>&1; then
          echo "[wrapper] pushed to origin" >> "$LOG"
        else
          echo "[wrapper] PUSH-FAILED" >> "$LOG"
        fi
      else
        echo "[wrapper] COMMIT-FAILED" >> "$LOG"
      fi
    else
      echo "[wrapper] BUMP-FAILED" >> "$LOG"
    fi
    rm -f "$SUMMARY_FILE"
  else
    echo "[wrapper] bumper missing at $BUMPER — skipping" >> "$LOG"
  fi
fi

# --- Wrapper-level Telegram heartbeat (fires regardless of agent's MCP state) ---
if [ -f "$TG_ENV" ] && [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
  TG_BODY=$(printf '%s' "$TG_MSG" | head -c 3800)
  HTTP_CODE=$(curl -s -o /tmp/docs-monitor-tg.out -w "%{http_code}" \
    -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${CHAT_ID}" \
    --data-urlencode "text=cc-native docs-monitor heartbeat $(date -u '+%Y-%m-%d %H:%M UTC')

${TG_BODY}")
  if [ "$HTTP_CODE" = "200" ]; then
    echo "[wrapper] Telegram heartbeat sent (HTTP 200)" >> "$LOG"
  else
    echo "[wrapper] TELEGRAM-FAILED HTTP=$HTTP_CODE body=$(cat /tmp/docs-monitor-tg.out 2>/dev/null | head -c 200)" >> "$LOG"
  fi
  rm -f /tmp/docs-monitor-tg.out
else
  echo "[wrapper] TELEGRAM-SKIPPED no $TG_ENV or TELEGRAM_BOT_TOKEN" >> "$LOG"
fi

echo "=== Done $(date -u '+%Y-%m-%d %H:%M UTC') ===" >> "$LOG"
