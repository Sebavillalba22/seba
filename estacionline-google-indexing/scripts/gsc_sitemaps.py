#!/usr/bin/env python3
"""Gestionar sitemaps en Search Console (Sitemaps API).

Listar los sitemaps enviados y su estado, ver el detalle de uno, o enviar
uno nuevo (por ejemplo el sitemap de noticias). Reenviar el sitemap es una
de las palancas reales para "Detectada: actualmente sin indexar".

Necesita OAuth (corré antes: python3 scripts/gsc_auth.py).

Uso:
  python3 scripts/gsc_sitemaps.py --list
  python3 scripts/gsc_sitemaps.py --details https://estacionline.com/sitemap.xml
  python3 scripts/gsc_sitemaps.py --submit  https://estacionline.com/sitemap.xml
  python3 scripts/gsc_sitemaps.py --submit  https://estacionline.com/news-sitemap.xml
  python3 scripts/gsc_sitemaps.py --list --site https://estacionline.com/

Solo stdlib.
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gsc_common as gc  # noqa: E402


def sitemaps_url(site: str, feed: str | None = None) -> str:
    base = f"{gc.WM_BASE}/sites/{gc.site_path(site)}/sitemaps"
    return f"{base}/{gc.site_path(feed)}" if feed else base


def cmd_list(site: str):
    resp = gc.api("GET", sitemaps_url(site))
    items = resp.get("sitemap", [])
    if not items:
        print("No hay sitemaps enviados para", site)
        return
    print(f"\nSitemaps en {site}:\n" + "-" * 68)
    for s in items:
        contents = s.get("contents", [])
        submitted = sum(int(c.get("submitted", 0)) for c in contents)
        indexed = sum(int(c.get("indexed", 0)) for c in contents)
        print(f"  {s.get('path')}")
        print(f"     enviado: {s.get('lastSubmitted', '?')}   "
              f"descargado: {s.get('lastDownloaded', 'nunca')}")
        print(f"     pendiente: {s.get('isPending')}   errores: {s.get('errors', 0)}   "
              f"warnings: {s.get('warnings', 0)}")
        if contents:
            print(f"     URLs enviadas: {submitted}"
                  + (f"   indexadas (histórico): {indexed}" if indexed else ""))
        print()


def cmd_details(site: str, feed: str):
    s = gc.api("GET", sitemaps_url(site, feed))
    print(f"\nDetalle de {feed}:\n" + "-" * 68)
    for k in ("path", "lastSubmitted", "lastDownloaded", "isPending",
              "isSitemapsIndex", "type", "errors", "warnings"):
        if k in s:
            print(f"  {k}: {s[k]}")
    for c in s.get("contents", []):
        print(f"  contenido [{c.get('type')}]: enviadas={c.get('submitted')} "
              f"indexadas={c.get('indexed')}")


def cmd_submit(site: str, feed: str):
    gc.api("PUT", sitemaps_url(site, feed))  # 200 sin cuerpo = OK
    print(f"✅ Sitemap enviado: {feed}")
    print("   (Google puede tardar en descargarlo; verificá con --details más tarde.)")


def main():
    ap = argparse.ArgumentParser(description="Sitemaps de Search Console.")
    ap.add_argument("--site", default=gc.DEFAULT_SITE, help=f"propiedad (def. {gc.DEFAULT_SITE})")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true", help="listar sitemaps y estado")
    g.add_argument("--details", metavar="URL", help="detalle de un sitemap")
    g.add_argument("--submit", metavar="URL", help="enviar/reenviar un sitemap")
    args = ap.parse_args()

    if args.list:
        cmd_list(args.site)
    elif args.details:
        cmd_details(args.site, args.details)
    elif args.submit:
        cmd_submit(args.site, args.submit)


if __name__ == "__main__":
    main()
