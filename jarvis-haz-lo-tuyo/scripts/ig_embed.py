#!/usr/bin/env python3
"""Obtener el CÓDIGO DE INSERCIÓN (embed) de un post de Instagram, para
pegarlo dentro del cuerpo de una nota web (no un link plano).

Métodos, en orden:
  1. oEmbed oficial de la Graph API (/instagram_oembed) con el token de
     instagram.json — devuelve el HTML exacto de Instagram.
  2. Si la API no lo permite (falta el permiso oEmbed Read, token, etc.),
     genera el blockquote oficial de Instagram + embed.js, que es el mismo
     código que da el botón "Insertar" de Instagram y funciona sin API.

Uso:
  ig_embed.py --latest
  ig_embed.py --permalink "https://www.instagram.com/p/ABC123/"
  ig_embed.py --media-id 1789...
Salida: JSON {ok, permalink, method: "oembed-api"|"blockquote", embed_html}
"""
from __future__ import annotations

import argparse
import json
import sys

import ig_publish
from ig_publish import _get


def _norm(url: str) -> str:
    return url.split("?")[0].rstrip("/") + "/"


def resolve_permalink(args) -> str:
    if args.permalink:
        return _norm(args.permalink)
    ig_id, token = ig_publish.load_ig()
    if args.media_id:
        r = _get(args.media_id, {"fields": "permalink", "access_token": token})
        return _norm(r["permalink"])
    # --latest
    r = _get(f"{ig_id}/media", {"fields": "permalink", "limit": 1, "access_token": token})
    data = r.get("data") or []
    if not data:
        print("ERROR: la cuenta de IG no tiene posts.", file=sys.stderr)
        sys.exit(1)
    return _norm(data[0]["permalink"])


def try_oembed(permalink: str) -> str | None:
    """oEmbed oficial. Requiere que la app tenga la feature 'oEmbed Read';
    si no, devolvemos None y se usa el blockquote."""
    try:
        _, token = ig_publish.load_ig()
        r = _get("instagram_oembed", {"url": permalink, "omitscript": "false",
                                      "access_token": token})
        return r.get("html")
    except SystemExit:
        return None


def blockquote_embed(permalink: str) -> str:
    return (
        f'<blockquote class="instagram-media" data-instgrm-captioned '
        f'data-instgrm-permalink="{permalink}?utm_source=ig_embed" data-instgrm-version="14" '
        f'style="background:#FFF; border:0; border-radius:3px; margin:1px auto; '
        f'max-width:540px; min-width:326px; padding:0; width:99.375%;">'
        f'<a href="{permalink}" target="_blank" rel="noopener">Ver esta publicación en Instagram</a>'
        f'</blockquote>\n'
        f'<script async src="https://www.instagram.com/embed.js"></script>'
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Código de inserción de un post de Instagram.")
    which = ap.add_mutually_exclusive_group(required=True)
    which.add_argument("--latest", action="store_true", help="el último post de la cuenta.")
    which.add_argument("--permalink", help="link del post (instagram.com/p/...).")
    which.add_argument("--media-id", help="media id de IG.")
    ap.add_argument("--blockquote-only", action="store_true",
                    help="no intentar la API; generar directamente el blockquote oficial.")
    args = ap.parse_args()

    permalink = resolve_permalink(args)
    html = None if args.blockquote_only else try_oembed(permalink)
    method = "oembed-api" if html else "blockquote"
    if not html:
        html = blockquote_embed(permalink)
    print(json.dumps({"ok": True, "permalink": permalink, "method": method,
                      "embed_html": html}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
