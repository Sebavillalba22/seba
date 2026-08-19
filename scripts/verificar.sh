#!/usr/bin/env bash
# Revisa el JARVIS OS pieza por pieza y te dice qué falta y cómo arreglarlo.
#
#   ./scripts/verificar.sh
#
# No cambia nada: solo mira.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

VERDE=$'\033[32m'; ROJO=$'\033[31m'; AMAR=$'\033[33m'; GRIS=$'\033[90m'; FIN=$'\033[0m'
FALTAN=0

ok()   { printf "  ${VERDE}✓${FIN} %s\n" "$1"; }
mal()  { printf "  ${ROJO}✗${FIN} %s\n     ${GRIS}→ %s${FIN}\n" "$1" "$2"; FALTAN=$((FALTAN+1)); }
warn() { printf "  ${AMAR}!${FIN} %s\n     ${GRIS}→ %s${FIN}\n" "$1" "$2"; }
titulo(){ printf "\n${GRIS}══${FIN} %s\n" "$1"; }

printf "\n  JARVIS OS · chequeo del sistema\n"

# ── Pieza 1: Claude Code ─────────────────────────────────────────────────────
titulo "Pieza 1 · Claude Code"
if command -v claude >/dev/null; then
  ok "Claude Code instalado ($(claude --version 2>/dev/null | head -1))"
else
  mal "No encuentro el comando 'claude'" "npm install -g @anthropic-ai/claude-code"
fi

# ── Pieza 2: skills ──────────────────────────────────────────────────────────
titulo "Pieza 2 · Skills"
PRESENTES=0
for s in metricas inbox tendencias plan vault; do
  [ -f ".claude/skills/$s/SKILL.md" ] && PRESENTES=$((PRESENTES+1))
done
if [ "$PRESENTES" -ge 3 ]; then
  ok "$PRESENTES de 5 skills en .claude/skills/"
else
  mal "Solo $PRESENTES skills" "faltan archivos SKILL.md — revisá .claude/skills/"
fi
if [ -d "$HOME/.claude/skills" ] && ls "$HOME/.claude/skills"/*/SKILL.md >/dev/null 2>&1; then
  ok "También hay skills personales en ~/.claude/skills/"
else
  warn "Las skills solo aplican dentro de este repo" "para usarlas en todas tus carpetas: cp -r .claude/skills/* ~/.claude/skills/"
fi

# ── Pieza 3: vault ───────────────────────────────────────────────────────────
titulo "Pieza 3 · Vault (memoria)"
for d in raw wiki outputs; do
  [ -d "vault/$d" ] && ok "vault/$d/" || mal "Falta vault/$d/" "mkdir -p vault/$d"
done
if [ -d "vault/.obsidian" ]; then
  ok "Obsidian ya abrió esta carpeta como vault"
else
  warn "Obsidian todavía no abrió vault/ como vault" "Obsidian → Open folder as vault → elegí $REPO/vault"
fi
if command -v claude >/dev/null && claude mcp list 2>/dev/null | grep -qi obsidian; then
  ok "MCP de Obsidian conectado (puedo buscar dentro del vault)"
else
  warn "Sin MCP de Obsidian (opcional: sirve para BUSCAR, no para escribir)" "./scripts/conectar-obsidian.sh"
fi

# ── Pieza 4: voz ─────────────────────────────────────────────────────────────
titulo "Pieza 4 · Voz"
IDIOMA=$(python3 -c "
import json, pathlib
p = pathlib.Path.home()/'.claude'/'settings.json'
try: print(json.loads(p.read_text()).get('language',''))
except Exception: print('')
" 2>/dev/null)
if [ "$IDIOMA" = "spanish" ] || [ "$IDIOMA" = "es" ]; then
  ok "Dictado en español"
else
  mal "El dictado transcribe en inglés (idioma: ${IDIOMA:-sin configurar})" "./scripts/instalar-voz.sh --solo-dictado"
fi
if command -v claude >/dev/null && claude mcp list 2>/dev/null | grep -qi voicemode; then
  ok "VoiceMode conectado (te contesta hablando: claude converse)"
else
  warn "Sin VoiceMode (con /voice ya podés dictar, pero no te responde en voz)" "./scripts/instalar-voz.sh"
fi

# ── Pieza 5: HUD y datos ─────────────────────────────────────────────────────
titulo "Pieza 5 · HUD y datos"
[ -f "hud.html" ] && ok "hud.html presente (./scripts/jarvis para abrirlo)" \
                  || mal "Falta hud.html" "revisá el repo"

hoy=$(date +%Y-%m-%d)
for par in "metricas.md:metricas" "plan.md:plan" "inbox.md:inbox" "estado-skills.md:—" "audio.md:—"; do
  archivo="${par%%:*}"; skill="${par##*:}"
  if [ -f "vault/outputs/$archivo" ]; then
    modificado=$(date -r "vault/outputs/$archivo" +%Y-%m-%d 2>/dev/null || echo "?")
    if [ "$modificado" = "$hoy" ]; then
      ok "vault/outputs/$archivo (de hoy)"
    else
      warn "vault/outputs/$archivo es del $modificado" "el HUD va a mostrar datos viejos — actualizalo"
    fi
  elif [ "$skill" = "—" ]; then
    mal "Falta vault/outputs/$archivo" "lo genera el sistema al correr cualquier skill"
  else
    mal "Falta vault/outputs/$archivo" "pedile a Claude que corra la skill '$skill'"
  fi
done

# ── Credenciales ─────────────────────────────────────────────────────────────
titulo "Credenciales"
if [ -f "jarvis-haz-lo-tuyo/instagram.json" ]; then
  if python3 scripts/metricas.py --check >/dev/null 2>&1; then
    ok "Instagram: token válido ($(python3 scripts/metricas.py --check 2>/dev/null))"
  else
    mal "Instagram: el token no responde" "regeneralo en la app de Meta y actualizá jarvis-haz-lo-tuyo/instagram.json"
  fi
else
  mal "Falta jarvis-haz-lo-tuyo/instagram.json" "copiá instagram.example.json y completá ig_user_id y access_token"
fi
[ -f "jarvis-haz-lo-tuyo/wordpress.json" ] && ok "WordPress configurado" \
  || warn "Sin jarvis-haz-lo-tuyo/wordpress.json (opcional)" "hace falta para subir imágenes y publicar notas"

# ── Cierre ───────────────────────────────────────────────────────────────────
echo
if [ "$FALTAN" -eq 0 ]; then
  printf "  ${VERDE}Sistema completo.${FIN} Arrancá con: ./scripts/jarvis\n\n"
else
  printf "  ${AMAR}%s cosa(s) por resolver${FIN} — cada una tiene su comando arriba.\n\n" "$FALTAN"
fi
