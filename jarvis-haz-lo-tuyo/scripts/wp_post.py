#!/usr/bin/env python3
"""Crear/buscar notas en WordPress (REST API). Stdlib only.

⚠️ Este script es el RESPALDO técnico para el paso web de «jarvis haz lo
tuyo». Si existe una skill de publicación web de Estacionline instalada,
USAR ESA SKILL — este script queda para cuando esa skill no está disponible
o como herramienta de búsqueda de duplicados.

Requiere wordpress.json (al lado de SKILL.md):
  {"base_url": "https://estacionline.com", "username": "...", "app_password": "..."}

Uso:
  # buscar posibles duplicados antes de crear la nota
  wp_post.py --find "cristina libre funes"

  # crear la nota (borrador por defecto; el cuerpo HTML va en un archivo)
  wp_post.py --title "Título periodístico" \
    --excerpt "Bajada de la nota" \
    --content-file nota.html \
    --slug "cristina-libre-funes" \
    --category "Política" --tag "Funes" --tag "Cristina" \
    --featured-image portada.jpg \
    --status draft

  --status draft|pending|publish  (default: draft — respetar el flujo habitual)
Salida: JSON con id, link, status.
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

WP_FILE = Path(__file__).resolve().parent.parent / "wordpress.json"


def _die(msg: str):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load_wp() -> tuple[str, str]:
    if not WP_FILE.exists():
        _die(f"no existe {WP_FILE} (ver wordpress.example.json).")
    d = json.loads(WP_FILE.read_text(encoding="utf-8"))
    for k in ("base_url", "username", "app_password"):
        if not d.get(k):
            _die(f"wordpress.json incompleto: falta {k}")
    auth = base64.b64encode(f"{d['username']}:{d['app_password']}".encode()).decode()
    return d["base_url"].rstrip("/"), auth


def _req(base: str, auth: str, path: str, method: str = "GET",
         payload: dict | None = None) -> dict | list:
    url = f"{base}/wp-json/wp/v2/{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(raw).get("message", raw)
        except json.JSONDecodeError:
            msg = raw
        _die(f"WordPress {e.code} en {path}: {msg}")
    except urllib.error.URLError as e:
        _die(f"conexión con WordPress: {e.reason}")


def find_posts(base: str, auth: str, query: str) -> list[dict]:
    """Busca notas por texto (título/contenido) para detectar duplicados.
    Incluye borradores y pendientes además de publicadas."""
    out: list[dict] = []
    for status in ("publish", "draft", "pending", "future"):
        res = _req(base, auth, f"posts?search={urllib.parse.quote(query)}"
                               f"&status={status}&per_page=10&_fields=id,link,slug,status,date,title")
        if isinstance(res, list):
            out.extend(res)
    return out


def term_id(base: str, auth: str, kind: str, name: str) -> int:
    """Resuelve categoría/etiqueta por nombre; la crea si no existe."""
    res = _req(base, auth, f"{kind}?search={urllib.parse.quote(name)}&per_page=10")
    for t in res if isinstance(res, list) else []:
        if t.get("name", "").strip().lower() == name.strip().lower():
            return t["id"]
    created = _req(base, auth, kind, "POST", {"name": name})
    return created["id"]


def upload_featured(base: str, auth: str, image: str) -> int:
    """Sube la imagen destacada (ruta local o URL) y devuelve su media id."""
    if image.startswith(("http://", "https://")):
        raw = urllib.request.urlopen(image, timeout=120).read()
        name = urllib.parse.urlsplit(image).path.rsplit("/", 1)[-1] or "portada.jpg"
    else:
        p = Path(image).expanduser()
        if not p.is_file():
            _die(f"no existe la imagen destacada: {p}")
        raw, name = p.read_bytes(), p.name
    import mimetypes
    ctype = mimetypes.guess_type(name)[0] or "image/jpeg"
    req = urllib.request.Request(f"{base}/wp-json/wp/v2/media", data=raw, method="POST", headers={
        "Authorization": f"Basic {auth}",
        "Content-Type": ctype,
        "Content-Disposition": f'attachment; filename="{name}"',
    })
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())["id"]
    except urllib.error.HTTPError as e:
        _die(f"WordPress {e.code} subiendo portada: {e.read().decode('utf-8', 'replace')[:300]}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Crear/buscar notas en WordPress (respaldo de jarvis).")
    ap.add_argument("--find", metavar="TEXTO", help="buscar notas existentes (dup check) y salir.")
    ap.add_argument("--title")
    ap.add_argument("--excerpt", default="")
    ap.add_argument("--content-file", help="archivo con el cuerpo HTML de la nota (incluido el embed de IG).")
    ap.add_argument("--slug")
    ap.add_argument("--category", action="append", default=[])
    ap.add_argument("--tag", action="append", default=[])
    ap.add_argument("--featured-image", help="portada: ruta local o URL.")
    ap.add_argument("--status", default="draft", choices=["draft", "pending", "publish"])
    args = ap.parse_args()

    base, auth = load_wp()

    if args.find:
        posts = find_posts(base, auth, args.find)
        print(json.dumps({"ok": True, "query": args.find, "matches": posts},
                         ensure_ascii=False, indent=2))
        return

    if not args.title or not args.content_file:
        _die("faltan --title y/o --content-file (o usá --find).")
    content = Path(args.content_file).read_text(encoding="utf-8")

    payload: dict = {"title": args.title, "content": content, "status": args.status}
    if args.excerpt:
        payload["excerpt"] = args.excerpt
    if args.slug:
        payload["slug"] = args.slug
    if args.category:
        payload["categories"] = [term_id(base, auth, "categories", c) for c in args.category]
    if args.tag:
        payload["tags"] = [term_id(base, auth, "tags", t) for t in args.tag]
    if args.featured_image:
        payload["featured_media"] = upload_featured(base, auth, args.featured_image)

    post = _req(base, auth, "posts", "POST", payload)
    print(json.dumps({"ok": True, "id": post.get("id"), "link": post.get("link"),
                      "status": post.get("status"), "slug": post.get("slug")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
