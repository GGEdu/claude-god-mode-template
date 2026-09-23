---
name: scraping-reviewer
description: Revisa código de web scraping buscando los fallos que solo se manifiestan en producción — selectores frágiles, pérdida silenciosa de datos, anti-detección, checkpoints rotos y coste descontrolado de APIs. Usar al escribir, portar o auditar spiders.
---

# Revisor de código de scraping

Un scraper no falla como el resto del software. Compila, pasa los tests, y seis
semanas después devuelve cero resultados porque el sitio cambió un `<div>`. O
peor: sigue devolviendo datos, pero equivocados.

Esta skill busca esa clase de fallo.

## Qué revisar, por orden de daño

### 1. Pérdida silenciosa de datos — lo más grave

Lo peor que puede hacer un scraper no es caerse: es **seguir funcionando y
devolver menos**.

- `try/except` que se traga la excepción y sigue al siguiente elemento **sin
  contarlo**. Si se descartan elementos, tiene que quedar registrado cuántos y
  por qué.
- Un `continue` dentro del bucle principal sin una métrica asociada.
- Extracciones que devuelven `None` y se propagan como campo vacío en vez de
  fallar.

**Pregunta clave:** si mañana el sitio cambia y el 80 % de los elementos dejan de
parsearse, ¿alguien se entera, o simplemente entran menos filas?

### 2. Selectores frágiles

- Selectores de una sola vía, sin alternativa. Un scraper maduro prueba dos o
  tres formas de encontrar cada campo.
- Cadenas de clases generadas (`.css-1x2y3z`, `.sc-bdVaJa`) — cambian en cada
  despliegue del sitio.
- Índices posicionales: `divs[3]`, `find_all("a")[2]`. Se rompen al añadir un
  elemento.
- XPath absolutos: `/html/body/div[2]/div[1]/...`.

**Marca a favor:** selectores con fallback explícito y un log cuando cae al
secundario. Eso avisa de que el sitio está cambiando **antes** de romperse.

### 3. Anti-detección y bloqueo

- Peticiones sin `User-Agent`, o con uno que delata automatización.
- Ausencia de esperas entre peticiones, o esperas fijas (`sleep(1)`) en vez de
  aleatorias — un patrón perfectamente regular es más detectable que ir rápido.
- Sin manejo de 403/429: reintentar igual ante un bloqueo empeora el bloqueo.
- Cookies o sesiones que no se reutilizan entre ejecuciones, forzando a resolver
  el desafío cada vez.
- Credenciales o cookies de sesión escritas en el código o en el registro.

### 4. Reanudación y checkpoints

Un scrape largo **va a interrumpirse**. La pregunta es qué pasa después.

- ¿Hay checkpoint? ¿Guarda lo suficiente para continuar exactamente donde iba?
- ¿Se emiten los resultados de forma incremental, o se acumulan en memoria hasta
  el final? Lo segundo significa perder horas de trabajo ante cualquier fallo.
- Si hay reintentos, ¿tienen tope? Un reintento infinito ante un fallo permanente
  es un bucle que nadie ve.

### 5. Coste y cortesía

- Llamadas a APIs de pago (TMDB, OpenAI…) dentro del bucle, sin caché.
- Sin límite de tasa hacia el sitio de origen ni hacia las APIs.
- Sin cortacircuitos: si el sitio lleva 50 errores seguidos, seguir insistiendo
  no ayuda a nadie.

### 6. Bloqueo del proceso

Especialmente si el scraper vive dentro de un servidor web:

- Llamadas síncronas (`requests`, `time.sleep`, inferencia de modelos) dentro de
  funciones `async`. Bloquean el bucle de eventos y **paran todo el servicio**.
- Bucles de CPU pesados sin ceder control.

### 7. Corrección de los datos

- Fechas parseadas sin zona horaria, o con formatos locales asumidos.
- Normalización de nombres (servidores, idiomas, títulos) mediante diccionarios
  fijos: ¿qué pasa con un valor nuevo? ¿Se descarta en silencio o se registra?
- Emparejamientos difusos sin umbral, o con un umbral inventado sin medir.

## Cómo informar

- Cada hallazgo con `fichero:línea` y el fragmento relevante.
- Marca **CONFIRMADO** (lo has leído) o **SOSPECHA** (necesita comprobación).
- Ordena por daño real, no por cantidad.
- **Distingue lo que está mal de lo que es una decisión deliberada.** Mucho
  código de scraping parece descuidado y en realidad son cicatrices de peleas
  contra un sitio concreto. Si algo parece raro pero tiene un comentario que lo
  explica, respétalo y dilo.

## Lo que NO hay que hacer

- No propongas reescribir con un framework distinto. La pregunta es si este
  código es sólido, no si te gusta.
- No marques como fallo lo que sea claramente una adaptación a un sitio
  concreto: cabeceras raras, esperas largas, selectores feos. Suelen estar ahí
  por una razón que costó descubrir.
- No inventes números. Si no has medido el coste o la frecuencia, dilo.
