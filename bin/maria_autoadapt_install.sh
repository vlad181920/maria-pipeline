#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PL="$HOME/Library/LaunchAgents/com.maria.autoadapt.plist"
mkdir -p "$HOME/Library/LaunchAgents"
mkdir -p "$ROOT/artifacts/logs"
cat > "$PL" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>com.maria.autoadapt</string>
<key>ProgramArguments</key><array><string>/bin/bash</string><string>-lc</string><string>$ROOT/bin/maria_autoadapt_start.sh</string></array>
<key>WorkingDirectory</key><string>$ROOT</string>
<key>RunAtLoad</key><true/>
<key>KeepAlive</key><true/>
<key>EnvironmentVariables</key><dict><key>BASE_SLEEP</key><string>90</string><key>MIN_BATCH</key><string>1</string></dict>
<key>StandardOutPath</key><string>$ROOT/artifacts/logs/launchd_autoadapt.out</string>
<key>StandardErrorPath</key><string>$ROOT/artifacts/logs/launchd_autoadapt.err</string>
</dict></plist>
PL
launchctl unload "$PL" >/dev/null 2>&1 || true
launchctl load -w "$PL"
launchctl kickstart -k "gui/$(id -u)/com.maria.autoadapt" >/dev/null 2>&1 || true
printf "%s\n" "$PL"
