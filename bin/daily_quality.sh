#!/usr/bin/env bash
set -euo pipefail
bash "$MARIA_HOME/bin/kb_report.sh"
bash "$MARIA_HOME/bin/make_qa.sh"
