---
name: obsidian
description: Connect Claude to the user's Obsidian vault (their existing vault, published as the private repo sebavillalba22/obsidian and synced to their devices via the Obsidian Git plugin). Triggers on "obsidian", "mis notas", "mi bóveda", "anotá esto", "guardalo en obsidian", "buscá en mis notas", "nota diaria", or any request to read/write/search personal notes. Covers connecting the repo in a session, reading and writing notes respecting the vault's own structure, and the first-time setup of publishing the existing vault to GitHub.
---

# obsidian — Conexión con la bóveda de notas

La bóveda de Obsidian del usuario es **su bóveda existente**, publicada como
repo privado **`sebavillalba22/obsidian`** (rama `main`). En sus
dispositivos, el plugin **Obsidian Git** hace pull/push automático: todo lo
que se pushea a `main` aparece solo en su Obsidian, y sus notas nuevas
llegan al repo solas.

## Conectar en una sesión

1. Agregar el repo con `add_repo` (owner `sebavillalba22`, repo `obsidian`,
   access `push`) y clonarlo como indique la respuesta.
2. **Siempre `git pull origin main` antes de tocar nada** — el usuario pudo
   haber escrito notas desde el celular hace un minuto.
3. Editar / crear notas, commit y `git push origin main`.

> Si `add_repo` falla porque el repo no existe → la bóveda todavía no se
> publicó: guiar al usuario con `para-tu-boveda/Guías/Sincronización con
> GitHub.md` (los pasos los ejecuta él en su PC, donde está la bóveda).
> Si falla por permisos, el usuario tiene que darle acceso al repo a la app
> de GitHub de Claude (claude.ai → Settings → Connectors → GitHub).

## Reglas de la bóveda

- **La bóveda usa `main` directo: sin ramas, sin PRs.** Es una libreta, no
  código. Commit y push inmediato después de cada cambio, para que le llegue
  al toque a sus dispositivos. Nunca force-push ni reescribir historia.
- **Es SU bóveda: la estructura manda.** Antes de crear una nota, mirar las
  carpetas y convenciones que ya existen (nombres, frontmatter, tags) e
  imitarlas. No crear carpetas nuevas ni reorganizar nada salvo pedido
  explícito.
- Nota rápida sin destino claro → a la carpeta tipo inbox si existe
  (`Inbox`, `00 Inbox`, `Bandeja`…); si no, a la raíz. No preguntar por
  decisiones menores de ubicación; se puede mover después.
- Nota diaria → seguir el formato de las que ya haya (carpeta, nombre tipo
  `AAAA-MM-DD`, plantilla). Si ya existe la del día, agregar ahí, no
  duplicar.
- Markdown plano de Obsidian: enlaces internos con `[[wikilinks]]`, tags
  `#asi`, frontmatter YAML si la bóveda lo usa. Nada de HTML raro.
- Adjuntos: a la carpeta de attachments que use la bóveda.
- Para buscar en las notas, usar Grep sobre el clon (es todo Markdown).
- Commits estilo `obsidian: <qué se anotó/cambió>`, en castellano.

## Kit `para-tu-boveda/`

Archivos pensados para copiarse a la bóveda del usuario:

- `.gitignore` — va en la raíz de la bóveda ANTES del primer commit.
- `Guías/Sincronización con GitHub.md` — publicar la bóveda, plugin Git,
  celular con token.
- `Guías/Conexión local con Claude MCP.md` — conectar Claude Desktop /
  Claude Code local directo a la app de Obsidian.

La primera vez que Claude se conecte a la bóveda ya publicada: si faltan las
guías o el `.gitignore`, copiarlos del kit y pushearlos (sin pisar archivos
que el usuario ya tenga).
