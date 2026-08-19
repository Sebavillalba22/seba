---
name: tendencias
description: Usa esta skill cuando el usuario pregunte qué está funcionando en su nicho, "tendencias", "qué está rindiendo", "sobre qué publico", "ideas de contenido" — para Estacionline (noticias locales de Funes, Roldán, Puerto Timbúes y Santa Fe) y su comunidad. Escanea qué rinde y deja un reporte accionable en vault/outputs/tendencias.md.
---

# tendencias — qué está funcionando en el nicho

Una skill, un propósito: **detectar qué contenido rinde y convertirlo en
ideas concretas para Estacionline**.

## Cómo escanear (usar lo disponible)

1. **Lo propio primero**: con la API Graph
   (`jarvis-haz-lo-tuyo/instagram.json`), traer los últimos 15-25 posts de
   @estacionline (`/media?fields=like_count,comments_count,media_type,caption,timestamp`)
   y rankear: qué temas, formatos (carrusel/reel/foto) y horarios rindieron
   mejor esta semana vs. la anterior.
2. **El nicho**: si hay búsqueda web disponible, buscar qué está pasando en
   la zona (Funes, Roldán, Puerto Timbúes, Santa Fe) — obras, eventos,
   medidas municipales, clima extremo — y qué formatos están empujando los
   medios locales comparables.
3. Sin fuentes → analizar lo que el usuario pegue. No inventar datos de
   rendimiento.

## Salida obligatoria: `vault/outputs/tendencias.md`

Sobrescribir el archivo con el reporte nuevo (el anterior se archiva
agregándolo al final de `vault/raw/tendencias-archivo.md`):

```
# Tendencias — 2026-08-19

## Qué está rindiendo
- Carruseles de obras públicas: 2× interacciones vs. promedio
- Horario 19-21 h sigue siendo el mejor

## Ideas accionables (3-5)
1. Carrusel: avance de la obra de la ruta A012 (vecinos preguntan)
2. …
```

Máximo 5 ideas, cada una con el porqué en una línea. Esto alimenta a la
skill `plan` — no es un informe largo.

## Al correr (protocolo HUD)

En `vault/outputs/estado-skills.md`: al empezar, poner la línea de
`tendencias` en `corriendo`; al terminar, volver a `inactiva`, sumar 1 a
`hoy:`, poner `ultima: HH:MM` y actualizar `actualizado:`. Si
`actualizado:` era de otro día, resetear antes todos los `hoy:` a 0.

## Respuesta al usuario

Las 3 mejores ideas con su porqué, en 5 líneas o menos. Cerrar con
"¿Meto alguna en el plan de hoy?".
