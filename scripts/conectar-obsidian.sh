#!/usr/bin/env bash
# Conecta Claude Code con tu vault de Obsidian (búsqueda dentro del vault).
#
#   ./scripts/conectar-obsidian.sh                 # te pide la API key
#   ./scripts/conectar-obsidian.sh <API_KEY>
#
# OJO: esto es el "camino avanzado". Para escribir y leer notas NO hace falta:
# Claude Code ya escribe los .md en vault/ y Obsidian los muestra. Esto suma
# que Claude pueda BUSCAR dentro del vault abierto en Obsidian.
#
# Requisito: plugin "Local REST API" (de coddingtonbear) instalado y activado
# en Obsidian, v5+ (trae el servidor MCP adentro). La key está en
# Obsidian → Configuración → Local REST API.
set -euo pipefail

HTTPS_URL="https://127.0.0.1:27124/mcp/"
HTTP_URL="http://127.0.0.1:27123/mcp/"

KEY="${1:-${OBSIDIAN_API_KEY:-}}"
if [ -z "$KEY" ]; then
  echo "Pegá tu API key de Obsidian (Configuración → Local REST API):"
  read -r -s KEY
  echo
fi
[ -n "$KEY" ] || { echo "✗ Sin API key no puedo conectar."; exit 1; }

command -v claude >/dev/null || { echo "✗ No encuentro el comando 'claude'."; exit 1; }

echo "→ Probando si Obsidian está escuchando…"
probar() { curl -sk -o /dev/null -w "%{http_code}" -m 5 -H "Authorization: Bearer $KEY" "$1" 2>/dev/null || echo 000; }

URL=""
CODE_HTTPS=$(probar "$HTTPS_URL")
case "$CODE_HTTPS" in
  200|400|405|406) URL="$HTTPS_URL"; echo "  ✓ responde por HTTPS (27124)";;
  401|403) echo "  ✗ Obsidian responde pero rechaza la key. Copiala de nuevo desde el plugin."; exit 1;;
  *)
    CODE_HTTP=$(probar "$HTTP_URL")
    case "$CODE_HTTP" in
      200|400|405|406) URL="$HTTP_URL"; echo "  ✓ responde por HTTP (27123)";;
      401|403) echo "  ✗ Obsidian responde pero rechaza la key. Copiala de nuevo desde el plugin."; exit 1;;
      *) cat <<'FIN'
  ✗ No contesta ni 27124 ni 27123. Revisá que:
      · Obsidian esté ABIERTO con tu vault
      · el plugin "Local REST API" esté instalado y activado (v5 o más)
      · si usás el puerto HTTP, esté tildado "Enable HTTP server" en el plugin
FIN
         exit 1;;
    esac;;
esac

# El certificado del plugin es autofirmado: si Claude Code rechaza el TLS,
# la salida es el endpoint HTTP en localhost (el tráfico no sale de la máquina).
echo "→ Registrando el MCP en Claude Code…"
claude mcp remove obsidian --scope user 2>/dev/null || true
claude mcp add --scope user --transport http obsidian "$URL" \
  --header "Authorization: Bearer $KEY"

echo
echo "✓ Listo. Abrí Claude Code y probá: «buscá en el vault qué sabemos de X»"
echo "  Ver conexiones:  claude mcp list"
echo "  Desconectar:     claude mcp remove obsidian --scope user"
