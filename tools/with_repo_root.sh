#!/usr/bin/env bash
set -e
cd "$(cd "$(dirname "$0")/.." && pwd)"
exec "$@"
