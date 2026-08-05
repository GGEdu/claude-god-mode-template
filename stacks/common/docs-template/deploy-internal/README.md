# Docs internos (VitePress → nginx)

Sirve los docs del proyecto **solo en la LAN/Tailscale**, sin exponerlos a
internet.

## ⚠️ No uses GitHub Pages en repos privados/homelab

En cuentas personales/Free, **GitHub Pages es PÚBLICO aunque el repo sea
privado** (las Pages privadas requieren GitHub Enterprise). Publicar ahí docs con
IPs internas, topología, endpoints o diseño de auth = fuga de reconocimiento sin
autenticación. Por eso el scaffold **no** incluye workflow de Pages; usa esto.

## Desplegar

En un host docker sin IP pública (p.ej. un CT del homelab):

```bash
# copia docs/ al host (excluye node_modules) y:
cd docs/deploy-internal
docker compose up -d --build
# → http://<host-interno>:8095/   (LAN/Tailscale)
```

## Notas

- `base: '/'` en `.vitepress/config.mts` (sirve en raíz interna).
- El build instala `git` (VitePress lo usa para `lastUpdated`).
- nginx resuelve cleanUrls y expone `/healthz` para el healthcheck.
