# Conexión local con Claude (MCP)

Esto conecta Claude **en tu PC** directo con la app de Obsidian, sin pasar
por GitHub. Sirve cuando trabajás con Claude Desktop o Claude Code local y
querés respuesta instantánea sobre la bóveda que tenés abierta.

> **Ojo — el camino simple primero:** como la bóveda es una carpeta de
> archivos Markdown, si usás **Claude Code en tu PC** alcanza con abrirlo
> parado en la carpeta de la bóveda (`cd C:\ruta\a\tu\boveda` → `claude`) y
> ya puede leer, buscar y editar todas tus notas. El MCP solo hace falta si
> querés que Claude interactúe con la **app en vivo**: usar el buscador de
> Obsidian, ver qué nota tenés abierta, abrir notas, etc.

## Paso 1 — Plugin "Local REST API" en Obsidian

1. Ajustes → Community plugins → Browse → **"Local REST API"** (de Adam
   Coddington) → Install → Enable.
2. En las opciones del plugin, copiá la **API Key**. Anotá también el
   puerto (por defecto HTTPS `27124`; podés habilitar HTTP `27123`).

## Paso 2 — Instalar uv (una vez)

El servidor MCP corre con `uvx`. En PowerShell:

```powershell
winget install astral-sh.uv
```

## Paso 3A — Claude Code local

```powershell
claude mcp add obsidian -e OBSIDIAN_API_KEY=TU_API_KEY -e OBSIDIAN_HOST=127.0.0.1 -- uvx mcp-obsidian
```

Reemplazá `TU_API_KEY` por la key del paso 1. Verificá con `claude mcp list`.

## Paso 3B — Claude Desktop

Editá `%APPDATA%\Claude\claude_desktop_config.json` (creálo si no existe) y
agregá:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uvx",
      "args": ["mcp-obsidian"],
      "env": {
        "OBSIDIAN_API_KEY": "TU_API_KEY",
        "OBSIDIAN_HOST": "127.0.0.1"
      }
    }
  }
}
```

Reiniciá Claude Desktop (salir del todo desde la bandeja) y tiene que
aparecer el servidor `obsidian` en las herramientas.

## Para tener en cuenta

- **Obsidian tiene que estar abierto** con tu bóveda cargada; si no, el
  MCP no responde.
- Funciona solo en esa PC. Desde sesiones web o el celular, Claude llega a
  tus notas por GitHub: ver [[Sincronización con GitHub]].
- Las dos vías conviven sin problema: local para trabajar en vivo, GitHub
  para todo lo demás.
