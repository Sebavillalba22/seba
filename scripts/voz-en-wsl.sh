#!/usr/bin/env bash
# Conversación de voz completa (Opción B de la guía) en Windows, vía WSL2.
#
# Instala: Node + Claude Code + dependencias de audio + VoiceMode
# (Whisper para escuchar, Kokoro para hablar — los dos corren en tu máquina).
#
# ANTES, una sola vez, en PowerShell como administrador:
#     wsl --install
# Reiniciás, abrís Ubuntu, elegís usuario y contraseña, y recién ahí corrés esto.
#
# Por qué WSL y no Windows directo: VoiceMode usa fcntl, un módulo que solo
# existe en Unix, y su instalador corta si detecta Windows. No es evitable.
set -euo pipefail

grep -qi microsoft /proc/version 2>/dev/null || {
  echo "✗ Esto va adentro de WSL (Ubuntu), no en Windows ni en Mac."
  exit 1
}

echo "══ 1/4 · Node.js y Claude Code ══"
if ! command -v node >/dev/null || [ "$(node -v | cut -c2- | cut -d. -f1)" -lt 18 ]; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi
command -v claude >/dev/null || sudo npm install -g @anthropic-ai/claude-code

echo
echo "══ 2/4 · Dependencias de audio ══"
# En WSL el micrófono entra por PulseAudio (WSLg), no por ALSA: sin estos
# paquetes VoiceMode instala bien pero no escucha nada.
sudo apt-get update -qq
sudo apt-get install -y ffmpeg gcc python3-dev \
  libasound2-dev libasound2-plugins libportaudio2 portaudio19-dev \
  pulseaudio pulseaudio-utils sox libsox-fmt-pulse

echo
echo "══ 3/4 · VoiceMode (baja los modelos: tarda) ══"
if ! command -v uvx >/dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
uvx voice-mode-install

echo
echo "══ 4/4 · Registrarlo en Claude Code ══"
claude mcp remove voicemode --scope user 2>/dev/null || true
claude mcp add --scope user voicemode -- uvx --refresh --from voice-mode voicemode-mcp-launcher

# Dictado en español, de paso (arranca en inglés por defecto).
python3 - <<'PY'
import json, pathlib
p = pathlib.Path.home() / ".claude" / "settings.json"
p.parent.mkdir(parents=True, exist_ok=True)
try:
    cfg = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(cfg, dict): raise ValueError
except Exception:
    cfg = {}
cfg["language"] = "spanish"
p.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY

cat <<'FIN'

✓ Listo.

  1. claude          → te pide iniciar sesión con tu cuenta de Claude
  2. claude converse → hablás y te responde hablando

  Si no te escucha:  pactl info    (tiene que listar un servidor de audio)
FIN
