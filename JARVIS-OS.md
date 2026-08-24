# JARVIS OS — armado en este repo

Implementación de la guía *Arma tu JARVIS OS* (@ortegoat) sobre Claude Code,
adaptada a Estacionline. Las 5 piezas, qué quedó hecho acá y qué te falta
hacer en tu máquina.

## Arranque rápido

```bash
./scripts/jarvis                  # abre el HUD en el navegador
./scripts/instalar-voz.sh         # Pieza 4: voz (necesita micrófono)
./scripts/conectar-obsidian.sh    # opcional: que Claude busque dentro del vault
python3 scripts/metricas.py       # llena el panel de Vitales con datos reales
```

> **Dos cosas de la guía en PDF cambiaron desde que se escribió** y acá están
> corregidas: el comando que registra VoiceMode es otro (el viejo ya no levanta
> el MCP), y para Obsidian ya no hacen falta los servidores MCP de terceros —
> el plugin oficial trae el suyo. Detalle en las piezas 4 y 3.

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

### Camino avanzado: que Claude *busque* dentro del vault

Esto es lo que cambió desde la guía. Ya no hace falta ningún servidor MCP de
terceros: el plugin oficial **Local REST API** (de coddingtonbear) trae su
propio servidor MCP adentro desde la v5.

1. En Obsidian: **Configuración → Complementos de la comunidad → Buscar →
   "Local REST API"** → instalar y activar.
2. Abrí la configuración del plugin y **copiá la API key**.
3. En la terminal, dentro del repo:

   ```bash
   ./scripts/conectar-obsidian.sh
   ```

   Te pide la key, prueba que Obsidian esté escuchando (HTTPS en 27124, y si
   el certificado autofirmado da problema, HTTP en 27123) y registra el MCP en
   Claude Code.

4. Probá: *"buscá en el vault qué sabemos de X"*.

Requisitos: Obsidian tiene que estar **abierto** con el vault (el servidor vive
dentro de la app) y el plugin en **v4.1.3 o superior** — las versiones v4
anteriores tenían un agujero de path traversal ya parcheado. Todo el tráfico es
contra `127.0.0.1`: no sale de tu máquina.

Para desconectarlo: `claude mcp remove obsidian --scope user`.

---

## Pieza 4 · Voz — oídos y boca ⏳ te toca a vos

> ⚠️ **La voz no funciona en Claude Code en la web.** El micrófono está en tu
> máquina y la sesión web corre en un servidor: no hay forma de que te escuche
> desde ahí. Para hablar y que te responda necesitás Claude Code instalado
> localmente (`npm install -g @anthropic-ai/claude-code`). Lo mismo vale para
> sesiones por SSH.
>
> **Si estás en Windows:** el dictado (`/voice`) anda en Windows nativo, pero
> VoiceMode no tiene instalación documentada ahí — el camino que funciona es
> **WSL2** (`wsl --install` en PowerShell como administrador, después clonás el
> repo dentro de Ubuntu y corrés el instalador desde ahí). En WSL hacen falta
> los paquetes de PulseAudio para que el micrófono entre; el script los pone
> solo. Si usás WSL para el dictado nativo, además necesitás WSLg (viene con
> WSL2 instalado desde la Microsoft Store).

Un solo comando deja todo listo:

```bash
./scripts/instalar-voz.sh                  # dictado en español + VoiceMode
./scripts/instalar-voz.sh --solo-dictado   # solo lo nativo, no instala nada más
```

**Opción A — dictado nativo** (ya viene con Claude Code). Con `/voice` tocás
espacio, hablás, y tu voz se transcribe en el prompt.

⚠️ **El dictado arranca en inglés**: si no le cambiás el idioma, transcribe
cualquier cosa. El script te lo deja en español (`"language": "spanish"` en
`~/.claude/settings.json`) y en modo *tap* — tocás espacio, hablás, tocás y se
manda. Con `/voice hold` volvés a mantener apretado.

Requiere cuenta de claude.ai (no anda con API key directa, Bedrock, Vertex ni
Foundry). El audio se transcribe en los servidores de Anthropic, y no consume
tokens ni cuenta para tus límites. Es solo entrada: no te responde hablando.

**Opción B — conversación completa, 100% local** con [VoiceMode](https://github.com/mbailey/voicemode)
(Whisper para escuchar + Kokoro para hablar). Ahí sí te contesta en voz alta,
gratis y sin que el audio salga de tu máquina.

⚠️ **El comando de la guía en PDF quedó viejo.** El que registra el MCP hoy es:

```bash
claude mcp add --scope user voicemode -- uvx --refresh --from voice-mode voicemode-mcp-launcher
```

El instalador ya usa el correcto, y además resuelve las dependencias del
sistema (ffmpeg, portaudio, ALSA en Linux; sox con PulseAudio si estás en WSL).
La primera corrida baja los modelos: tarda. Después:

```bash
claude converse
```

Cuando trabajes por voz, la skill `vault` mantiene actualizado
`vault/outputs/audio.md` y la franja de abajo del HUD muestra la última
transcripción y la última respuesta.

---

## Pieza 5 · El HUD — la cara ✅ hecho

`hud.html` — un solo archivo, sin backend, sin librerías externas. Fondo casi
negro, un solo acento (el verde del isologo), mono para números y sans para
etiquetas. Todo en una pantalla, sin scroll.

**Cómo abrirlo:**

```bash
./scripts/jarvis        # levanta el servidor y abre el navegador
```

(Necesita servidor para poder leer los `.md`. Si lo abrís haciendo doble clic,
`file://` bloquea la lectura: el propio HUD te ofrece un botón **ELEGIR CARPETA
VAULT** en Chrome y Edge para darle acceso a mano.)

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

## Los scripts

| Script | Qué hace |
|---|---|
| `scripts/jarvis` | Levanta el HUD y lo abre en el navegador |
| `scripts/metricas.py` | Jala los números de IG al vault (`--check`, `--manual`) |
| `scripts/estado_skills.py` | Mueve el estado de las skills que muestra el HUD |
| `scripts/instalar-voz.sh` | Pieza 4: dictado en español + VoiceMode |
| `scripts/conectar-obsidian.sh` | Registra el MCP de Obsidian en Claude Code |

Todo con Python de la biblioteca estándar: no hay que instalar dependencias.

---

## Checklist final

- [x] Claude Code instalado y corriendo en tu proyecto
- [x] Al menos 3 skills (hay 5, en `.claude/skills/`)
- [x] Vault de Obsidian escribiendo outputs reales
- [ ] **Voz** — `./scripts/instalar-voz.sh` *(en tu máquina, necesita micrófono)*
- [ ] **HUD mostrando datos reales** — `./scripts/jarvis` + `python3 scripts/metricas.py`
      (necesita `jarvis-haz-lo-tuyo/instagram.json`, que vive solo en tu máquina)

---

## Recursos oficiales

- Claude Code — documentación: <https://docs.claude.com/claude-code>
- Claude Code — Skills: <https://code.claude.com/docs/en/skills>
- Claude Code — Voice dictation: <https://code.claude.com/docs/en/voice-dictation>
- Obsidian: <https://obsidian.md>
- VoiceMode: <https://github.com/mbailey/voicemode>

> "JARVIS OS" no es un producto que descargás: es un patrón que armás
> combinando estas 5 piezas open source y oficiales. — @ortegoat
