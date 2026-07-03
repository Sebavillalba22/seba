#!/usr/bin/env python3
"""Postear a cualquiera de las páginas configuradas en pages.json, por nombre o id.

Multiplataforma (Windows / macOS / Linux). Resuelve el token desde pages.json
y delega en publish.py.

Ejemplos:
  python scripts/publish_to.py --page estacionline --message "Título\n\nBajada" --link https://...
  python scripts/publish_to.py --page funes --message "..." --link https://...
  python scripts/publish_to.py --page "Puerto Timbúes" --message "..." --image https://.../foto.jpg
  python scripts/publish_to.py --page funes --message "..." --image https://.../1.jpg --image https://.../2.jpg
  python scripts/publish_to.py --list          # muestra las páginas disponibles
  python scripts/publish_to.py --page roldan --check

Con varias --image (2-10) publica UN solo posteo con las fotos adjuntas
(estilo repost de carrusel de IG) — nunca crea un álbum.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES_FILE = ROOT / "pages.json"
PUBLISH = Path(__file__).resolve().parent / "publish.py"


def load_pages() -> dict:
    if not PAGES_FILE.exists():
        sys.exit(f"ERROR: no encuentro {PAGES_FILE}. Copiá pages.json al lado de SKILL.md.")
    return json.loads(PAGES_FILE.read_text(encoding="utf-8"))


def resolve(pages: dict, query: str):
    q = query.strip().lower()
    if q in pages:  # exact id
        return q, pages[q]
    matches = [(pid, info) for pid, info in pages.items() if q in info.get("name", "").lower()]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        sys.exit(f"ERROR: ninguna página coincide con {query!r}. Usá --list para ver las opciones.")
    names = ", ".join(f"{info['name']} ({pid})" for pid, info in matches)
    sys.exit(f"ERROR: {query!r} es ambiguo: {names}. Usá el id exacto.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", help="id exacto o parte del nombre (ej. 'funes', 'estacionline').")
    ap.add_argument("--message", "-m")
    ap.add_argument("--image", "-i", action="append", default=[],
                    help="ruta/URL de imagen; repetir para varias fotos en un solo post (2-10).")
    ap.add_argument("--link", "-l")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--first-comment", help="texto/link como primer comentario del post.")
    ap.add_argument("--list", action="store_true", help="listar páginas configuradas y salir.")
    args = ap.parse_args()

    pages = load_pages()
    if args.list:
        for pid, info in pages.items():
            print(f"  {pid}  {info.get('name')}")
        return
    if not args.page:
        sys.exit("ERROR: falta --page (o usá --list).")

    pid, info = resolve(pages, args.page)
    cmd = [sys.executable, str(PUBLISH), "--page-id", pid, "--token", info["access_token"]]
    if args.check:
        cmd.append("--check")
    else:
        if args.message:
            cmd += ["--message", args.message]
        for image in args.image:
            cmd += ["--image", image]
        if args.link:
            cmd += ["--link", args.link]
        if args.first_comment:
            cmd += ["--first-comment", args.first_comment]
    sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
