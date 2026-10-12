#!/usr/bin/env bash
# Retained runtime, fresh temporary profile for each run.
set -euo pipefail
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
install_dir="${ETUX_FREECAD_INSTALL_DIR:-/workspace/.local/freecad/1.1.3}"
runtime="$install_dir/squashfs-root"
test -x "$runtime/AppRun"
profile="$(mktemp -d /tmp/etux-freecad113.XXXXXX)"
trap 'rm -rf "$profile"' EXIT
mkdir -p "$profile/cache" "$profile/config" "$profile/data"
export XDG_CACHE_HOME="$profile/cache"
export XDG_CONFIG_HOME="$profile/config"
export XDG_DATA_HOME="$profile/data"
# The Python entry point resets AppRun's xcb setting before Qt initialization.
"$runtime/AppRun" python "$repo_dir/tools/check_freecad_runtime.py" \
    --expect-version 1.1.3 --lib-dir "$runtime/usr/lib" --ext-dir "$runtime/usr/Ext" "$@"
