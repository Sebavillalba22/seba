#!/usr/bin/env python3
"""Listar y DESCARGAR los videos / reels de @estacionline vía la Graph API. Stdlib only.

Sirve para tomar los videos que ya están publicados en Instagram y reusarlos en
otras plataformas (YouTube, TikTok). Lee instagram.json (ig_user_id + token).

Uso:
  ig_fetch.py --list                       # lista los últimos videos/reels
  ig_fetch.py --list --limit 30
  ig_fetch.py --download-latest            # baja el último video a ./videos/
  ig_fetch.py --download-latest 3          # baja los últimos 3
  ig_fetch.py --download <MEDIA_ID>        # baja uno puntual
  ig_fetch.py --out /ruta/carpeta          # carpeta destino (default: ./videos)
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CRED_FILE = ROOT / "instagram.json"
API = "https://graph.facebook.com/v21.0"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def load_creds() -> dict:
    if not CRED_FILE.exists():
        sys.exit(f"ERROR: no encuentro {CRED_FILE}.")
    return json.loads(CRED_FILE.read_text(encoding="utf-8"))


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8"))


def list_videos(creds: dict, limit: int) -> list[dict]:
    ig = creds["ig_user_id"]
    tok = creds["access_token"]
    fields = "id,media_type,media_product_type,media_url,thumbnail_url,permalink,caption,timestamp"
    url = f"{API}/{ig}/media?fields={fields}&limit={limit}&access_token={urllib.parse.quote(tok)}"
    data = _get(url)
    if "error" in data:
        sys.exit(f"ERROR API: {data['error']}")
    return [m for m in data.get("data", []) if m.get("media_type") == "VIDEO" and m.get("media_url")]


def slug(text: str, media_id: str) -> str:
    base = "".join(c if c.isalnum() or c in " -_" else "" for c in (text or "").strip())[:50].strip()
    base = "_".join(base.split()) or "video"
    return f"{base}_{media_id}.mp4"


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as r, open(dest, "wb") as f:
        while True:
            chunk = r.read(65536)
            if not chunk:
                break
            f.write(chunk)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--download", metavar="MEDIA_ID")
    ap.add_argument("--download-latest", nargs="?", type=int, const=1, metavar="N")
    ap.add_argument("--out", default=str(ROOT / "videos"))
    args = ap.parse_args()

    creds = load_creds()
    vids = list_videos(creds, args.limit)
    outdir = Path(args.out)

    if args.list or (not args.download and args.download_latest is None):
        print(f"{len(vids)} videos/reels encontrados:\n")
        for m in vids:
            cap = (m.get("caption") or "").replace("\n", " ")[:70]
            print(f"  {m['id']}  {m['timestamp'][:10]}  {m.get('media_product_type','')}")
            print(f"      {cap}")
            print(f"      {m.get('permalink','')}")
        return

    targets = []
    if args.download:
        targets = [m for m in vids if m["id"] == args.download]
        if not targets:
            sys.exit(f"ERROR: no encontré el video {args.download} entre los últimos {args.limit}.")
    elif args.download_latest is not None:
        targets = vids[: args.download_latest]

    for m in targets:
        dest = outdir / slug(m.get("caption", ""), m["id"])
        print(f"bajando {m['id']} -> {dest} ...", flush=True)
        download(m["media_url"], dest)
        print(f"  OK ({dest.stat().st_size // 1024} KB)")
    print(f"\nListo. {len(targets)} archivo(s) en {outdir}")


if __name__ == "__main__":
    main()
