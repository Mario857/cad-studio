#!/usr/bin/env bash
# Install the pinned Linux Bambu Studio (extracted AppImage, no FUSE) into ~/.cache/cad-studio/bambu-studio.
# Idempotent and safe to run concurrently (flock). macOS uses /Applications/BambuStudio.app instead.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
CACHE="${CAD_CACHE_DIR:-$HOME/.cache/cad-studio}"
DEST="$CACHE/bambu-studio"
APPRUN="$DEST/squashfs-root/AppRun"
mkdir -p "$CACHE"

[[ "$(uname -s)" == "Linux" ]] || { echo "install-slicer: Linux only"; exit 0; }
[[ "$(uname -m)" == "x86_64" ]] || { echo "install-slicer: Bambu Studio ships x86_64 Linux builds only"; exit 1; }

exec 9>"$CACHE/install-slicer.lock"
flock 9
[[ -x "$APPRUN" ]] && exit 0

toml() { sed -n "s/^$1 *= *\"\(.*\)\"/\1/p" "$REPO/config/printer.toml" | head -1; }
VERSION="$(toml linux_version)"
UBUNTU_MAJOR="$(. /etc/os-release 2>/dev/null; echo "${VERSION_ID%%.*}")"
if [[ "$UBUNTU_MAJOR" == "22" ]]; then ASSET="$(toml linux_asset_ubuntu22)"; else ASSET="$(toml linux_asset_ubuntu24)"; fi

if command -v apt-get >/dev/null; then
  SUDO=""; [[ "$(id -u)" -ne 0 ]] && SUDO="sudo"
  $SUDO apt-get update -qq || true
  $SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends \
    curl ca-certificates libgtk-3-0 libwebkit2gtk-4.1-0 libgl1 libegl1 libgles2 libosmesa6 \
    libglu1-mesa libsm6 libgomp1 fontconfig libsecret-1-0 libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 >/dev/null
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
echo "install-slicer: downloading Bambu Studio $VERSION ($ASSET)"
curl -fsSL -o "$TMP/bambu.AppImage" "https://github.com/bambulab/BambuStudio/releases/download/$VERSION/$ASSET"
chmod +x "$TMP/bambu.AppImage"
# Blank the AppImage magic in the ELF padding so it also runs under binfmt emulators (qemu/Rosetta).
printf '\x00\x00\x00' | dd of="$TMP/bambu.AppImage" bs=1 seek=8 conv=notrunc status=none
rm -rf "$DEST" && mkdir -p "$DEST"
(cd "$DEST" && "$TMP/bambu.AppImage" --appimage-extract >/dev/null)
echo "install-slicer: installed $APPRUN"
