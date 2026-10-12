#!/usr/bin/env bash
# Official x86_64 AppImage, outside the checkout; no apt or system Python changes.
set -euo pipefail
if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
    echo 'This installer supports Linux x86_64 only.' >&2
    exit 1
fi
install_dir="${ETUX_FREECAD_INSTALL_DIR:-/workspace/.local/freecad/1.1.3}"
if [[ "$install_dir" != /* ]]; then
    echo 'ETUX_FREECAD_INSTALL_DIR must be an absolute path.' >&2
    exit 1
fi
asset='FreeCAD_1.1.3-Linux-x86_64-py311.AppImage'
expected_sha='3a853eb69ee595f779f2255dbf80a765926981d8ff68903cefee4dfb03a8f5ef'
url="https://github.com/FreeCAD/FreeCAD/releases/download/1.1.3/$asset"
mkdir -p "$install_dir"
verify() {
    printf '%s  %s\n' "$expected_sha" "$1" | sha256sum --check --status
}
if [[ ! -f "$install_dir/$asset" ]]; then
    curl --fail --location --retry 2 --connect-timeout 20 --max-time 600 \
        --output "$install_dir/$asset.download" "$url"
    verify "$install_dir/$asset.download"
    mv "$install_dir/$asset.download" "$install_dir/$asset"
fi
verify "$install_dir/$asset" || { echo 'AppImage checksum mismatch; refusing execution.' >&2; exit 1; }
chmod +x "$install_dir/$asset"
runtime="$install_dir/squashfs-root"
if [[ -d "$runtime" ]]; then
    if [[ ! -f "$runtime/.etux-appimage-sha256" ]] || \
       [[ "$(cat "$runtime/.etux-appimage-sha256")" != "$expected_sha" ]]; then
        echo 'Existing extraction is not managed by this installer; preserve and inspect it first.' >&2
        exit 1
    fi
else
    staging="$(mktemp -d "$install_dir/.extract.XXXXXX")"
    trap 'rm -rf "$staging"' EXIT
    (cd "$staging"; "$install_dir/$asset" --appimage-extract > extraction.log)
    printf '%s\n' "$expected_sha" > "$staging/squashfs-root/.etux-appimage-sha256"
    mv "$staging/squashfs-root" "$runtime"
fi
test -x "$runtime/AppRun"
test -x "$runtime/usr/bin/python"
printf 'FREECAD113_RUNTIME=%s\n' "$runtime"
