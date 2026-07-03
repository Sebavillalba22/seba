#!/usr/bin/env python3
"""Publish to a Facebook Page via the Meta Graph API. Stdlib only.

Credentials are read, in order of precedence, from:
  1. CLI flags   --page-id / --token
  2. Env vars    FB_PAGE_ID / FB_PAGE_ACCESS_TOKEN
  3. JSON file   ~/.claude/skills/facebook-publish/.credentials.json
                 {"page_id": "...", "access_token": "..."}

Usage examples
--------------
  # plain text post
  publish.py --message "Hola Funes"

  # text + local photo
  publish.py --message "Mirá esto" --image /ruta/foto.jpg

  # text + photo from a URL
  publish.py --message "Mirá esto" --image https://.../foto.jpg

  # several photos in ONE feed post (2-10) — repost estilo carrusel de IG.
  # NO crea ningún álbum: sube cada foto sin publicar y las adjunta a un
  # único posteo con attached_media.
  publish.py --message "Mirá esto" --image https://.../1.jpg --image https://.../2.jpg

  # share a link (link preview card)
  publish.py --message "Nota nueva" --link https://estacionline.com/...

  # verify the token works and print the page name
  publish.py --check
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

GRAPH_VERSION = "v21.0"
GRAPH = f"https://graph.facebook.com/{GRAPH_VERSION}"
CRED_FILE = Path(__file__).resolve().parent.parent / ".credentials.json"

MAX_PHOTOS_PER_POST = 10  # mismo tope que el carrusel de IG


# ─────────────────────────── credentials ───────────────────────────

def load_credentials(cli_page_id: str | None, cli_token: str | None) -> tuple[str, str]:
    page_id = cli_page_id or os.environ.get("FB_PAGE_ID")
    token = cli_token or os.environ.get("FB_PAGE_ACCESS_TOKEN")
    if (not page_id or not token) and CRED_FILE.exists():
        try:
            data = json.loads(CRED_FILE.read_text(encoding="utf-8"))
            page_id = page_id or data.get("page_id")
            token = token or data.get("access_token")
        except (json.JSONDecodeError, OSError) as e:
            _die(f"No pude leer {CRED_FILE}: {e}")
    if not token:
        _die(
            "Falta el Page Access Token. Definí FB_PAGE_ACCESS_TOKEN, pasá "
            f"--token, o creá {CRED_FILE} con {{\"page_id\":..., \"access_token\":...}}."
        )
    if not page_id:
        _die("Falta el Page ID. Definí FB_PAGE_ID, pasá --page-id, o ponelo en el archivo de credenciales.")
    return page_id, token


# ─────────────────────────── HTTP helpers ──────────────────────────

def _die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def _read_response(resp) -> dict:
    raw = resp.read().decode("utf-8", errors="replace")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_raw": raw}


def _post_urlencoded(url: str, fields: dict) -> dict:
    data = urllib.parse.urlencode(fields).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    return _do(req)


def _post_multipart(url: str, fields: dict, file_path: Path) -> dict:
    boundary = f"----claudefb{uuid.uuid4().hex}"
    ctype = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    body = bytearray()
    for key, value in fields.items():
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode()
        body += f"{value}\r\n".encode()
    body += f"--{boundary}\r\n".encode()
    body += (
        f'Content-Disposition: form-data; name="source"; '
        f'filename="{file_path.name}"\r\n'
    ).encode()
    body += f"Content-Type: {ctype}\r\n\r\n".encode()
    body += file_path.read_bytes()
    body += f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(url, data=bytes(body), method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    return _do(req)


def _get(url: str) -> dict:
    return _do(urllib.request.Request(url, method="GET"))


def _do(req) -> dict:
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return _read_response(resp)
    except urllib.error.HTTPError as e:
        payload = _read_response(e)
        err = payload.get("error", {}) if isinstance(payload, dict) else {}
        msg = err.get("message") or payload
        _die(f"Graph API {e.code}: {msg}")
    except urllib.error.URLError as e:
        _die(f"No pude conectar con Graph API: {e.reason}")


# ─────────────────────────── actions ───────────────────────────────

def check(page_id: str, token: str) -> None:
    info = _get(f"{GRAPH}/{page_id}?fields=id,name,fan_count&access_token={urllib.parse.quote(token)}")
    print(json.dumps({"ok": True, "page": info}, ensure_ascii=False, indent=2))


def post_status(post_id: str, token: str) -> None:
    """Diagnóstico de un post: ¿existe? ¿está publicado/oculto/restringido?
    Si la Graph API responde 'does not exist', Facebook lo eliminó (spam,
    integridad o contenido duplicado)."""
    fields = ("id,is_published,is_hidden,is_expired,created_time,permalink_url,"
              "privacy,status_type,message,scheduled_publish_time,"
              "attachments{media_type,subattachments}")
    info = _get(f"{GRAPH}/{post_id}?fields={urllib.parse.quote(fields)}"
                f"&access_token={urllib.parse.quote(token)}")
    print(json.dumps({"ok": True, "post": info}, ensure_ascii=False, indent=2))


def list_feed(page_id: str, token: str, limit: int = 10) -> None:
    """Últimos posts del feed de la página, para ver qué está visible."""
    fields = "id,created_time,is_published,is_hidden,permalink_url,status_type,message"
    info = _get(f"{GRAPH}/{page_id}/feed?limit={limit}"
                f"&fields={urllib.parse.quote(fields)}"
                f"&access_token={urllib.parse.quote(token)}")
    print(json.dumps({"ok": True, "feed": info.get("data", info)}, ensure_ascii=False, indent=2))


def comment_on_post(post_id: str, token: str, text: str) -> dict:
    """Agrega un comentario a un post de la página (requiere pages_manage_engagement)."""
    return _post_urlencoded(
        f"{GRAPH}/{post_id}/comments",
        {"access_token": token, "message": text},
    )


def upload_photo(page_id: str, token: str, image: str,
                 caption: str | None = None, published: bool = True) -> dict:
    """Sube una foto a /{page-id}/photos. Con published=False queda 'unpublished'
    (sin post propio) lista para adjuntar a un post de feed con attached_media."""
    url = f"{GRAPH}/{page_id}/photos"
    fields: dict = {"access_token": token}
    if caption:
        fields["caption"] = caption
    if not published:
        fields["published"] = "false"
    if image.startswith(("http://", "https://")):
        fields["url"] = image
        return _post_urlencoded(url, fields)
    p = Path(image).expanduser()
    if not p.is_file():
        _die(f"No existe la imagen: {p}")
    return _post_multipart(url, fields, p)


def publish_multi_photo_post(page_id: str, token: str, message: str | None,
                             images: list[str]) -> dict:
    """UN solo posteo de feed con varias fotos adjuntas (equivalente nativo de FB
    al repost de un carrusel de IG). No crea ningún álbum ni posts sueltos:
    sube cada foto con published=false y las adjunta via attached_media."""
    if len(images) > MAX_PHOTOS_PER_POST:
        _die(f"Máximo {MAX_PHOTOS_PER_POST} fotos por posteo (recibí {len(images)}).")
    photo_ids: list[str] = []
    for i, image in enumerate(images, 1):
        r = upload_photo(page_id, token, image, published=False)
        pid = r.get("id")
        if not pid:
            _die(f"la foto {i}/{len(images)} no devolvió id: {r}")
        photo_ids.append(pid)
        print(f"  foto {i}/{len(images)} subida ({pid})", file=sys.stderr)
    fields = {"access_token": token, "message": message or ""}
    for i, pid in enumerate(photo_ids):
        fields[f"attached_media[{i}]"] = json.dumps({"media_fbid": pid})
    return _post_urlencoded(f"{GRAPH}/{page_id}/feed", fields)


def publish(page_id: str, token: str, message: str | None,
            images: list[str], link: str | None,
            first_comment: str | None = None) -> None:
    if not message and not images and not link:
        _die("Nada para publicar: pasá --message, --image y/o --link.")
    if images and link:
        _die("--image y --link no van juntos: elegí uno.")

    if len(images) > 1:
        result = publish_multi_photo_post(page_id, token, message, images)
    elif len(images) == 1:
        result = upload_photo(page_id, token, images[0], caption=message)
    else:
        fields = {"access_token": token, "message": message or ""}
        if link:
            fields["link"] = link
        result = _post_urlencoded(f"{GRAPH}/{page_id}/feed", fields)

    post_id = result.get("post_id") or result.get("id")
    out = {"ok": True, "result": result}
    if post_id and "_" in str(post_id):
        # post_id form is "{pageid}_{postid}" → build a permalink.
        out["permalink"] = f"https://www.facebook.com/{post_id}"
    if first_comment and post_id:
        c = comment_on_post(post_id, token, first_comment)
        out["first_comment"] = {"id": c.get("id")}
    print(json.dumps(out, ensure_ascii=False, indent=2))


# ─────────────────────────── CLI ───────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="Publish to a Facebook Page (Graph API).")
    ap.add_argument("--message", "-m", help="Texto del posteo / caption de la foto.")
    ap.add_argument("--image", "-i", action="append", default=[],
                    help="Ruta local o URL de una imagen. Repetir para varias fotos "
                         "en UN solo post (2-10, estilo repost de carrusel de IG).")
    ap.add_argument("--link", "-l", help="URL a compartir (tarjeta de link).")
    ap.add_argument("--page-id", help="Override del Page ID.")
    ap.add_argument("--token", help="Override del Page Access Token.")
    ap.add_argument("--check", action="store_true", help="Verificar credenciales y salir.")
    ap.add_argument("--first-comment", help="Texto/link a dejar como primer comentario del post.")
    ap.add_argument("--post-status", metavar="POST_ID",
                    help="Diagnóstico de un post (¿existe? ¿publicado? ¿oculto?) y salir.")
    ap.add_argument("--list-feed", action="store_true",
                    help="Listar los últimos 10 posts del feed de la página y salir.")
    args = ap.parse_args()

    page_id, token = load_credentials(args.page_id, args.token)
    if args.check:
        check(page_id, token)
    elif args.post_status:
        post_status(args.post_status, token)
    elif args.list_feed:
        list_feed(page_id, token)
    else:
        publish(page_id, token, args.message, args.image, args.link,
                first_comment=args.first_comment)


if __name__ == "__main__":
    main()
