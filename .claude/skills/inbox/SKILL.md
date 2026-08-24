---
name: inbox
description: Usa esta skill cuando el usuario pida su resumen matutino, "qué hay hoy", "revisá el inbox", "qué me llegó", "resumen de mensajes y agenda". Junta lo que llegó (comentarios de IG, mails/calendario si hay conectores, lo que el usuario pegue), lo condensa en un parte corto y lo guarda en vault/outputs/inbox.md (lo que lee el HUD).
---

# inbox — el parte matutino

Una skill, un propósito: **condensar lo que entró en un resumen accionable**.

## Fuentes (usar las que estén disponibles, en este orden)

1. **Comentarios recientes de IG**: API Graph con
   `jarvis-haz-lo-tuyo/instagram.json` —
   `GET /{ig_user_id}/media?fields=comments{text,username,timestamp},permalink&limit=10`
   y quedarse con lo de las últimas 24 h que pida respuesta.
2. **Mail y calendario**: solo si la sesión tiene conectores (Gmail, Calendar)
   — buscar lo no leído importante y los eventos de hoy.
3. **Lo que el usuario pegue** (capturas, mensajes de WhatsApp copiados,
   avisos): siempre entra al resumen.
4. Sin fuentes disponibles → decirlo y pedir al usuario que pegue lo que
   quiera resumir. No inventar mensajes.

## Salida obligatoria: `vault/outputs/inbox.md`

Agregar la entrada nueva **arriba** (debajo del título `# Inbox`), con este
formato exacto (el HUD muestra las últimas 3-5):

```
# Inbox

## 09:12 — Parte de la mañana (2026-08-20)
3 comentarios en el carrusel de obras piden precios — responder hoy.
Municipalidad de Funes confirmó la entrevista de mañana 10:00.
Nada urgente en el mail.
```

Reglas: título de entrada = `## HH:MM — <título corto>`; cuerpo de 2-5
líneas, lo urgente primero; mantener como máximo las últimas 10 entradas
(las viejas se mueven a `vault/raw/inbox-archivo.md`).

## Al correr (protocolo HUD)

Marcá el estado con el script — no edites `estado-skills.md` a mano
(él lleva el contador del día y lo resetea solo):

```bash
python3 scripts/estado_skills.py inbox corriendo   # al empezar
python3 scripts/estado_skills.py inbox inactiva    # al terminar (suma 1 corrida)
```

## Respuesta al usuario

El mismo parte, tal cual quedó en el vault — sin repetir en otro formato.
Si algo requiere acción hoy, cerrarlo con "¿Lo meto en el plan?" (skill
`plan`).
