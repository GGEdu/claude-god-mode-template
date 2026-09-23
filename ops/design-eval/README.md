# Medición de homogeneidad de diseño

Tres encargos fijos (`BRIEFS.md`) × 2 ejecuciones del agente `ui-engineer`, cada una en su
directorio con un `index.html`. `measure.py <dir>` hace capturas (desktop/móvil, Chrome
headless) y mide fuentes, colores dominantes, patrones vetados y hallazgos del detector de
impeccable. Repetir antes de fusionar cualquier cambio en `ui-engineer` o en las skills de diseño.

## 2026-09-23 — antes y después de impeccable

| | Antes | Después |
|---|---|---|
| Hallazgos del detector | 82 (37 de bajo contraste) | 10 (8 falsos positivos en modo oscuro según el agente) |
| Fuente más repetida | Inter en 5/6 | **Archivo en 5/6** |
| Fuentes sobreusadas (lista de impeccable) | 6/6 muestras | 1/6 (Roboto Mono) |
| Pares casi idénticos | los 3 (mismo nombre inventado incluso) | solo las landings (ambas «registro municipal», verde + rojo sello) |
| Coste por muestra | ~60k tokens, 3–7 min | ~220k tokens, 12–18 min |

Lecturas: los dashboards y formularios pasan de clónicos a claramente distintos. Queda
convergencia en las landings (mismo mundo de «trámite oficial») y **Archivo emerge como el
nuevo default**: no está en la lista de fuentes vetadas de impeccable. Vigilarlo en la
próxima medición antes de añadir reglas propias (n=6 no basta).
