#!/usr/bin/env python3
"""Repostear en la página de Facebook un post YA publicado en Instagram
(carrusel o foto única), como hace el crosspost automático del teléfono.

NO crea ningún álbum: trae las imágenes y el caption del post de IG vía la
Graph API y publica UN solo posteo de feed en la página con las fotos
adjuntas (attached_media). En el celular las fotos se deslizan de a una.

Lee instagram.json (ig_user_id + token con scopes de IG) para consultar el
post de IG, y las credenciales de página de FB igual que publish.py
(.credentials.json / env / --page-id + --token).

Ejemplos:
  # repostear el ÚLTIMO post de IG
  fb_repost_ig.py --latest

  # por link del post
  fb_repost_ig.py --permalink "https://www.instagram.com/p/ABC123/"

  # por media id (lo devuelve ig_publish.py al publicar)
  fb_repost_ig.py --media-id 1789...

  # con otro caption, o sin caption
  fb_repost_ig.py --latest --caption "Otro texto"
  fb_repost_ig.py --latest --no-caption

  # ver qué haría sin publicar
  fb_repost_ig.py --latest --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
from pathlib import Path

from publish import (  # mismo directorio scripts/
    GRAPH,
    _die,
    _get,
    load_credentials,
    publish_multi_photo_post,
    upload_photo,
)

IG_FILE = Path(__file__).resolve().parent.parent / "instagram.json"


def load_ig() -> tuple[str, str]:
    if not IG_FILE.exists():
        _die(f"No existe {IG_FILE}. Falta configurar Instagram.")
    d = json.loads(IG_FILE.read_text(encoding="utf-8"))
    if not d.get("ig_user_id") or not d.get("access_token"):
        _die("instagram.json incompleto (ig_user_id / access_token).")
    return d["ig_user_id"], d["access_token"]


def _ig_get(path: str, params: dict, token: str) -> dict:
    params = dict(params, access_token=token)
    return _get(f"{GRAPH}/{path}?" + urllib.parse.urlencode(params))


def _norm_permalink(url: str) -> str:
    """Compara permalinks ignorando query string y barra final."""
    u = urllib.parse.urlsplit(url.strip())
    return (u.netloc.removeprefix("www.") + u.path.rstrip("/")).lower()


def resolve_media_id(ig_id: str, token: str,
                     media_id: str | None, permalink: str | None,
                     latest: bool) -> str:
    if media_id:
        return media_id
    if latest:
        r = _ig_get(f"{ig_id}/media", {"fields": "id", "limit": 1}, token)
        data = r.get("data") or []
        if not data:
            _die("la cuenta de IG no tiene posts.")
        return data[0]["id"]
    if permalink:
        want = _norm_permalink(permalink)
        r = _ig_get(f"{ig_id}/media", {"fields": "id,permalink", "limit": 50}, token)
        for m in r.get("data") or []:
            if _norm_permalink(m.get("permalink", "")) == want:
                return m["id"]
        _die(f"no encontré {permalink} entre los últimos 50 posts de IG.")
    _die("pasá --latest, --permalink o --media-id.")


def fetch_ig_post(media_id: str, token: str) -> dict:
    fields = ("id,caption,media_type,media_url,permalink,"
              "children{id,media_type,media_url}")
    return _ig_get(media_id, {"fields": fields}, token)


def image_urls(post: dict) -> list[str]:
    """URLs de las imágenes del post, en orden. Los videos del carrusel se
    saltean con aviso (a FB solo se pueden adjuntar fotos por esta vía)."""
    if post.get("media_type") == "CAROUSEL_ALBUM":
        urls, skipped = [], 0
        for child in (post.get("children") or {}).get("data", []):
            if child.get("media_type") == "IMAGE" and child.get("media_url"):
                urls.append(child["media_url"])
            else:
                skipped += 1
        if skipped:
            print(f"  aviso: salteo {skipped} item(s) de video del carrusel "
                  "(el repost a FB solo adjunta fotos)", file=sys.stderr)
        if not urls:
            _die("el carrusel no tiene imágenes reposteables (¿es todo video?).")
        return urls
    if post.get("media_type") == "IMAGE" and post.get("media_url"):
        return [post["media_url"]]
    _die(f"tipo de post no soportado para repost: {post.get('media_type')} "
         "(soportados: IMAGE y CAROUSEL_ALBUM).")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Repostear un post de Instagram en la página de Facebook (sin crear álbum).")
    which = ap.add_mutually_exclusive_group()
    which.add_argument("--latest", action="store_true", help="repostear el último post de IG.")
    which.add_argument("--permalink", help="link del post de IG (instagram.com/p/...).")
    which.add_argument("--media-id", help="media id de IG (lo devuelve ig_publish.py).")
    ap.add_argument("--caption", help="override del texto (default: el caption de IG).")
    ap.add_argument("--no-caption", action="store_true", help="publicar sin texto.")
    ap.add_argument("--page-id", help="Override del Page ID de FB.")
    ap.add_argument("--token", help="Override del Page Access Token de FB.")
    ap.add_argument("--dry-run", action="store_true", help="mostrar qué publicaría y salir.")
    args = ap.parse_args()

    ig_id, ig_token = load_ig()
    page_id, page_token = load_credentials(args.page_id, args.token)

    media_id = resolve_media_id(ig_id, ig_token, args.media_id, args.permalink, args.latest)
    post = fetch_ig_post(media_id, ig_token)
    urls = image_urls(post)
    caption = "" if args.no_caption else (args.caption if args.caption is not None
                                          else post.get("caption") or "")

    if args.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "ig_media_id": media_id,
                          "ig_permalink": post.get("permalink"),
                          "caption": caption, "images": urls},
                         ensure_ascii=False, indent=2))
        return

    if len(urls) == 1:
        result = upload_photo(page_id, page_token, urls[0], caption=caption)
    else:
        result = publish_multi_photo_post(page_id, page_token, caption, urls)

    post_id = result.get("post_id") or result.get("id")
    out = {"ok": True, "ig_media_id": media_id, "ig_permalink": post.get("permalink"),
           "result": result}
    if post_id and "_" in str(post_id):
        out["fb_permalink"] = f"https://www.facebook.com/{post_id}"
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
