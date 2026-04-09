# Analizar un proyecto externo

::: info Prerequisito: instalación completada
Esta funcionalidad requiere que el template esté instalado y configurado. Si aún no lo has hecho, sigue la [guía de instalación](/instalacion) primero.
:::

Puedes clonar cualquier proyecto de Git dentro de este template para usar todos los agentes, skills, MCPs y herramientas disponibles sin configuración adicional.

## Por qué funciona

Claude Code carga la configuración desde el directorio donde está corriendo — en este caso, la raíz del template. Cualquier subdirectorio (incluido `projects/`) hereda automáticamente:

- Todos los agentes (`agents/`)
- Todos los skills y slash commands (`.claude/commands/`)
- Todos los MCP servers configurados (`.mcp.json`)
- Las reglas de código (`.claude/rules/`)

No hace falta abrir una sesión nueva ni cambiar de directorio.

## Flujo estándar

### 1. Cargar el proyecto

```bash
make load-project URL=https://github.com/usuario/repo.git
# → Clona en projects/<nombre>/
```

### 2. Ejecutar el análisis completo

```bash
make analyze-project NAME=<nombre>
```

Este comando muestra el prompt exacto para pedirle a Claude que ejecute las **3 revisiones en paralelo** y genere el informe.

### 3. Resultado

Se genera automáticamente `projects/<nombre>/REPORT.md` con:

- Análisis general — stack, arquitectura, puntos de mejora
- Revisión de seguridad — vulnerabilidades OWASP Top 10
- Revisión de código — bugs, anti-patrones, deuda técnica
- Roadmap de fixes priorizado (CRITICAL → HIGH → MEDIUM → LOW)

---

## El análisis completo en detalle

Cuando se ejecuta `make analyze-project`, Claude lanza **3 agentes en paralelo**:

| Agente | Qué revisa |
| --- | --- |
| **Explore (análisis general)** | Stack, arquitectura, patrones, testing, configuración |
| **security-reviewer** | OWASP Top 10, auth, CSRF, XSS, exposición de datos, dependencias |
| **code-reviewer** | Bugs, anti-patrones React, race conditions, accesibilidad, dead code |

Los resultados se consolidan en un único `REPORT.md` con secciones por severidad (CRITICAL, HIGH, MEDIUM, LOW) y un roadmap de fixes por fases.

---

## Prompts adicionales

Una vez cargado el proyecto, también puedes pedir:

**Propuesta de mejoras con TDD:**

```
Para el proyecto en projects/<nombre>, propón cómo implementar [feature]
siguiendo el flujo TDD del agente tdd-guide.
```

**Análisis de arquitectura en profundidad:**

```
Usa el agente architect para evaluar la arquitectura actual de projects/<nombre>
y proponer una refactorización.
```

**Implementar un fix específico:**

```
Implementa el fix CODE-4 del REPORT.md en projects/<nombre>.
```

---

## Limpiar cuando termines

Los proyectos en `projects/` son temporales — nunca se commitean al template.

```bash
rm -rf projects/<nombre>
```

## Ver proyectos cargados

```bash
ls projects/
```
