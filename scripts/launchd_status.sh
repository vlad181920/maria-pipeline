#!/bin/zsh
set -euo pipefail

LABEL="${1:-com.maria.earn.loop}"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

red()  { print -r -- "\e[31m$*\e[0m"; }
grn()  { print -r -- "\e[32m$*\e[0m"; }
ylw()  { print -r -- "\e[33m$*\e[0m"; }
hdr()  { print -r -- "\n== $* =="; }

if [[ ! -f "$PLIST" ]]; then
  red "plist not found: $PLIST"
  exit 1
fi

# -- прочитати значення з plist (PlistBuddy більш стабільний за defaults)
pb="/usr/libexec/PlistBuddy"
get_plist() {
  local key="$1"
  "$pb" -c "Print :$key" "$PLIST" 2>/dev/null || true
}

WD="$(get_plist WorkingDirectory)"
[[ -z "${WD:-}" ]] && WD="$(pwd -P)"
CMD0="$(get_plist ProgramArguments:0)"
CMD1="$(get_plist ProgramArguments:1)"
CMD2="$(get_plist ProgramArguments:2)"
INTERVAL="$(get_plist StartInterval)"
OUT="$(get_plist StandardOutPath)"
ERR="$(get_plist StandardErrorPath)"
PATH_ENV="$(get_plist EnvironmentVariables:PATH)"

hdr "Agent"
echo "Label:          $LABEL"
echo "Plist:          $PLIST"
echo "WorkingDirectory: $WD"
echo "StartInterval:  ${INTERVAL:-n/a}"
echo "PATH (env):     ${PATH_ENV:-n/a}"
echo "ProgramArguments:"
echo "  0: ${CMD0:-n/a}"
echo "  1: ${CMD1:-n/a}"
echo "  2: ${CMD2:-n/a}"

hdr "launchctl state"
if launchctl print "gui/$(id -u)/$LABEL" >/tmp/_launch_print.txt 2>/dev/null; then
  grn "launchctl print: OK"
  sed -n '1,80p' /tmp/_launch_print.txt
else
  ylw "launchctl print not available, showing 'launchctl list | grep'"
  launchctl list | grep -F "$LABEL" || true
fi

hdr "Filesystem checks"
if [[ -d "$WD" ]]; then
  grn "WD exists: $WD"
else
  red "WD missing: $WD"
fi

# Спроба знайти скрипт
SCRIPT_PATH=""
if [[ -x "$WD/scripts/loop_cycle.sh" ]]; then
  SCRIPT_PATH="$WD/scripts/loop_cycle.sh"
elif [[ -x "$WD/loop_cycle.sh" ]]; then
  SCRIPT_PATH="$WD/loop_cycle.sh"
fi
if [[ -n "$SCRIPT_PATH" ]]; then
  grn "script OK: $SCRIPT_PATH"
  echo -n "perm: "; stat -f "%Sp %N" "$SCRIPT_PATH" 2>/dev/null || true
else
  red "script not found/executable under $WD (expected scripts/loop_cycle.sh)"
fi

hdr "Logs"
[[ -n "${OUT:-}" ]] && echo "stdout: $OUT" || echo "stdout: (not set)"
[[ -n "${ERR:-}" ]] && echo "stderr: $ERR" || echo "stderr: (not set)"

if [[ -n "${OUT:-}" && -f "$OUT" ]]; then
  grn "-- tail stdout --"
  tail -n 50 "$OUT" || true
else
  ylw "stdout file not found"
fi

if [[ -n "${ERR:-}" && -f "$ERR" ]]; then
  grn "-- tail stderr --"
  tail -n 50 "$ERR" || true
else
  ylw "stderr file not found"
fi

hdr "Quick tips"
echo "• Reload:   launchctl unload \"$PLIST\" && launchctl load \"$PLIST\""
echo "• Start:    launchctl kickstart -k \"gui/\$(id -u)/$LABEL\""
echo "• Remove:   launchctl unload \"$PLIST\"; launchctl remove \"$LABEL\""
echo "• Logs:     tail -f \"${OUT:-/path/to/out}\" \"${ERR:-/path/to/err}\""

grn "\nDone."
