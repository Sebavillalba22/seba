#!/usr/bin/env python3
"""Herramientas de sitemap SIN API de Google (solo descarga el XML).

Expande sitemaps (incluye índices anidados y .gz), lista todas las URLs, y
cruza contra una lista propia para encontrar huecos de descubribilidad
(URLs que no están en el sitemap → candidatas a "Detectada: sin indexar").

Uso:
  # listar todas las URLs del sitemap (expande sub-sitemaps)
  python3 scripts/sitemap_tools.py --list https://estacionline.com/sitemap.xml

  # volcarlas a un archivo (para después auditarlas o inspeccionarlas)
  python3 scripts/sitemap_tools.py --list https://estacionline.com/sitemap.xml --out urls.txt

  # qué URLs de mi lista NO están en el sitemap
  python3 scripts/sitemap_tools.py --diff https://estacionline.com/sitemap.xml --file urls.txt

  # descubrir el/los sitemap(s) declarados en robots.txt
  python3 scripts/sitemap_tools.py --from-robots https://estacionline.com

Solo stdlib.
"""
from __future__ import annotations

import argparse
import gzip
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def _die(msg: str):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def fetch(url: str, ua: str, timeout: float = 30.0) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        _die(f"{url} → HTTP {e.code}")
    except urllib.error.URLError as e:
        _die(f"{url} → {getattr(e, 'reason', e)}")


def norm(u: str) -> str:
    p = urllib.parse.urlsplit(u.strip())
    host = p.netloc.lower()
    path = p.path or "/"
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    return urllib.parse.urlunsplit(((p.scheme or "https").lower(), host, path, p.query, ""))


def expand(url: str, ua: str, seen=None) -> list[str]:
    if seen is None:
        seen = set()
    if url in seen:
        return []
    seen.add(url)
    body = fetch(url, ua)
    if url.endswith(".gz") or body[:2] == b"\x1f\x8b":
        try:
            body = gzip.decompress(body)
        except OSError:
            pass
    text = body.decode("utf-8", "replace")
    locs = [m.strip() for m in re.findall(r"<loc>\s*(.*?)\s*</loc>", text, re.I | re.S)]
    if "<sitemapindex" in text.lower():
        out: list[str] = []
        for sm in locs:
            out.extend(expand(sm, ua, seen))
        return out
    return locs


def sitemaps_from_robots(base: str, ua: str) -> list[str]:
    body = fetch(urllib.parse.urljoin(base, "/robots.txt"), ua)
    text = body.decode("utf-8", "replace")
    return [line.split(":", 1)[1].strip()
            for line in text.splitlines()
            if line.strip().lower().startswith("sitemap:")]


def main():
    ap = argparse.ArgumentParser(description="Herramientas de sitemap sin API.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", metavar="SITEMAP", help="listar URLs del sitemap")
    g.add_argument("--diff", metavar="SITEMAP", help="URLs de --file que faltan en el sitemap")
    g.add_argument("--from-robots", metavar="BASE", help="mostrar sitemaps de robots.txt")
    ap.add_argument("--file", help="archivo de URLs (para --diff)")
    ap.add_argument("--out", help="guardar la lista de URLs en un archivo")
    ap.add_argument("--ua", default=DEFAULT_UA)
    args = ap.parse_args()

    if args.from_robots:
        sms = sitemaps_from_robots(args.from_robots, args.ua)
        if not sms:
            print("robots.txt no declara ningún sitemap.")
        for s in sms:
            print(s)
        return

    if args.list:
        urls = expand(args.list, args.ua)
        print(f"# {len(urls)} URLs en {args.list}", file=sys.stderr)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write("\n".join(urls) + "\n")
            print(f"Guardado en {args.out}", file=sys.stderr)
        else:
            for u in urls:
                print(u)
        return

    if args.diff:
        if not args.file:
            _die("--diff necesita --file con tu lista de URLs.")
        sm = {norm(u) for u in expand(args.diff, args.ua)}
        with open(args.file, encoding="utf-8") as f:
            mine = [ln.split("#", 1)[0].strip() for ln in f if ln.split("#", 1)[0].strip()]
        missing = [u for u in mine if norm(u) not in sm]
        print(f"# {len(missing)} de {len(mine)} URLs NO están en el sitemap:", file=sys.stderr)
        for u in missing:
            print(u)
        if not missing:
            print("(todas tus URLs están en el sitemap ✔)", file=sys.stderr)


if __name__ == "__main__":
    main()
