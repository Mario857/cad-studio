#!/usr/bin/env bash
# Simulate a fresh Claude Code cloud session (x86_64 Ubuntu 24.04) in Docker: setup + full check.
# Usage: scripts/test-cloud-env.sh [model-name]   (default: phone-stand)
set -euo pipefail
cd "$(dirname "$0")/.."
MODEL="${1:-phone-stand}"
NAME="cad-studio-cloud-test"
docker rm -f "$NAME" >/dev/null 2>&1 || true

docker run --rm --name "$NAME" --platform linux/amd64 -e MODEL="$MODEL" -v "$PWD":/src:ro ubuntu:24.04 bash -c '
set -euo pipefail
apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3 python3-pip curl git >/dev/null
mkdir /work && cd /src && tar --exclude=.venv --exclude="models/*/out" -cf - . | tar -xf - -C /work && cd /work
echo "== setup.sh"; time bash scripts/setup.sh
echo "== waiting for slicer install"; sleep 2
flock "$HOME/.cache/cad-studio/install-slicer.lock" true; cat /tmp/cad-install-slicer.log
echo "== doctor"; ./cad doctor
echo "== check"; time ./cad check "$MODEL"
'
