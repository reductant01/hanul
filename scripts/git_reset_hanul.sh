#!/bin/bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
git fetch origin
git checkout hanul
git reset --hard origin/hanul
git clean -fd
chmod +x scripts/hanul/*.sh
[ -f run_hanul_nuc.sh ] && chmod +x run_hanul_nuc.sh run_hanul_control_pc.sh run_hanul_webots.sh 2>/dev/null || true
echo "hanul 브랜치로 리셋 완료."
