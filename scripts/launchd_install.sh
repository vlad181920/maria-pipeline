#!/bin/zsh
set -euo pipefail

# === Config ===
LABEL="com.maria.earn.loop"
SLEEP="${1:-300}"          # інтервал у секундах (дефолт 300)
TARGET_PRICE="${2:-29}"    # цільова ціна (дефолт 29)

# === Paths ===
ROOT="$(pwd -P)"                       # абсолютний шлях репозиторію
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOGDIR="$ROOT/artifacts/earn/logs"
OUT="$LOGDIR/launchd.out"
ERR="$LOGDIR/launchd.err"

# Перевірки
[ -x "$ROOT/scripts/loop_cycle.sh" ] || { echo "ERR: scripts/loop_cycle.sh не знайдено або не виконуваний" >&2; exit 1; }

mkdir -p "$LOGDIR"
: > "$OUT" || true
: > "$ERR" || true

# Зняти існуючий
launchctl unload "$PLIST" 2>/dev/null || true
launchctl remove "$LABEL" 2>/dev/null || true

# Згенерувати plist
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>

  <key>StartInterval</key><integer>$SLEEP</integer>
  <key>WorkingDirectory</key><string>$ROOT</string>

  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>-lc</string>
    <string>scripts/loop_cycle.sh --sleep $SLEEP --target-price $TARGET_PRICE</string>
  </array>

  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>LANG</key><string>en_US.UTF-8</string>
    <key>LC_ALL</key><string>en_US.UTF-8</string>
  </dict>

  <key>RunAtLoad</key><true/>

  <key>StandardOutPath</key><string>$OUT</string>
  <key>StandardErrorPath</key><string>$ERR</string>
</dict></plist>
PL

# Завантажити і стартувати
launchctl load "$PLIST"
launchctl kickstart -k "gui/$(id -u)/$LABEL" 2>/dev/null || launchctl start "$LABEL"

echo "✓ installed $LABEL"
echo "WorkingDirectory: $ROOT"
echo "Sleep: $SLEEP  | Target price: $TARGET_PRICE"
echo "Logs:"
echo "  tail -n 100 \"$OUT\""
echo "  tail -n 100 \"$ERR\""
echo
launchctl list | grep "$LABEL" || true
