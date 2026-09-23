#!/usr/bin/env bash
# Instala el motor de impeccable en la caché que usa su launcher
# (~/.impeccable/bin/<versión>/impeccable), verificado contra la huella fijada en git.
# El launcher solo verifica contra un .sha256 del mismo origen; esto cierra ese hueco.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/../skills/impeccable" && pwd)"
VERSION="$(tr -d '[:space:]' < "$SKILL_DIR/scripts/VERSION")"
ASSET="impeccable-linux-x64"
EXPECTED="$(awk -v a="$ASSET" '$2==a {print $1}' "$SKILL_DIR/ENGINE.sha256")"
DEST="${IMPECCABLE_HOME:-$HOME/.impeccable}/bin/$VERSION/impeccable"

if [ "$(uname -s)-$(uname -m)" != "Linux-x86_64" ]; then
  echo "  ⚠️  impeccable: solo hay huella fijada para linux-x64; instala el motor a mano (skills/impeccable/UPSTREAM.md)" >&2
  exit 0
fi
if [ -z "$EXPECTED" ]; then
  echo "  ❌ impeccable: no hay huella para $ASSET en ENGINE.sha256" >&2
  exit 1
fi
if [ -x "$DEST" ] && [ "$(sha256sum "$DEST" | cut -d' ' -f1)" = "$EXPECTED" ]; then
  echo "  ✅ Motor impeccable $VERSION ya instalado y verificado"
  exit 0
fi

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
curl -fsSL --retry 2 -o "$tmp" \
  "https://github.com/pbakaus/impeccable/releases/download/engine-v$VERSION/$ASSET"
ACTUAL="$(sha256sum "$tmp" | cut -d' ' -f1)"
if [ "$ACTUAL" != "$EXPECTED" ]; then
  echo "  ❌ impeccable: la huella del motor $VERSION no coincide con la fijada" >&2
  echo "     esperada $EXPECTED" >&2
  echo "     obtenida $ACTUAL" >&2
  exit 1
fi
install -D -m 755 "$tmp" "$DEST"
echo "  ✅ Motor impeccable $VERSION instalado y verificado ($DEST)"
