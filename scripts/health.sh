#!/bin/zsh
set -e

# ---------- config ----------
EXP_DEFAULT="artifacts/earn/experiments/20250919_211414__micro-service-offer-audit-implementation"
EXP="${1:-$EXP_DEFAULT}"

SCHEMAS_DIR="schemas"
EVENT_SCHEMA="$SCHEMAS_DIR/event.schema.json"
CMD_SCHEMA="$SCHEMAS_DIR/command.schema.json"
METRICS_SCHEMA="$SCHEMAS_DIR/metrics_summary.schema.json"

BUS_DIR="bus"
BUS_EVENTS="$BUS_DIR/events.jsonl"
BUS_CMDS="$BUS_DIR/commands.jsonl"

PY_VALIDATOR="tools/schema_validate.py"

# ---------- ui helpers ----------
ok(){   print -P "%F{green}✔%f $*"; }
warn(){ print -P "%F{yellow}⚠%f $*"; }
err(){  print -P "%F{red}✖%f $*"; }
hdr(){  print -P "\n%F{cyan}==>%f $*"; }

EXIT_CODE=0
fail(){ err "$*"; EXIT_CODE=1; }

# ---------- deps ----------
hdr "Checking dependencies"
command -v python3 >/dev/null && ok "python3 found" || { fail "python3 missing"; }
command -v jq >/dev/null && ok "jq found" || { fail "jq missing"; }
command -v gh >/dev/null && ok "gh found" || warn "gh not found (PR/release checks will be skipped)"

python3 - <<'PY' 2>/dev/null && echo "OK jsonschema" >/dev/null || true
try:
    import jsonschema  # noqa
    print("OK")
except Exception:
    pass
PY
if [ "$(tail -n1 <<<"$(python3 - <<'PY'
try:
    import jsonschema
    print("OK")
except:
    print("NO")
PY
)")" = "OK" ]; then
  ok "python jsonschema installed"
else
  warn "python 'jsonschema' not installed (schema validation will be soft)"
fi

# ---------- files ----------
hdr "Checking files & layout"
[ -d "$EXP" ] && ok "EXP exists: $EXP" || fail "EXP not found: $EXP"
[ -f tools/metrics_aggregate.py ] && ok "tools/metrics_aggregate.py" || fail "missing tools/metrics_aggregate.py"
[ -f tools/bus_dispatcher.py ] && ok "tools/bus_dispatcher.py" || fail "missing tools/bus_dispatcher.py"
[ -f scripts/exp_release.sh ] && ok "scripts/exp_release.sh" || fail "missing scripts/exp_release.sh"
[ -f scripts/exp_status.sh ] && ok "scripts/exp_status.sh" || warn "scripts/exp_status.sh not found (status step skipped)"

[ -f "$EVENT_SCHEMA" ]   && ok "schema: $EVENT_SCHEMA"   || fail "missing $EVENT_SCHEMA"
[ -f "$CMD_SCHEMA" ]     && ok "schema: $CMD_SCHEMA"     || fail "missing $CMD_SCHEMA"
[ -f "$METRICS_SCHEMA" ] && ok "schema: $METRICS_SCHEMA" || fail "missing $METRICS_SCHEMA"

# ---------- schema validation helpers ----------
have_validator=false
if [ -f "$PY_VALIDATOR" ]; then
  have_validator=true
fi

validate_json () {
  local schema="$1"; local jsonfile="$2"
  if [ "$have_validator" = true ]; then
    if python3 "$PY_VALIDATOR" "$schema" "$jsonfile" >/dev/null 2>&1; then
      ok "validated: $(basename "$jsonfile") against $(basename "$schema")"
    else
      fail "schema validation failed: $(basename "$jsonfile")"
    fi
  else
    # soft check: ensure JSON parses
    if jq type "$jsonfile" >/dev/null 2>&1; then
      ok "json parse OK (soft): $(basename "$jsonfile")"
    else
      fail "invalid json: $(basename "$jsonfile")"
    fi
  fi
}

validate_jsonl () {
  local schema="$1"; local jsonl="$2"; local name="$(basename "$jsonl")"
  if [ ! -f "$jsonl" ]; then
    warn "$name not found (skip)"; return
  fi
  local lineno=0
  while IFS= read -r line || [ -n "$line" ]; do
    lineno=$((lineno+1))
    [ -z "$line" ] && continue
    if [ "$have_validator" = true ]; then
      if ! python3 "$PY_VALIDATOR" "$schema" - <<<"$line" >/dev/null 2>&1; then
        fail "$name:$lineno failed schema"
      fi
    else
      echo "$line" | jq type >/dev/null 2>&1 || fail "$name:$lineno invalid json"
    fi
  done < "$jsonl"
  if [ $EXIT_CODE -eq 0 ]; then ok "$name lines validated"; else warn "$name had validation errors"; fi
}

# ---------- validate metrics & config ----------
hdr "Validating experiment artifacts"
CFG="$EXP/config.json"
MS="$EXP/metrics_summary.json"
EJ="$EXP/events.jsonl"

[ -f "$CFG" ] && ok "config.json exists" || warn "config.json missing (will be created by flows)"

if [ -f "$MS" ]; then
  validate_json "$METRICS_SCHEMA" "$MS"
else
  warn "metrics_summary.json not found — run: python3 tools/metrics_aggregate.py \"$EXP\""
fi

if [ -f "$EJ" ]; then
  validate_jsonl "$EVENT_SCHEMA" "$EJ"
else
  warn "events.jsonl not found yet"
fi

# ---------- validate bus ----------
hdr "Validating bus queues"
[ -d "$BUS_DIR" ] && ok "bus/ exists" || warn "bus/ not found (will be created on first event)"
validate_jsonl "$EVENT_SCHEMA" "$BUS_EVENTS"
validate_jsonl "$CMD_SCHEMA" "$BUS_CMDS"

# ---------- quick status ----------
hdr "Experiment status"
if [ -f scripts/exp_status.sh ]; then
  scripts/exp_status.sh "$EXP" || true
else
  warn "status skipped (no scripts/exp_status.sh)"
fi

# ---------- summary ----------
hdr "Summary"
if [ $EXIT_CODE -eq 0 ]; then
  ok "Health OK"
else
  fail "Health has issues (exit $EXIT_CODE)"
fi

exit $EXIT_CODE
