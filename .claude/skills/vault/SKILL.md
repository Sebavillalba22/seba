---
name: vault
description: Usa esta skill cuando el usuario quiera guardar o recuperar memoria — "guardá esto", "acordate de", "anotá", "buscá en el vault", "qué sabemos de X", "qué hicimos ayer" — o cuando otra tarea produzca algo que deba quedar registrado. Lee y escribe la memoria del sistema en vault/ (raw/, wiki/, outputs/) siguiendo la regla del vault.
---

# vault — la memoria (leer y escribir)

Una skill, un propósito: **que nada se pierda y todo se pueda encontrar**.

## La regla del vault

> **Si no está en el vault, no pasó.** Todo lo que Claude produce
> (resúmenes, planes, reportes) se escribe como markdown en
> `vault/outputs/`. Capturas crudas van a `vault/raw/`. Conocimiento
> curado va a `vault/wiki/`.

## Guardar

- **Captura rápida** ("guardá esto", una idea, un link, un dato):
  `vault/raw/AAAA-MM-DD-<tema-corto>.md`, tal cual llegó, con una línea de
  contexto arriba (fecha, de dónde salió).
- **Conocimiento curado** ("acordate que", decisiones, contactos, cómo se
  hace algo): nota en `vault/wiki/<tema>.md` — una nota por tema; si ya
  existe, actualizarla, no duplicarla. Usar links `[[entre notas]]`.
- **Entregables** (resúmenes, reportes pedidos por el usuario):
  `vault/outputs/<nombre>.md` con fecha adentro.

## Recuperar

"¿Qué sabemos de X?" → buscar con Grep en todo `vault/` (raw, wiki y
outputs), responder citando de qué nota salió cada cosa, y si el tema
apareció en varias capturas de `raw/`, ofrecer consolidarlo en una nota de
`wiki/`.

## Sesiones de voz (franja de audio del HUD)

Cuando la conversación sea por voz (VoiceMode o dictado), mantener
`vault/outputs/audio.md` actualizado después de cada intercambio, con este
formato exacto:

```
estado: escuchando
transcripcion: <lo último que dijo el usuario>
respuesta: <lo último que respondió JARVIS en voz>
actualizado: HH:MM
```

`estado` es `escuchando` durante la sesión de voz y `en espera` al
terminarla.

## Al correr (protocolo HUD)

En `vault/outputs/estado-skills.md`: al empezar, poner la línea de `vault`
en `corriendo`; al terminar, volver a `inactiva`, sumar 1 a `hoy:`, poner
`ultima: HH:MM` y actualizar `actualizado:`. Si `actualizado:` era de otro
día, resetear antes todos los `hoy:` a 0.
