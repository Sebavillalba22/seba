#!/usr/bin/env python3
"""Publicar en Instagram (foto, video, o carrusel MIXTO) vía Meta Graph API. Stdlib only.

Requiere instagram.json (al lado de SKILL.md):
  {"ig_user_id": "...", "page_id": "...", "access_token": "<page token con IG scopes>"}

⚠️ Instagram exige que las imágenes/videos estén en una URL PÚBLICA (no acepta
archivos locales). Subí los assets a un host público (ej. la biblioteca de
medios de WordPress con wp_upload.py) y pasá las URLs.

El tipo de cada media se detecta por extensión: .mp4/.mov/.m4v → VIDEO, si no IMAGE.
El ORDEN de los --media importa (así queda el carrusel).

Flujo:
  - 1 media   -> crea container -> media_publish
  - 2..10     -> un container por media (is_carousel_item) ->
                 container CAROUSEL (children) -> media_publish

Ejemplos:
  ig_publish.py --caption "Texto" --media https://.../1.jpg
  ig_publish.py --caption "Texto" \
     --media https://.../01.jpg --media https://.../02.mp4 --media https://.../03.jpg
  ig_publish.py --check
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

GRAPH = "https://graph.facebook.com/v21.0"
IG_FILE = Path(__file__).resolve().parent.parent / "instagram.json"

VIDEO_EXTS = (".mp4", ".mov", ".m4v")


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


def _media_type(url: str) -> str:
    path = urllib.parse.urlsplit(url).path.lower()
    return "VIDEO" if path.endswith(VIDEO_EXTS) else "IMAGE"


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


def _wait_ready(container_id: str, token: str, tries: int = 30, delay: int = 2):
    """Espera a que el container quede FINISHED antes de publicar.
    Los VIDEO tardan más en procesar → subir `tries`."""
    for _ in range(tries):
        st = _get(container_id, {"fields": "status_code,status", "access_token": token})
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code == "ERROR":
            _die(f"el container {container_id} quedó en ERROR: {st.get('status')}")
        time.sleep(delay)
    _die(f"timeout esperando el container {container_id}")


def _make_container(ig_id: str, token: str, url: str, carousel_item: bool,
                    caption: str | None = None) -> str:
    """Crea un container de imagen o video y espera a que esté FINISHED."""
    mt = _media_type(url)
    fields = {"access_token": token}
    if carousel_item:
        fields["is_carousel_item"] = "true"
    if caption is not None:
        fields["caption"] = caption
    if mt == "VIDEO":
        fields["media_type"] = "VIDEO"
        fields["video_url"] = url
    else:
        fields["image_url"] = url
    cont = _post(f"{ig_id}/media", fields)
    cid = cont["id"]
    # el video puede tardar bastante en procesar (subida + transcodificación)
    _wait_ready(cid, token, tries=90 if mt == "VIDEO" else 30, delay=2)
    return cid


def check(ig_id: str, token: str):
    info = _get(ig_id, {"fields": "username,followers_count,media_count", "access_token": token})
    print(json.dumps({"ok": True, "ig": info}, ensure_ascii=False, indent=2))


def _latest_media(ig_id: str, token: str) -> dict | None:
    """Último post de la cuenta (permalink + timestamp), sin morir si falla."""
    try:
        r = _get(f"{ig_id}/media", {"fields": "permalink,timestamp", "limit": "1", "access_token": token})
        data = r.get("data", [])
        return data[0] if data else None
    except SystemExit:
        return None


def _recent(ts: str, seconds: int = 180) -> bool:
    try:
        dt = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S%z")
        return (datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds() <= seconds
    except (ValueError, TypeError):
        return False


def media_publish(ig_id: str, token: str, creation_id: str) -> dict:
    """Publica el container. Si Meta devuelve 403 'request limit' DESPUÉS de haber
    publicado (el 403 llega en la respuesta aunque el post se haya creado),
    verifica el feed antes de declarar fallo — así no confundimos 'límite de API'
    con 'no se publicó'."""
    before = _latest_media(ig_id, token)
    before_link = before.get("permalink") if before else None
    data = urllib.parse.urlencode({"creation_id": creation_id, "access_token": token}).encode()
    req = urllib.request.Request(f"{GRAPH}/{ig_id}/media_publish", data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return {"published": json.loads(r.read().decode("utf-8", "replace")), "verified": False}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(body).get("error", {}).get("message", body)
        except json.JSONDecodeError:
            msg = body
        # Verificación: ¿apareció un post NUEVO y reciente? -> el publish sí entró.
        time.sleep(6)
        after = _latest_media(ig_id, token)
        if after and after.get("permalink") != before_link and _recent(after.get("timestamp", "")):
            print(f"  ⚠️ Meta devolvió 403 ({msg[:60]}…) PERO el post se publicó igual. "
                  f"Verificado contra el feed.", file=sys.stderr)
            return {"published": {"permalink": after["permalink"]}, "verified": True}
        _die(f"Graph {e.code}: {msg}  (verificado: el post NO aparece en el feed)")


def publish(ig_id: str, token: str, caption: str, media: list[str], dry_run: bool = False):
    for u in media:
        if not u.startswith(("http://", "https://")):
            _die(f"la media debe ser una URL pública, no: {u}")
    if not media:
        _die("pasá al menos una --media (URL pública).")
    if len(media) > 10:
        _die("Instagram permite hasta 10 elementos por carrusel.")

    kinds = [_media_type(u) for u in media]
    print(f"  {len(media)} media: {', '.join(kinds)}", file=sys.stderr)

    if len(media) == 1:
        creation_id = _make_container(ig_id, token, media[0], carousel_item=False, caption=caption or "")
    else:
        child_ids = []
        for i, u in enumerate(media, 1):
            cid = _make_container(ig_id, token, u, carousel_item=True)
            child_ids.append(cid)
            print(f"  item {i}/{len(media)} listo [{kinds[i-1]}] ({cid})", file=sys.stderr)
        cont = _post(f"{ig_id}/media", {
            "media_type": "CAROUSEL",
            "children": ",".join(child_ids),
            "caption": caption or "",
            "access_token": token,
        })
        creation_id = cont["id"]
        _wait_ready(creation_id, token, tries=90)

    if dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "creation_id": creation_id,
                          "note": "container FINISHED; NO publicado"}, ensure_ascii=False, indent=2))
        return

    res = media_publish(ig_id, token, creation_id)
    pub = res["published"]
    media_id = pub.get("id")
    permalink = pub.get("permalink")
    if media_id and not permalink:
        try:
            permalink = _get(media_id, {"fields": "permalink", "access_token": token}).get("permalink")
        except SystemExit:
            permalink = None
    print(json.dumps({"ok": True, "media_id": media_id, "permalink": permalink,
                      "verified_via_feed": res["verified"]}, ensure_ascii=False, indent=2))


def repost_fb(media_id: str) -> int:
    """Repostea el post recién publicado en la página de FB (fb_repost_ig.py)."""
    script = Path(__file__).resolve().parent / "fb_repost_ig.py"
    print("→ reposteando en Facebook...", file=sys.stderr)
    return subprocess.call([sys.executable, str(script), "--media-id", media_id])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--caption", "-c", default="")
    # --media (o el alias --image / -i): URL pública, repetible, ORDENADA.
    # Imagen o video (.mp4/.mov). argparse preserva el orden de la línea de comandos.
    ap.add_argument("--media", "--image", "-i", dest="media", action="append", default=[],
                    help="URL pública (imagen o video). Repetir para carrusel (2-10). El orden importa.")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="arma el/los container(s) pero NO publica.")
    ap.add_argument("--repost-fb", action="store_true",
                    help="después de publicar en IG, repostear en la página de FB (sin álbum).")
    args = ap.parse_args()
    ig_id, token = load_ig()
    if args.check:
        check(ig_id, token)
    else:
        publish(ig_id, token, args.caption, args.media, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
