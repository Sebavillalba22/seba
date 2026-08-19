# Vault — la memoria del JARVIS OS

Carpeta pensada para abrirse como **vault de Obsidian** (Obsidian → "Open folder
as vault" → elegir esta carpeta `vault/`). No hace falta ningún plugin:
Claude Code lee y escribe los `.md` directamente acá.

## Estructura

| Carpeta    | Qué va ahí                                                        |
|------------|-------------------------------------------------------------------|
| `raw/`     | Todo lo que se captura sin editar (notas de voz, links, datos crudos, historiales) |
| `wiki/`    | Conocimiento ya organizado (temas, contactos, decisiones)          |
| `outputs/` | Lo que JARVIS entrega: resúmenes, planes, reportes — **y lo que lee el HUD** |

## La regla del vault

> **Si no está en el vault, no pasó.**

Todo lo que Claude produce (resúmenes, planes, reportes, métricas) se escribe
como markdown en `outputs/`. Así siempre se puede leer exactamente qué hizo el
sistema, desde Obsidian o desde el HUD (`hud.html` en la raíz del repo).

## Archivos que el HUD lee de `outputs/`

| Archivo             | Lo escribe la skill | Panel del HUD        |
|---------------------|---------------------|----------------------|
| `metricas.md`       | `metricas`          | Vitales (sparklines) |
| `plan.md`           | `plan`              | Agenda de hoy        |
| `inbox.md`          | `inbox`             | Inbox                |
| `estado-skills.md`  | todas               | Panel de comandos    |
| `audio.md`          | sesión de voz       | Franja de audio      |

Los formatos exactos están descritos en cada `SKILL.md` de `.claude/skills/`.
