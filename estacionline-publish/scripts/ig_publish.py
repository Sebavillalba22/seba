#!/usr/bin/env python3
"""Publicar en Instagram (foto única o carrusel) vía Meta Graph API. Stdlib only.

Requiere instagram.json (al lado de SKILL.md):
  {"ig_user_id": "...", "page_id": "...", "access_token": "<page token con IG scopes>"}

⚠️ Instagram exige que las imágenes estén en una URL PÚBLICA (no acepta
archivos locales). Subí las imágenes a un host público (ej. la biblioteca de
medios de WordPress) y pasá las URLs.

Flujo:
  - 1 imagen  -> crea container -> media_publish
  - 2..10 img -> crea un container por imagen (is_carousel_item) ->
                 container CAROUSEL (children) -> media_publish

Ejemplos:
  ig_publish.py --caption "Texto" --image https://.../1.jpg
  ig_publish.py --caption "Texto" --image https://.../1.jpg --image https://.../2.jpg --image https://.../3.jpg
  ig_publish.py --caption "Texto" --image https://.../1.jpg --image https://.../2.jpg --repost-fb
  ig_publish.py --check

Con --repost-fb, después de publicar en IG repostea el mismo post en la
página de Facebook (un solo posteo con las fotos adjuntas, SIN álbum),
como el crosspost automático del teléfono. Delega en fb_repost_ig.py.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

GRAPH = "https://graph.facebook.com/v21.0"
IG_FILE = Path(__file__).resolve().parent.parent / "instagram.json"


def _die(msg: str):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load_ig():
    if not IG_FILE.exists():
        _die(f"No existe {IG_FILE}. Falta configurar Instagram.")
    d = json.loads(IG_FILE.read_text(encoding="utf-8"))
    if not d.get("ig_user_id") or not d.get("access_token"):
        _die("instagram.json incompleto (ig_user_id / access_token).")
    return d["ig_user_id"], d["access_token"]


def _post(path: str, fields: dict) -> dict:
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(f"{GRAPH}/{path}", data=data, method="POST")
    return _do(req)


def _get(path: str, params: dict) -> dict:
    url = f"{GRAPH}/{path}?" + urllib.parse.urlencode(params)
    return _do(urllib.request.Request(url, method="GET"))


def _do(req) -> dict:
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(body).get("error", {}).get("message", body)
        except json.JSONDecodeError:
            msg = body
        _die(f"Graph {e.code}: {msg}")
    except urllib.error.URLError as e:
        _die(f"conexión: {e.reason}")


def _wait_ready(container_id: str, token: str, tries: int = 30):
    """Espera a que el container quede FINISHED antes de publicar."""
    for _ in range(tries):
        st = _get(container_id, {"fields": "status_code", "access_token": token})
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code == "ERROR":
            _die(f"el container {container_id} quedó en ERROR")
        time.sleep(2)
    _die(f"timeout esperando el container {container_id}")


def check(ig_id: str, token: str):
    info = _get(ig_id, {"fields": "username,followers_count,media_count", "access_token": token})
    print(json.dumps({"ok": True, "ig": info}, ensure_ascii=False, indent=2))


def publish(ig_id: str, token: str, caption: str, images: list[str], dry_run: bool = False):
    for u in images:
        if not u.startswith(("http://", "https://")):
            _die(f"la imagen debe ser una URL pública, no: {u}")
    if not images:
        _die("pasá al menos una --image (URL pública).")
    if len(images) > 10:
        _die("Instagram permite hasta 10 imágenes por carrusel.")

    if len(images) == 1:
        cont = _post(f"{ig_id}/media", {"image_url": images[0], "caption": caption or "", "access_token": token})
        creation_id = cont["id"]
        _wait_ready(creation_id, token)
    else:
        child_ids = []
        for i, u in enumerate(images, 1):
            c = _post(f"{ig_id}/media", {"image_url": u, "is_carousel_item": "true", "access_token": token})
            _wait_ready(c["id"], token)
            child_ids.append(c["id"])
            print(f"  item {i}/{len(images)} listo ({c['id']})", file=sys.stderr)
        cont = _post(f"{ig_id}/media", {
            "media_type": "CAROUSEL",
            "children": ",".join(child_ids),
            "caption": caption or "",
            "access_token": token,
        })
        creation_id = cont["id"]
        _wait_ready(creation_id, token)

    if dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "creation_id": creation_id,
                          "note": "container FINISHED; NO publicado"}, ensure_ascii=False, indent=2))
        return None

    pub = _post(f"{ig_id}/media_publish", {"creation_id": creation_id, "access_token": token})
    media_id = pub.get("id")
    perma = _get(media_id, {"fields": "permalink", "access_token": token}) if media_id else {}
    print(json.dumps({"ok": True, "media_id": media_id, "permalink": perma.get("permalink")},
                     ensure_ascii=False, indent=2))
    return media_id


def repost_fb(media_id: str) -> int:
    """Repostea el post recién publicado en la página de FB (fb_repost_ig.py)."""
    script = Path(__file__).resolve().parent / "fb_repost_ig.py"
    print("→ reposteando en Facebook...", file=sys.stderr)
    return subprocess.call([sys.executable, str(script), "--media-id", media_id])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--caption", "-c", default="")
    ap.add_argument("--image", "-i", action="append", default=[], help="URL pública. Repetir para carrusel (2-10).")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="arma el container pero NO publica.")
    ap.add_argument("--repost-fb", action="store_true",
                    help="después de publicar en IG, repostear en la página de FB (sin álbum).")
    args = ap.parse_args()
    ig_id, token = load_ig()
    if args.check:
        check(ig_id, token)
    else:
        media_id = publish(ig_id, token, args.caption, args.image, dry_run=args.dry_run)
        if args.repost_fb and media_id:
            sys.exit(repost_fb(media_id))


if __name__ == "__main__":
    main()
