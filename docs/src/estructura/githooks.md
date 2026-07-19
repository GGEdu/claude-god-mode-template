# Directorio: `.githooks/`

Los **2 git hooks** del template. Se activan automáticamente en operaciones git para prevenir errores antes de que lleguen al repositorio.

> Se instalan con `git config core.hooksPath .githooks` (normalmente incluido en el onboarding de cada stack).

---

## `pre-commit`

**Se dispara:** En cada `git commit`, antes de que el commit se cree.  
**Bloquea el commit si:** Encuentra errores de linting o credenciales hardcodeadas.

### Flujo

```
git commit
    ↓
¿package.json? → Ejecutar Biome (linter/formatter Node.js)
¿pyproject.toml / requirements.txt? → Ejecutar Ruff (linter Python)
    ↓
Secrets scan: buscar patrones de credenciales en archivos staged
    ↓
¿Algún check falló? → Bloquear commit con mensaje de error
```

### Linters que ejecuta

| Condición | Linter | Comando |
|-----------|--------|---------|
| `package.json` existe | Biome | `npx biome check --apply .` |
| `pyproject.toml` o `requirements.txt` existe | Ruff | `ruff check . && ruff format .` |

### Patrones de secretos buscados

El hook escanea los archivos staged buscando:

| Patrón | Detecta |
|--------|---------|
| `ghp_[a-zA-Z0-9]{20,}` | GitHub Personal Access Token |
| `sk-[a-zA-Z0-9]{30,}` | API key de OpenAI u otros |
| `AKIA[A-Z0-9]{16}` | AWS Access Key ID |
| `api_key\s*=\s*['"]{20,}` | API keys genéricas en código |

Si encuentra algún patrón:

1. Bloquea el commit
2. Muestra el archivo y línea donde se encontró
3. Sugiere usar variables de entorno

### Ejemplo de salida bloqueada

```
❌ Posible credencial encontrada en src/config.ts:
   sk-proj-abc123xyz...

   Usa variables de entorno en su lugar.
   Si es un falso positivo, usa: git commit --no-verify
```

---

## `pre-push`

**Se dispara:** En cada `git push`, antes de enviar cambios al remoto.  
**Bloquea el push si:** Los tests fallan.

### Flujo

```
git push
    ↓
¿package.json con "test" script? → npm test
¿composer.json? → php artisan test --no-interaction
¿go.mod? → go test ./...
¿pyproject.toml / requirements.txt? → python -m pytest
    ↓
¿Tests fallaron? → Bloquear push
```

### Frameworks detectados

| Condición | Comando de test |
|-----------|----------------|
| `package.json` con script `"test"` | `npm test` |
| `composer.json` (Laravel) | `php artisan test --no-interaction` |
| `go.mod` | `go test ./...` |
| `pyproject.toml` o `requirements.txt` | `python -m pytest` |

Si no se detecta ningún runner, el hook deja pasar el push.

### Ejemplo de salida bloqueada

```
❌ Los tests fallaron. Push bloqueado.

   Corrige los tests antes de hacer push.
   Si necesitas forzar, usa: git push --no-verify
```

---

## `pre-push` con análisis IA via LiteLLM

Para proyectos que tengan **LiteLLM desplegado localmente**, el pre-push puede incluir análisis semántico de seguridad además de (o en lugar de) los tests. Esta variante es apropiada cuando:

- LiteLLM corre en el servidor (`localhost:4000` u otra URL LAN)
- No se quiere depender de APIs externas de IA ni de `ANTHROPIC_API_KEY` en CI/CD
- Se quiere análisis semántico (SQL injection, SSRF, JWT) que `bandit` no cubre

### Flujo

```
git push
    ↓
¿Hay diff en rutas vigiladas? (src/api/, src/data/, src/scraper/, src/ingestion/)
    │
    ├─ No → skip silencioso — push continúa
    │
    └─ Sí → POST LiteLLM /v1/chat/completions (timeout 30 s)
              │
              ├─ LiteLLM no responde → fail-open (push pasa, aviso en stderr)
              │
              ├─ CRITICAL detectado → bloquear push (exit 1)
              │
              └─ HIGH / MEDIUM → warning impreso, push pasa (exit 0)
```

### Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `LITELLM_URL` | `http://localhost:4000` | URL del servidor LiteLLM |
| `LITELLM_MODEL` | `cerebro-lite` | Alias del modelo a usar |

### Qué analiza el modelo

Solo hallazgos con >80% de confianza. El prompt cubre:

| Nº | Categoría | Ejemplo de hallazgo |
|----|-----------|---------------------|
| 1 | JWT sin `tenant_id` | Endpoint protegido que no extrae el tenant del token |
| 2 | SQL injection | Query asyncpg con f-string o concatenación |
| 3 | SSRF | URL de usuario pasada al scraper sin validación |
| 4 | Secrets hardcodeados | Token o clave literal en el diff |
| 5 | Outbox bypass | Notificación directa que salta `outbox_eventos` |
| 6 | Pydantic sin validación | Campo que llega a la DB sin validator |

Respuesta del modelo: una línea por hallazgo (`CRITICAL/HIGH/MEDIUM archivo:línea desc`) o `CLEAN`.

### Comportamiento fail-open

Si LiteLLM no responde (timeout, servicio caído, red no disponible):

```
⚠️  LiteLLM no disponible (...) — push continúa sin análisis
```

El push **no se bloquea**. La infraestructura caída no paraliza el flujo de trabajo.

### Separación con GitHub Actions CI

El análisis de IA corre en el hook local (donde LiteLLM es accesible). GitHub Actions ejecuta solo análisis estático determinista — sin API keys:

```yaml
# .github/workflows/ci.yml — sin IA, sin secrets Anthropic
- run: ruff check src/
- run: mypy src/ --ignore-missing-imports
- run: bandit -r src/ -ll     # solo MEDIUM y HIGH
- run: pip-audit
```

Esta separación permite que el CI/CD funcione en runners externos (GitHub, GitLab) sin acceso a la LAN privada donde vive LiteLLM.

---

## Instalación

```bash
git config core.hooksPath .githooks
```

Esto le dice a git que use `.githooks/` en lugar del directorio estándar `.git/hooks/`. No se copian archivos — git los lee directamente desde el directorio del proyecto.

## Bypass (casos de emergencia)

```bash
git commit --no-verify   # Salta pre-commit
git push --no-verify     # Salta pre-push
```

Solo usar en emergencias documentadas. Los hooks existen para proteger el repositorio.
