#!/usr/bin/env bash
# SessionStart hook (and manual setup). Its stdout lands in Claude's context, so it prints one line.
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv >/dev/null; then
  { python3 -m pip install -q --user uv 2>/dev/null || python3 -m pip install -q --break-system-packages uv; } >/dev/null 2>&1 \
    || curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1
fi
uv sync --frozen -q >/dev/null 2>&1 || uv sync --frozen

slicer="ready"
if [[ "$(uname -s)" == "Linux" && ! -x "${CAD_CACHE_DIR:-$HOME/.cache/cad-studio}/bambu-studio/squashfs-root/AppRun" ]]; then
  # ~250 MB download: start it now so it is done by the time the first model is ready to slice.
  nohup bash scripts/install-slicer.sh >/tmp/cad-install-slicer.log 2>&1 &
  slicer="installing in background"
fi
echo "cad-studio ready: use ./cad (slicer $slicer). Follow CLAUDE.md."
