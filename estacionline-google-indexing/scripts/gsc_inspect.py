#!/usr/bin/env python3
"""Estado real de indexación por URL (URL Inspection API de Search Console).

Para cada URL, Google devuelve el motivo EXACTO por el que está o no está
indexada — el mismo dato que ves en el inspector de URLs, pero en lote:

  - verdict            PASS / NEUTRAL / FAIL
  - coverageState      texto humano: "Rastreada: actualmente sin indexar",
                       "Enviada y indexada", "Página alternativa con...", etc.
  - robotsTxtState     ALLOWED / DISALLOWED
  - indexingState      INDEXING_ALLOWED / BLOCKED_BY_META_TAG / ...
  - lastCrawlTime      última vez que Googlebot la rastreó
  - googleCanonical    la canónica que ELIGIÓ Google
  - userCanonical      la canónica que declara tu página
  - pageFetchState     SUCCESSFUL / SOFT_404 / ...

Esto reemplaza tener que adivinar el item_key del drilldown: te dice, URL
por URL, por qué no indexa y qué corregir.

Necesita OAuth (corré antes: python3 scripts/gsc_auth.py).

Uso:
  python3 scripts/gsc_inspect.py --file urls.txt
  python3 scripts/gsc_inspect.py https://estacionline.com/una-nota/
  python3 scripts/gsc_inspect.py --file urls.txt --json estado.json
  python3 scripts/gsc_inspect.py --file urls.txt --site https://estacionline.com/

Cupos de la API: ~2000 URLs/día y 600/min por propiedad. Usá --limit / --delay.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gsc_common as gc  # noqa: E402

INSPECT_URL = gc.SC_BASE + "/urlInspection/index:inspect"


def read_urls(path: str) -> list[str]:
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.split("#", 1)[0].strip()
                if line:
                    out.append(line)
    except OSError as e:
        gc.die(f"no se pudo leer {path}: {e}")
    return out


def inspect(url: str, site: str, lang: str) -> dict:
    body = {"inspectionUrl": url, "siteUrl": site, "languageCode": lang}
    resp = gc.api("POST", INSPECT_URL, body)
    return resp.get("inspectionResult", {})


def summarize(url: str, result: dict) -> dict:
    idx = result.get("indexStatusResult", {})
    row = {
        "url": url,
        "verdict": idx.get("verdict", "?"),
        "coverageState": idx.get("coverageState", "?"),
        "robotsTxtState": idx.get("robotsTxtState"),
        "indexingState": idx.get("indexingState"),
        "pageFetchState": idx.get("pageFetchState"),
        "lastCrawlTime": idx.get("lastCrawlTime"),
        "googleCanonical": idx.get("googleCanonical"),
        "userCanonical": idx.get("userCanonical"),
        "sitemaps": idx.get("sitemap", []),
        "referringUrls": idx.get("referringUrls", []),
        "inspectionLink": result.get("inspectionResultLink"),
        "mobileVerdict": result.get("mobileUsabilityResult", {}).get("verdict"),
        "richVerdict": result.get("richResultsResult", {}).get("verdict"),
    }
    return row


ICON = {"PASS": "✅", "PARTIAL": "🟡", "NEUTRAL": "⚪", "FAIL": "❌"}


def print_row(r: dict):
    icon = ICON.get(r["verdict"], "•")
    print(f"\n{icon} {r['url']}")
    print(f"     Estado     : {r['coverageState']}  (verdict: {r['verdict']})")
    if r["lastCrawlTime"]:
        print(f"     Últ. rastreo: {r['lastCrawlTime']}")
    print(f"     robots.txt : {r['robotsTxtState']}   indexación: {r['indexingState']}"
          f"   fetch: {r['pageFetchState']}")
    gcan, ucan = r["googleCanonical"], r["userCanonical"]
    if gcan or ucan:
        flag = "" if (gcan and ucan and gc_norm(gcan) == gc_norm(ucan)) else "  ⚠️ DISTINTAS"
        print(f"     Canónica   : Google={gcan}  |  tu página={ucan}{flag}")
    if r["sitemaps"]:
        print(f"     En sitemap : {', '.join(r['sitemaps'])}")
    else:
        print("     En sitemap : (no figura) ⚠️")
    if not r["referringUrls"]:
        print("     Enlaces internos que la referencian: (ninguno) ⚠️ reforzar enlazado")


def gc_norm(u: str) -> str:
    return (u or "").rstrip("/").lower()


def main():
    ap = argparse.ArgumentParser(description="Estado de indexación por URL (URL Inspection API).")
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--file")
    ap.add_argument("--site", default=gc.DEFAULT_SITE, help=f"propiedad (def. {gc.DEFAULT_SITE})")
    ap.add_argument("--lang", default="es")
    ap.add_argument("--limit", type=int, default=200, help="máximo de URLs (def. 200; cupo diario ~2000)")
    ap.add_argument("--delay", type=float, default=0.3, help="pausa entre llamadas (def. 0.3s)")
    ap.add_argument("--json", dest="json_out")
    args = ap.parse_args()

    urls = list(args.urls)
    if args.file:
        urls += read_urls(args.file)
    seen = set()
    urls = [u for u in urls if not (u in seen or seen.add(u))]
    if not urls:
        gc.die("no hay URLs (usá --file o pasá URLs).")
    if len(urls) > args.limit:
        print(f"Limitando a {args.limit} de {len(urls)} (subí --limit).", file=sys.stderr)
        urls = urls[: args.limit]

    rows = []
    counts: dict[str, int] = {}
    for i, u in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] inspeccionando {u}", file=sys.stderr)
        result = inspect(u, args.site, args.lang)
        r = summarize(u, result)
        rows.append(r)
        counts[r["coverageState"]] = counts.get(r["coverageState"], 0) + 1
        print_row(r)
        if args.delay and i < len(urls):
            time.sleep(args.delay)

    print("\n" + "=" * 68)
    print("  RESUMEN POR ESTADO (coverageState)")
    print("=" * 68)
    for state, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {n:>3}  {state}")

    indexadas = [r["url"] for r in rows if r["verdict"] == "PASS"]
    no_index = [r for r in rows if r["verdict"] != "PASS"]
    print(f"\n  ✅ Indexadas: {len(indexadas)}   ❌/⚪ Sin indexar: {len(no_index)}")
    if no_index:
        print("\n  Para pedir indexación a mano (inspector → Solicitar indexación):")
        for r in no_index:
            print(f"     {r['url']}   [{r['coverageState']}]")

    if args.json_out:
        try:
            with open(args.json_out, "w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=2)
            print(f"\nDetalle en {args.json_out}", file=sys.stderr)
        except OSError as e:
            gc.die(f"no se pudo escribir {args.json_out}: {e}")


if __name__ == "__main__":
    main()
