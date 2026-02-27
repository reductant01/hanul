#!/bin/bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin
git checkout hanul
git reset --hard origin/hanul
git clean -fd
echo "hanul 브랜치로 리셋 완료."
