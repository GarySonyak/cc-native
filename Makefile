.PHONY: test test-verify test-reminder test-audit clean

PYTHON ?= python3
HOOK_VERIFY := hooks/cc-native-verify.py
HOOK_REMIND := hooks/cc-native-reminder.py
HOOK_AUDIT  := hooks/maybe-audit.py
F_DIR := tests/fixtures/.claude

test: test-verify test-reminder test-audit
	@echo "OK — all hook fixture tests passed"

# Each fixture line: <expected exit code> <relative file_path>
# Fixture paths are absolute under the cwd so the verify hook can stat them.
test-verify:
	@echo "==> cc-native-verify"
	@fail=0 ; \
	for case in \
	  "0 $(F_DIR)/agents/good-agent.md" \
	  "2 $(F_DIR)/agents/bad-agent-permmode.md" \
	  "0 $(F_DIR)/settings.json" \
	  "2 $(F_DIR)/settings-bad.json" \
	  "2 $(F_DIR)/settings-secret-env.json" \
	  "2 $(F_DIR)/settings-secret-basic-auth.json" \
	  "2 $(F_DIR)/hooks/bad-hook-no-stdin.py" ; do \
	  expected=$${case%% *}; path=$${case#* }; \
	  printf '{"tool_input":{"file_path":"%s"}}' "$$(realpath $$path)" \
	    | CLAUDE_PLUGIN_ROOT="$(CURDIR)" $(PYTHON) $(HOOK_VERIFY) > /tmp/cc-verify.out 2> /tmp/cc-verify.err ; \
	  got=$$? ; \
	  if [ "$$got" != "$$expected" ]; then \
	    echo "FAIL  $$path (expected exit $$expected, got $$got)"; \
	    cat /tmp/cc-verify.out /tmp/cc-verify.err 1>&2 ; fail=1 ; \
	  else \
	    echo "  ok  $$path (exit $$got)"; \
	  fi ; \
	done ; \
	exit $$fail

test-reminder:
	@echo "==> cc-native-reminder"
	@printf '{"tool_input":{"file_path":"/x/.claude/agents/foo.md"}}' \
	  | $(PYTHON) $(HOOK_REMIND) | grep -q "feature-guide" \
	  && echo "  ok  reminder fires for .claude/agents/" \
	  || (echo "FAIL  reminder did not inject feature-guide directive"; exit 1)
	@printf '{"tool_input":{"file_path":"/tmp/random.txt"}}' \
	  | $(PYTHON) $(HOOK_REMIND) > /tmp/cc-rem-other.out ; \
	  if [ -s /tmp/cc-rem-other.out ]; then \
	    echo "FAIL  reminder fired for non-config path"; exit 1 ; \
	  else \
	    echo "  ok  reminder silent for non-config path" ; \
	  fi

test-audit:
	@echo "==> maybe-audit"
	@printf '{"transcript_path":"/nonexistent"}' \
	  | $(PYTHON) $(HOOK_AUDIT) > /tmp/cc-audit.out ; \
	  if [ -s /tmp/cc-audit.out ]; then \
	    echo "FAIL  maybe-audit emitted output without a transcript"; exit 1 ; \
	  else \
	    echo "  ok  maybe-audit silent on missing transcript" ; \
	  fi
	@printf '{"transcript_path":"tests/fixtures/transcripts/needs-audit.jsonl"}' \
	  | $(PYTHON) $(HOOK_AUDIT) > /tmp/cc-audit.out ; \
	  if grep -q '"decision": "block"' /tmp/cc-audit.out; then \
	    echo "  ok  maybe-audit blocks when auditor not yet invoked" ; \
	  else \
	    echo "FAIL  maybe-audit did not block on un-audited config edit"; cat /tmp/cc-audit.out; exit 1 ; \
	  fi
	@printf '{"transcript_path":"tests/fixtures/transcripts/loop-fixed.jsonl"}' \
	  | $(PYTHON) $(HOOK_AUDIT) > /tmp/cc-audit.out ; \
	  if [ -s /tmp/cc-audit.out ]; then \
	    echo "FAIL  maybe-audit re-blocked after auditor already ran via Task tool (loop regression)"; cat /tmp/cc-audit.out; exit 1 ; \
	  else \
	    echo "  ok  maybe-audit silent after Task-tool auditor invocation" ; \
	  fi
	@printf '{"transcript_path":"tests/fixtures/transcripts/loop-fixed-agent.jsonl"}' \
	  | $(PYTHON) $(HOOK_AUDIT) > /tmp/cc-audit.out ; \
	  if [ -s /tmp/cc-audit.out ]; then \
	    echo "FAIL  maybe-audit re-blocked after auditor already ran via Agent tool (SDK harness regression)"; cat /tmp/cc-audit.out; exit 1 ; \
	  else \
	    echo "  ok  maybe-audit silent after Agent-tool auditor invocation" ; \
	  fi
	@printf '{"transcript_path":"tests/fixtures/transcripts/edit-after-audit.jsonl"}' \
	  | $(PYTHON) $(HOOK_AUDIT) > /tmp/cc-audit.out ; \
	  if grep -q '"decision": "block"' /tmp/cc-audit.out && grep -q 'settings.json' /tmp/cc-audit.out; then \
	    echo "  ok  maybe-audit re-blocks for new edits after a prior audit" ; \
	  else \
	    echo "FAIL  maybe-audit did not flag a fresh edit made after a prior auditor call"; cat /tmp/cc-audit.out; exit 1 ; \
	  fi

clean:
	rm -f /tmp/cc-verify.out /tmp/cc-verify.err /tmp/cc-rem-other.out /tmp/cc-audit.out
