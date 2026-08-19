# JARVIS OS — armado en este repo

Implementación de la guía *Arma tu JARVIS OS* (@ortegoat) sobre Claude Code,
adaptada a Estacionline. Las 5 piezas, qué quedó hecho acá y qué te falta
hacer en tu máquina.

---

## Pieza 1 · Claude Code — el motor

Ya lo estás usando. Si lo instalás en otra máquina:

```bash
# requiere Node.js 18+ (o usá el instalador nativo, que no necesita Node)
npm install -g @anthropic-ai/claude-code
cd mi-proyecto
claude
```

Requiere iniciar sesión con tu cuenta de Claude (Pro, Max, Team o Enterprise).
**El único gasto fijo de todo el sistema es tu plan de Claude** (~$20/mes
mínimo). Las skills, el vault y la voz local son gratis y open source.

Docs: <https://docs.claude.com/claude-code>

---

## Pieza 2 · Skills — el cerebro ✅ hecho

Cinco skills en `.claude/skills/`, una carpeta con su `SKILL.md` cada una.
Claude las activa solo cuando hacen falta — no hace falta invocarlas.

| Skill        | Qué hace                                              | Escribe en                    |
|--------------|-------------------------------------------------------|-------------------------------|
| `metricas`   | Jala los números de IG/web y los resume                | `vault/outputs/metricas.md`   |
| `inbox`      | Arma el parte matutino de mensajes y agenda            | `vault/outputs/inbox.md`      |
| `tendencias` | Escanea qué está funcionando en el nicho               | `vault/outputs/tendencias.md` |
| `plan`       | Escribe tu top 3 de prioridades del día                | `vault/outputs/plan.md`       |
| `vault`      | Lee y escribe la memoria (Pieza 3)                     | `vault/raw/`, `wiki/`, `outputs/` |

Están en `.claude/skills/` (**del proyecto**: solo aplican en este repo).
Para tenerlas en todas tus carpetas, copialas a las personales:

```bash
cp -r .claude/skills/* ~/.claude/skills/
```

Probalas escribiendo, adentro de Claude Code: *"armame el plan de hoy"*,
*"pasame los números"*, *"revisá el inbox"*, *"qué está rindiendo"*,
*"guardá esto en el vault"*.

> **Regla de oro:** una skill, un propósito. El campo `description` es lo que
> Claude lee para decidir cuándo usarla — por eso son largas y específicas.

Docs: <https://code.claude.com/docs/en/skills>

---

## Pieza 3 · Obsidian — la memoria ✅ hecho

La carpeta `vault/` ya está armada con la estructura de la guía:

```
vault/
  raw/       # todo lo que se captura sin editar
  wiki/      # conocimiento ya organizado
  outputs/   # lo que JARVIS entrega — y lo que lee el HUD
```

En Obsidian: **Open folder as vault** → elegir `vault/`. No hace falta ningún
plugin: Claude Code escribe los `.md` directo ahí y vos los ves organizados.

**La regla del vault: si no está en el vault, no pasó.** Todo lo que produce
el sistema queda como markdown en `outputs/`, así siempre podés leer qué hizo.

*Camino avanzado (opcional):* para que Claude **busque dentro** del vault hay
servidores MCP de la comunidad — [obsidian-mcp-server](https://github.com/Vasallo94/obsidian-mcp-server)
y [obsidian-claude-code-mcp](https://github.com/iansinnott/obsidian-claude-code-mcp).
No son oficiales de Obsidian ni de Anthropic: revisá el código y los permisos
antes de darles acceso al vault, sobre todo si pueden escribir o borrar notas.

---

## Pieza 4 · Voz — oídos y boca ⏳ te toca a vos

Esta pieza necesita micrófono local, así que se instala en tu máquina (no
funciona por SSH ni en Claude Code en la web).

**Opción A — dictado nativo** (ya viene, no instalás nada):

```
/voice          # dentro de Claude Code: mantené espacio, hablá, soltá
```

Requiere cuenta de claude.ai (no anda con API key directa, Bedrock, Vertex ni
Foundry). Es solo entrada de voz: no te responde hablando.

**Opción B — conversación completa, 100% local** con [VoiceMode](https://github.com/mbailey/voicemode)
(Whisper para escuchar + Kokoro para hablar, vía MCP):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uvx voice-mode-install
claude mcp add --scope user voicemode -- uvx --refresh voice-mode
# dentro de Claude Code:
claude converse
```

Gratis (sin costo por minuto), privado (el audio no sale de tu máquina), con
fallback opcional a OpenAI si preferís nube.

Cuando trabajes por voz, la skill `vault` mantiene actualizado
`vault/outputs/audio.md` y la franja de abajo del HUD muestra la última
transcripción y la última respuesta.

---

## Pieza 5 · El HUD — la cara ✅ hecho

`hud.html` — un solo archivo, sin backend, sin librerías externas. Fondo casi
negro, un solo acento (el verde del isologo), mono para números y sans para
etiquetas. Todo en una pantalla, sin scroll.

**Cómo abrirlo** (necesita servidor para poder leer los `.md`):

```bash
python3 -m http.server 8000
# y entrá a http://localhost:8000/hud.html
```

Si lo abrís haciendo doble clic (`file://`), el navegador bloquea la lectura de
archivos: el propio HUD te ofrece un botón **ELEGIR CARPETA VAULT** (Chrome y
Edge) para darle acceso a mano.

**Los 4 paneles + la franja de audio:**

| Zona                       | De dónde salen los datos                    |
|----------------------------|---------------------------------------------|
| Vitales (izq. arriba)      | `outputs/metricas.md` — valor, variación 7d y sparkline |
| Agenda de hoy (izq. abajo) | `outputs/plan.md` — resalta la tarea **AHORA** |
| Panel de comandos (der. arriba) | `outputs/estado-skills.md` — estado y corridas de hoy |
| Inbox (der. abajo)         | `outputs/inbox.md` — últimos 3-5 partes     |
| Franja de audio (abajo)    | `outputs/audio.md` — escuchando/en espera + última transcripción y respuesta |

Se refresca solo cada 5 segundos. **No tiene datos de ejemplo**: si falta un
archivo, el panel te dice cuál falta y qué skill lo genera — así nunca te
quedás mirando datos viejos creyendo que son de hoy. Por eso al abrirlo la
primera vez Vitales aparece vacío: corré la skill `metricas` y se puebla.

**Para iterar sobre el diseño**, pedile ajustes puntuales a Claude Code, no
"hacelo más lindo": *"achicá el panel de agenda y agrandá el de vitales"*,
*"el sparkline de seguidores no se actualiza, revisá cómo lee el archivo"*.
Con la Pieza 4 andando, se lo ajustás hablando.

---

## Checklist final

- [x] Claude Code instalado y corriendo en tu proyecto
- [x] Al menos 3 skills (hay 5, en `.claude/skills/`)
- [x] Vault de Obsidian escribiendo outputs reales
- [ ] **Voz** — nativa (`/voice`) o VoiceMode — respondiendo *(en tu máquina)*
- [ ] **HUD mostrando datos reales** — abrilo y corré `metricas` para poblar Vitales

---

## Recursos oficiales

- Claude Code — documentación: <https://docs.claude.com/claude-code>
- Claude Code — Skills: <https://code.claude.com/docs/en/skills>
- Claude Code — Voice dictation: <https://code.claude.com/docs/en/voice-dictation>
- Obsidian: <https://obsidian.md>
- VoiceMode: <https://github.com/mbailey/voicemode>

> "JARVIS OS" no es un producto que descargás: es un patrón que armás
> combinando estas 5 piezas open source y oficiales. — @ortegoat
