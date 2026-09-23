# impeccable — procedencia y actualización

Copia **verbatim** de `pbakaus/impeccable` (Apache-2.0, ver `LICENSE` y `NOTICE.md`),
directorio `.claude/skills/impeccable/`. No editar estos ficheros: cualquier ajuste
nuestro va en `agents/ui-engineer.md`, no aquí, para que la actualización sea un `cp -r`.

| Campo | Valor |
|---|---|
| Commit upstream | `e0881d2de397d5e9761d7b35ff5017d8f5ebf69b` (2026-09-22) |
| Skill | 4.3.1 (`SKILL.md` frontmatter) |
| Motor | `engine-v0.1.5` (`scripts/VERSION`) |
| Huella motor linux-x64 | `ENGINE.sha256` — coincide con el `.sha256` del release **y** con el `digest` que GitHub calcula al subir el asset |

## Por qué la huella fijada

El launcher (`scripts/impeccable`) descarga el binario de GitHub Releases y lo verifica
contra un `.sha256` servido desde el mismo origen: protege de descargas corruptas, no de
un release comprometido. `ops/install-impeccable-engine.sh` (lo llama `make install`)
descarga el motor y lo compara con `ENGINE.sha256`, que está en git; si no coincide,
no instala. El launcher confía después en la caché `~/.impeccable/bin/<versión>/`.

## Red y privacidad (verificado en `crates/context/src/seed_text.rs`)

- `concept-seed`: un GET a `https://impeccable.style/api/roll` con scope, modo, clave
  aleatoria de 8 hex y contador de re-roll. No envía ficheros, prompts ni código.
- Ping de telemetría anónimo tras elegir dirección y comprobación de actualizaciones:
  desactivados con `IMPECCABLE_NO_TELEMETRY=1` e `IMPECCABLE_NO_UPDATE_CHECK=1`
  (variables en `env` de `~/.claude/settings.json`).

## Actualizar

1. `git clone --depth 1 https://github.com/pbakaus/impeccable /tmp/imp`
2. `rm -rf skills/impeccable/{SKILL.md,reference,scripts} && cp -r /tmp/imp/.claude/skills/impeccable/* skills/impeccable/`
3. Si cambió `scripts/VERSION`: descargar `impeccable-linux-x64` del tag `engine-v<versión>`,
   comprobar que su sha256 coincide con el `.sha256` y con
   `gh api repos/pbakaus/impeccable/releases/tags/engine-v<versión> --jq '.assets[]|select(.name=="impeccable-linux-x64")|.digest'`,
   y solo entonces actualizar `ENGINE.sha256`.
4. Actualizar la tabla de arriba y repetir la medición de `ops/design-eval/` antes de fusionar.
