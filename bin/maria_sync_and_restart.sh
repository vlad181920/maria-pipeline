#!/usr/bin/env bash
set -euo pipefail
SRC_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NEW_ROOT="${1:-$HOME/maria}"
mkdir -p "$NEW_ROOT" "$NEW_ROOT/artifacts/logs" "$NEW_ROOT/artifacts/stats" "$HOME/Library/LaunchAgents"
rsync -a --delete "$SRC_ROOT"/ "$NEW_ROOT"/
chmod +x "$NEW_ROOT/bin/maria_start.sh" "$NEW_ROOT/bin/maria_daily.sh" 2>/dev/null || true
PL1="$HOME/Library/LaunchAgents/com.maria.runforever.plist"
PL2="$HOME/Library/LaunchAgents/com.maria.kpidaily.plist"
cat > "$PL1" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>com.maria.runforever</string>
<key>ProgramArguments</key><array><string>/bin/bash</string><string>-lc</string><string>$NEW_ROOT/bin/maria_start.sh</string></array>
<key>WorkingDirectory</key><string>$NEW_ROOT</string>
<key>RunAtLoad</key><true/>
<key>KeepAlive</key><true/>
<key>EnvironmentVariables</key><dict><key>PERIOD</key><string>120</string></dict>
<key>StandardOutPath</key><string>$NEW_ROOT/artifacts/logs/launchd_runforever.out</string>
<key>StandardErrorPath</key><string>$NEW_ROOT/artifacts/logs/launchd_runforever.err</string>
</dict></plist>
PL
cat > "$PL2" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>com.maria.kpidaily</string>
<key>ProgramArguments</key><array><string>/bin/bash</string><string>-lc</string><string>$NEW_ROOT/bin/maria_daily.sh</string></array>
<key>StartCalendarInterval</key><dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
<key>RunAtLoad</key><false/>
<key>StandardOutPath</key><string>$NEW_ROOT/artifacts/logs/launchd_kpidaily.out</string>
<key>StandardErrorPath</key><string>$NEW_ROOT/artifacts/logs/launchd_kpidaily.err</string>
</dict></plist>
PL
launchctl unload "$PL1" >/dev/null 2>&1 || true
launchctl unload "$PL2" >/dev/null 2>&1 || true
launchctl load -w "$PL1" >/dev/null 2>&1 || true
launchctl load -w "$PL2" >/dev/null 2>&1 || true
launchctl kickstart -k "gui/$(id -u)/com.maria.runforever" >/dev/null 2>&1 || true
echo "$NEW_ROOT"
