#!/usr/bin/env python3
"""Subir una imagen a la biblioteca de medios de WordPress (REST API) y
devolver su URL pública. Instagram exige URLs públicas; este script evita
tener que subir las slides a mano.

Requiere wordpress.json (al lado de SKILL.md):
  {
    "base_url": "https://estacionline.com",
    "username": "usuario_wp",
    "app_password": "xxxx xxxx xxxx xxxx xxxx xxxx"
  }

El app_password se genera en wp-admin → Usuarios → Perfil →
"Contraseñas de aplicación" (NO es la contraseña normal del usuario).

Uso:
  wp_upload.py /ruta/slide1.jpg [/ruta/slide2.jpg ...]
"""
from __future__ import annotations

import base64
import json
import mimetypes
import sys
import urllib.error
import urllib.request
from pathlib import Path

WP_FILE = Path(__file__).resolve().parent.parent / "wordpress.json"


def _die(msg: str):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load_wp() -> tuple[str, str, str]:
    if not WP_FILE.exists():
        _die(f"no existe {WP_FILE} (ver wordpress.example.json).")
    d = json.loads(WP_FILE.read_text(encoding="utf-8"))
    for k in ("base_url", "username", "app_password"):
        if not d.get(k):
            _die(f"wordpress.json incompleto: falta {k}")
    return d["base_url"].rstrip("/"), d["username"], d["app_password"]


def upload(path: Path) -> str:
    """Sube el archivo y devuelve la URL pública (source_url)."""
    base, user, pw = load_wp()
    path = path.expanduser()
    if not path.is_file():
        _die(f"no existe el archivo: {path}")
    ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    auth = base64.b64encode(f"{user}:{pw}".encode()).decode()
    req = urllib.request.Request(
        f"{base}/wp-json/wp/v2/media",
        data=path.read_bytes(),
        method="POST",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": ctype,
            "Content-Disposition": f'attachment; filename="{path.name}"',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            body = json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(raw).get("message", raw)
        except json.JSONDecodeError:
            msg = raw
        _die(f"WordPress {e.code}: {msg}")
    except urllib.error.URLError as e:
        _die(f"conexión con WordPress: {e.reason}")
    url = body.get("source_url")
    if not url:
        _die(f"WordPress no devolvió source_url: {body}")
    return url


def main() -> None:
    if len(sys.argv) < 2:
        _die("uso: wp_upload.py archivo1.jpg [archivo2.jpg ...]")
    urls = [upload(Path(p)) for p in sys.argv[1:]]
    print(json.dumps({"ok": True, "urls": urls}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
