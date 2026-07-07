#!/usr/bin/env python3
"""Rendimiento en Búsqueda (Search Analytics API de Search Console).

Muestra clics, impresiones, CTR y posición media por consulta, por página o
por fecha. Sirve para ver qué SÍ está indexado y trayendo tráfico, y para
priorizar qué notas conviene reforzar/pedir indexación.

Necesita OAuth (corré antes: python3 scripts/gsc_auth.py).

Uso:
  # top consultas de los últimos 28 días
  python3 scripts/gsc_performance.py --by query --days 28

  # top páginas de un rango explícito
  python3 scripts/gsc_performance.py --by page --start 2026-06-01 --end 2026-06-30

  # consultas de UNA página concreta
  python3 scripts/gsc_performance.py --by query --page https://estacionline.com/una-nota/

  # evolución diaria de clics/impresiones
  python3 scripts/gsc_performance.py --by date --days 90

Solo stdlib.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gsc_common as gc  # noqa: E402


def query_url(site: str) -> str:
    return f"{gc.WM_BASE}/sites/{gc.site_path(site)}/searchAnalytics/query"


def daterange(days: int) -> tuple[str, str]:
    end = _dt.date.today()
    start = end - _dt.timedelta(days=days)
    return start.isoformat(), end.isoformat()


def run(site: str, dim: str, start: str, end: str, row_limit: int,
        page_filter: str | None) -> list[dict]:
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": [dim],
        "rowLimit": row_limit,
    }
    if page_filter:
        body["dimensionFilterGroups"] = [{
            "filters": [{"dimension": "page", "operator": "equals", "expression": page_filter}]
        }]
    resp = gc.api("POST", query_url(site), body)
    return resp.get("rows", [])


def main():
    ap = argparse.ArgumentParser(description="Rendimiento en Búsqueda (Search Analytics).")
    ap.add_argument("--site", default=gc.DEFAULT_SITE, help=f"propiedad (def. {gc.DEFAULT_SITE})")
    ap.add_argument("--by", choices=["query", "page", "date"], default="query")
    ap.add_argument("--days", type=int, default=28, help="rango en días hasta hoy (def. 28)")
    ap.add_argument("--start", help="fecha inicio YYYY-MM-DD (pisa --days)")
    ap.add_argument("--end", help="fecha fin YYYY-MM-DD")
    ap.add_argument("--rows", type=int, default=25, help="filas a mostrar (def. 25)")
    ap.add_argument("--page", help="filtrar por una página concreta")
    args = ap.parse_args()

    if args.start and args.end:
        start, end = args.start, args.end
    else:
        start, end = daterange(args.days)

    rows = run(args.site, args.by, start, end, args.rows, args.page)
    label = {"query": "CONSULTA", "page": "PÁGINA", "date": "FECHA"}[args.by]
    print(f"\n{label:<45} {'CLICS':>7} {'IMPR.':>8} {'CTR':>7} {'POS.':>6}")
    print("-" * 78)
    tot_c = tot_i = 0
    for r in rows:
        key = r.get("keys", ["?"])[0]
        clicks = int(r.get("clicks", 0))
        impr = int(r.get("impressions", 0))
        ctr = r.get("ctr", 0) * 100
        pos = r.get("position", 0)
        tot_c += clicks
        tot_i += impr
        show = key if len(key) <= 44 else key[:41] + "..."
        print(f"{show:<45} {clicks:>7} {impr:>8} {ctr:>6.1f}% {pos:>6.1f}")
    print("-" * 78)
    print(f"{'TOTAL (' + start + ' → ' + end + ')':<45} {tot_c:>7} {tot_i:>8}")
    if not rows:
        print("(sin datos en el rango — puede que la propiedad sea nueva o el filtro no matchee)")


if __name__ == "__main__":
    main()
