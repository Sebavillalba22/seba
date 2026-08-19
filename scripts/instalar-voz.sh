#!/usr/bin/env bash
# Pieza 4 — Voz. Corré esto EN TU MÁQUINA (necesita micrófono).
#
#   ./scripts/instalar-voz.sh          # deja el dictado en español + instala VoiceMode
#   ./scripts/instalar-voz.sh --solo-dictado
#
# Dictado nativo (/voice): entrada de voz, ya viene con Claude Code.
# VoiceMode: conversación completa (te contesta hablando), 100% local.
set -euo pipefail

SOLO_DICTADO=false
[ "${1:-}" = "--solo-dictado" ] && SOLO_DICTADO=true

echo "══ Pieza 4 · Voz ══"

# ── 1. Dictado en español ───────────────────────────────────────────────────
# El dictado arranca en INGLÉS por defecto: sin esto, transcribe mal.
echo "→ Dejando el dictado de Claude Code en español…"
python3 - <<'PY'
import json, pathlib
p = pathlib.Path.home() / ".claude" / "settings.json"
p.parent.mkdir(parents=True, exist_ok=True)
try:
    cfg = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(cfg, dict):
        raise ValueError
except Exception:
    cfg = {}
cfg["language"] = "spanish"
voz = cfg.get("voice") if isinstance(cfg.get("voice"), dict) else {}
voz.setdefault("enabled", True)
voz.setdefault("mode", "tap")      # tap: tocás espacio, hablás, tocás y se manda
cfg["voice"] = voz
p.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"  ✓ {p}: language=spanish, voice={voz}")
PY

if $SOLO_DICTADO; then
  echo
  echo "✓ Listo. Abrí Claude Code y tocá espacio para hablar (o /voice hold para mantener apretado)."
  exit 0
fi

# ── 2. Dependencias del sistema para VoiceMode ──────────────────────────────
echo "→ Revisando dependencias del sistema…"
case "$(uname -s)" in
  Darwin)
    if command -v brew >/dev/null; then
      brew list ffmpeg >/dev/null 2>&1 || brew install ffmpeg
      brew list portaudio >/dev/null 2>&1 || brew install portaudio
    else
      echo "  ! Sin Homebrew. Instalá ffmpeg y portaudio a mano: https://brew.sh"
    fi;;
  Linux)
    if command -v apt-get >/dev/null; then
      PAQS="ffmpeg gcc libasound2-dev libasound2-plugins libportaudio2 portaudio19-dev"
      echo "  Hacen falta: $PAQS"
      echo "  (pide sudo — si preferís, cancelá con Ctrl+C e instalalos vos)"
      sudo apt-get update -qq && sudo apt-get install -y $PAQS
      grep -qi microsoft /proc/version 2>/dev/null && sudo apt-get install -y sox libsox-fmt-pulse
    else
      echo "  ! No es apt. Instalá el equivalente de: ffmpeg gcc alsa portaudio"
    fi;;
esac

# ── 3. uv + VoiceMode ───────────────────────────────────────────────────────
if ! command -v uvx >/dev/null; then
  echo "→ Instalando uv…"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "→ Instalando VoiceMode (Whisper para escuchar + Kokoro para hablar, local)…"
echo "  La primera vez baja los modelos: puede tardar bastante."
uvx voice-mode-install

echo "→ Registrando VoiceMode en Claude Code…"
# Comando actualizado: la guía en PDF trae el viejo, que ya no levanta el MCP.
claude mcp remove voicemode --scope user 2>/dev/null || true
claude mcp add --scope user voicemode -- uvx --refresh --from voice-mode voicemode-mcp-launcher

cat <<'FIN'

✓ Voz instalada.

  Conversación completa (te contesta hablando):   claude converse
  Solo dictado, sin instalar nada:                /voice   (dentro de Claude Code)

  Comprobar:  claude mcp list
FIN
