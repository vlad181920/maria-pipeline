#!/bin/zsh
set -euo pipefail

# Defaults
LABEL="com.maria.earn.loop"
INTERVAL=300
WORKDIR="$HOME/maria"   # змінюй на $HOME/Desktop/Марія якщо треба
TARGET_PRICE=29
OUT_LOG="$WORKDIR/artifacts/earn/logs/launchd.out"
ERR_LOG="$WORKDIR/artifacts/earn/logs/launchd.err"

usage() {
  cat <<USAGE
Usage: $0 [--label LABEL] [--interval SECONDS] [--workdir PATH] [--target-price N]
  --label         launchd Label (default: $LABEL)
  --interval      StartInterval seconds (default: $INTERVAL)
  --workdir       WorkingDirectory (default: $WORKDIR)
  --target-price  Price to pass to loop_cycle.sh (default: $TARGET_PRICE)
USAGE
}

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --label) LABEL="$2"; shift 2;;
    --interval) INTERVAL="$2"; shift 2;;
    --workdir) WORKDIR="$2"; shift 2;;
    --target-price) TARGET_PRICE="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
SCRIPT="$WORKDIR/scripts/loop_cycle.sh"

red() { print -r -- "\e[31m$*\e[0m"; }
grn() { print -r -- "\e[32m$*\e[0m"; }
ylw() { print -r -- "\e[33m$*\e[0m"; }
hdr() { print -r -- "\n== $* =="; }

hdr "Pre-flight checks"
if [[ ! -d "$WORKDIR" ]]; then
  red "WorkingDirectory not found: $WORKDIR"
  exit 1
fi
if [[ ! -x "$SCRIPT" ]]; then
  ylw "Script not executable: $SCRIPT (fixing perms)"
  chmod +x "$SCRIPT" || { red "Failed to chmod +x $SCRIPT"; exit 1; }
fi

mkdir -p "$WORKDIR/artifacts/earn/logs"
OUT_LOG="$WORKDIR/artifacts/earn/logs/launchd.out"
ERR_LOG="$WORKDIR/artifacts/earn/logs/launchd.err"

hdr "Writing plist: $PLIST"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>

  <key>StartInterval</key><integer>$INTERVAL</integer>
  <key>WorkingDirectory</key><string>$WORKDIR</string>

  <key>ProgramArguments</key>
  <array>
    <string>$SCRIPT</string>
    <string>--sleep</string><string>$INTERVAL</string>
    <string>--target-price</string><string>$TARGET_PRICE</string>
  </array>

  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>LANG</key><string>en_US.UTF-8</string>
    <key>LC_ALL</key><string>en_US.UTF-8</string>
  </dict>

  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$OUT_LOG</string>
  <key>StandardErrorPath</key><string>$ERR_LOG</string>
</dict></plist>
PL

hdr "Reloading agent"
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
grn "loaded: $PLIST"

hdr "Kickstart (run now)"
launchctl kickstart -k "gui/$(id -u)/$LABEL" 2>/dev/null || launchctl start "$LABEL" || true

hdr "launchctl list"
launchctl list | grep -F "$LABEL" || ylw "not in list yet (may start on schedule)"

hdr "Tailing logs"
[[ -f "$OUT_LOG" ]] && { grn "-- stdout tail --"; tail -n 50 "$OUT_LOG" || true; } || ylw "no stdout yet: $OUT_LOG"
[[ -f "$ERR_LOG" ]] && { grn "-- stderr tail --"; tail -n 50 "$ERR_LOG" || true; } || ylw "no stderr yet: $ERR_LOG"

hdr "Tips"
echo "• To check detailed state: launchctl print gui/\$(id -u)/$LABEL"
echo "• To remove: launchctl unload \"$PLIST\"; launchctl remove \"$LABEL\""
echo "• To run once manually: (cd \"$WORKDIR\" && \"$SCRIPT\" --sleep 0 --target-price $TARGET_PRICE)"

grn "\nDone."
