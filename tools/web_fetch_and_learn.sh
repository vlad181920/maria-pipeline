#!/usr/bin/env bash
set -e
PORT=$(cat artifacts/logs/web_learn.port 2>/dev/null || echo 8765)
url="$1"
title="${2:-$1}"
curl --noproxy 127.0.0.1,localhost -s -X POST "http://127.0.0.1:${PORT}/learn" -H "Content-Type: application/json" -d "{\"url\":\"$url\",\"title\":\"$title\"}"
