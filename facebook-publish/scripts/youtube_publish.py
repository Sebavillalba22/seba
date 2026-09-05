#!/usr/bin/env python3
"""Subir videos al canal de YouTube de Estacionline (Data API v3). Stdlib only.

Credenciales en youtube.json (client_id/secret + refresh_token permanente). El
access_token se renueva solo con el refresh_token en cada corrida.

Uso:
  youtube_publish.py --check                          # muestra el canal
  youtube_publish.py --file video.mp4 --title "Título" --description "..."
  youtube_publish.py --file v.mp4 --title "T" --tags "funes,rosario" --privacy public
  youtube_publish.py --file v.mp4 --title "T" --privacy unlisted

Privacidad: private (default) | unlisted | public.
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
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CRED_FILE = ROOT / "youtube.json"
TOKEN_URL = "https://oauth2.googleapis.com/token"
API = "https://www.googleapis.com/youtube/v3"
UPLOAD = "https://www.googleapis.com/upload/youtube/v3/videos"
CATEGORY_NEWS = "25"  # News & Politics


def load_creds() -> dict:
    if not CRED_FILE.exists():
        sys.exit(f"ERROR: no encuentro {CRED_FILE}.")
    return json.loads(CRED_FILE.read_text(encoding="utf-8"))


def save_creds(c: dict) -> None:
    CRED_FILE.write_text(json.dumps(c, indent=2, ensure_ascii=False), encoding="utf-8")


def refresh_token(creds: dict) -> str:
    """Renueva el access_token con el refresh_token y lo persiste."""
    data = urllib.parse.urlencode({
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "refresh_token": creds["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            payload = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR renovando token HTTP {e.code}: {e.read().decode('utf-8','replace')}")
    creds["access_token"] = payload["access_token"]
    save_creds(creds)
    return creds["access_token"]


def check(creds: dict) -> None:
    tok = refresh_token(creds)
    req = urllib.request.Request(
        f"{API}/channels?part=snippet,statistics&mine=true",
        headers={"Authorization": f"Bearer {tok}"})
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read().decode())
    items = d.get("items", [])
    if not items:
        print(json.dumps({"ok": False, "resp": d}, ensure_ascii=False)); sys.exit(1)
    it = items[0]
    print(json.dumps({"ok": True, "canal": it["snippet"]["title"],
                      "subs": it["statistics"].get("subscriberCount"),
                      "id": it["id"]}, ensure_ascii=False, indent=2))


def upload(creds: dict, path: str, title: str, description: str,
           tags: list[str], privacy: str) -> None:
    if not os.path.exists(path):
        sys.exit(f"ERROR: no existe el archivo {path}")
    tok = refresh_token(creds)
    size = os.path.getsize(path)
    ctype = mimetypes.guess_type(path)[0] or "video/mp4"
    metadata = {
        "snippet": {"title": title[:100], "description": description or "",
                    "tags": tags, "categoryId": CATEGORY_NEWS},
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
    }
    # 1) iniciar upload resumable
    init = urllib.request.Request(
        f"{UPLOAD}?uploadType=resumable&part=snippet,status",
        data=json.dumps(metadata).encode("utf-8"), method="POST",
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8",
                 "X-Upload-Content-Type": ctype, "X-Upload-Content-Length": str(size)})
    try:
        with urllib.request.urlopen(init) as r:
            location = r.headers.get("Location")
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR iniciando upload HTTP {e.code}: {e.read().decode('utf-8','replace')}")
    if not location:
        sys.exit("ERROR: YouTube no devolvió URL de subida.")
    # 2) subir los bytes (un solo PUT)
    print(f"subiendo {os.path.basename(path)} ({size//1024//1024} MB)...", flush=True)
    with open(path, "rb") as f:
        put = urllib.request.Request(location, data=f.read(), method="PUT",
                                     headers={"Content-Type": ctype, "Content-Length": str(size)})
        try:
            with urllib.request.urlopen(put) as r:
                vid = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            sys.exit(f"ERROR subiendo HTTP {e.code}: {e.read().decode('utf-8','replace')}")
    vid_id = vid.get("id")
    print(json.dumps({"ok": True, "id": vid_id,
                      "url": f"https://youtu.be/{vid_id}",
                      "privacy": privacy}, ensure_ascii=False, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="ruta al video (mp4).")
    ap.add_argument("--title")
    ap.add_argument("--description", default="")
    ap.add_argument("--tags", default="", help="separados por coma.")
    ap.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    creds = load_creds()
    if args.check:
        check(creds)
        return
    if not args.file or not args.title:
        sys.exit("ERROR: faltan --file y --title.")
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    upload(creds, args.file, args.title, args.description, tags, args.privacy)


if __name__ == "__main__":
    main()
