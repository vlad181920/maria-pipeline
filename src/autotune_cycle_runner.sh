#!/bin/bash
set -Eeuo pipefail

ROOT="$HOME/Desktop/Марія"
LOG="$ROOT/artifacts/logs/autotune_cycle.out"

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }

echo "[autocycle] $(ts) === autotune cycle start ===" | tee -a "$LOG"

# Крок 1. Згенерувати нову мутовану версію коду
echo "[autocycle] $(ts) running autonomous_code_evolution.py" | tee -a "$LOG"
python3 "$ROOT/src/autonomous_code_evolution.py" 2>&1 | tee -a "$LOG"

# Крок 2. Інтегрувати її як кандидат у гілку autotune/*
echo "[autocycle] $(ts) running autotune_integrator.py" | tee -a "$LOG"
python3 "$ROOT/src/autotune_integrator.py" 2>&1 | tee -a "$LOG"

echo "[autocycle] $(ts) === autotune cycle end ===" | tee -a "$LOG"
