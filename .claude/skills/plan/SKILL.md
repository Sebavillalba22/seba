---
name: plan
description: Usa esta skill cuando el usuario pida su plan del día, "qué hago hoy", "prioridades", "armame el día", "agenda de hoy", o quiera agregar/marcar tareas. Escribe el top 3 de prioridades del día (más lo fijo con horario) en vault/outputs/plan.md — la agenda que muestra el HUD.
---

# plan — el top 3 del día

Una skill, un propósito: **decidir las 3 prioridades de hoy y dejarlas con
horario en el vault**.

## Cómo armar el plan

1. Leer los insumos del vault si existen: `vault/outputs/inbox.md` (lo que
   pide acción), `vault/outputs/tendencias.md` (ideas), y el `plan.md`
   anterior (lo que quedó sin `[x]` se pregunta: ¿se arrastra o se
   descarta?).
2. Sumar lo que el usuario diga explícitamente — eso manda.
3. Elegir **top 3 prioridades reales** (lo que mueve la aguja de
   Estacionline: publicar, cobrar, conseguir anunciantes, cubrir la noticia
   del día) + como máximo 3 ítems fijos con horario (entrevistas, turnos).
   Máximo 6 líneas en total.

## Salida obligatoria: `vault/outputs/plan.md`

Antes de sobrescribir, archivar el plan anterior agregándolo al final de
`vault/raw/plan-historial.md`. Formato EXACTO (el HUD parsea `- HH:MM tarea`
y resalta la tarea "ahora"; `[x]` = hecha):

```
# Plan — 2026-08-20

- 09:00 Responder los comentarios del carrusel de obras
- [x] 10:30 Entrevista Municipalidad de Funes
- 15:00 Carrusel: avance obra A012 (idea de tendencias)
- 19:00 Publicar y programar historias
```

Reglas: orden cronológico; toda línea lleva horario `HH:MM` (si el usuario
no lo da, proponer uno razonable); marcar `[x]` cuando el usuario diga que
algo está hecho (editar la línea, no borrarla).

## Al correr (protocolo HUD)

En `vault/outputs/estado-skills.md`: al empezar, poner la línea de `plan`
en `corriendo`; al terminar, volver a `inactiva`, sumar 1 a `hoy:`, poner
`ultima: HH:MM` y actualizar `actualizado:`. Si `actualizado:` era de otro
día, resetear antes todos los `hoy:` a 0.

## Respuesta al usuario

El plan tal cual quedó, y una sola pregunta si algo quedó ambiguo. Sin
sermones de productividad.
