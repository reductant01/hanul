#!/bin/bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin
git checkout hanul
git reset --hard origin/hanul
git clean -fd
chmod +x scripts/hanul/*.sh
[ -f hanul_nuc.sh ] && chmod +x hanul_nuc.sh hanul_control_pc.sh hanul_webots.sh 2>/dev/null || true
echo "hanul 브랜치로 리셋 완료."
