#!/usr/bin/env python3
"""Publicar / crear posts en WordPress (estacionline.com) vía la API REST. Stdlib only.

Autenticación por Application Password (Usuarios -> Perfil -> Contraseñas de
aplicación en wp-admin). Credenciales en wordpress.json (al lado de SKILL.md):

  {
    "site": "https://estacionline.com",
    "user": "tu_usuario_wp",
    "app_password": "xxxx xxxx xxxx xxxx xxxx xxxx"
  }

Uso:
  wp_publish.py --check                                  # verifica auth (whoami)
  wp_publish.py --title "Título" --content "<p>HTML</p>" # crea BORRADOR
  wp_publish.py --title "..." --content "..." --publish  # publica directo
  wp_publish.py --title "..." --content "..." --image "https://.../foto.jpg" --publish
  wp_publish.py --title "..." --content-file nota.html --status draft
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CRED_FILE = ROOT / "wordpress.json"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def load_creds() -> dict:
    if not CRED_FILE.exists():
        sys.exit(f"ERROR: no encuentro {CRED_FILE}. Copiá wordpress.json al lado de SKILL.md.")
    c = json.loads(CRED_FILE.read_text(encoding="utf-8"))
    c["site"] = c.get("site", "https://estacionline.com").rstrip("/")
    return c


def _auth_header(creds: dict) -> str:
    raw = f"{creds['user']}:{creds['app_password']}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def _req(method: str, url: str, creds: dict, data: bytes | None = None,
         headers: dict | None = None) -> tuple[int, dict]:
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", _auth_header(creds))
    req.add_header("User-Agent", UA)  # Cloudflare/Donweb rechazan UA de bots
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req) as r:
            body = r.read().decode("utf-8", "replace")
            return r.status, (json.loads(body) if body else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"raw": raw[:500]}
        return e.code, payload


def check(creds: dict) -> None:
    code, payload = _req("GET", f"{creds['site']}/wp-json/wp/v2/users/me?context=edit", creds)
    if code == 200:
        print(json.dumps({"ok": True, "user": {
            "id": payload.get("id"), "name": payload.get("name"),
            "slug": payload.get("slug"), "roles": payload.get("roles"),
        }}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"ok": False, "http": code, "error": payload}, ensure_ascii=False, indent=2))
        sys.exit(1)


def upload_media(creds: dict, image_url: str) -> int:
    """Baja una imagen de una URL pública y la sube a la biblioteca. Devuelve el media id."""
    dl = urllib.request.Request(image_url, headers={"User-Agent": UA})
    with urllib.request.urlopen(dl) as r:
        img = r.read()
    fname = image_url.rsplit("/", 1)[-1].split("?")[0] or "imagen.jpg"
    ctype = mimetypes.guess_type(fname)[0] or "image/jpeg"
    code, payload = _req(
        "POST", f"{creds['site']}/wp-json/wp/v2/media", creds, data=img,
        headers={"Content-Type": ctype, "Content-Disposition": f'attachment; filename="{fname}"'},
    )
    if code not in (200, 201):
        sys.exit(f"ERROR subiendo imagen HTTP {code}: {json.dumps(payload, ensure_ascii=False)}")
    return payload["id"]


def publish(creds: dict, title: str, content: str, status: str,
            image_url: str | None, dry_run: bool) -> None:
    body = {"title": title, "content": content, "status": status}
    if image_url and not dry_run:
        body["featured_media"] = upload_media(creds, image_url)

    if dry_run:
        if image_url:
            body["_image_url"] = image_url
        print(json.dumps({"dry_run": True, "post": body}, ensure_ascii=False, indent=2))
        return

    code, payload = _req(
        "POST", f"{creds['site']}/wp-json/wp/v2/posts", creds,
        data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json"},
    )
    if code in (200, 201):
        print(json.dumps({"ok": True, "id": payload.get("id"),
                          "status": payload.get("status"),
                          "link": payload.get("link")}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"ok": False, "http": code, "error": payload}, ensure_ascii=False, indent=2))
        sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--title")
    ap.add_argument("--content", help="HTML del cuerpo.")
    ap.add_argument("--content-file", help="archivo con el HTML del cuerpo.")
    ap.add_argument("--image", help="URL pública de la imagen destacada.")
    ap.add_argument("--status", default="draft", choices=["draft", "publish", "pending", "private"])
    ap.add_argument("--publish", action="store_true", help="atajo de --status publish.")
    ap.add_argument("--check", action="store_true", help="verifica auth (whoami).")
    ap.add_argument("--dry-run", action="store_true", help="no crea nada, muestra el body.")
    args = ap.parse_args()

    creds = load_creds()
    if args.check:
        check(creds)
        return
    if not args.title:
        sys.exit("ERROR: falta --title.")
    content = args.content
    if args.content_file:
        content = Path(args.content_file).read_text(encoding="utf-8")
    if content is None:
        sys.exit("ERROR: falta --content o --content-file.")
    status = "publish" if args.publish else args.status
    publish(creds, args.title, content, status, args.image, args.dry_run)


if __name__ == "__main__":
    main()
