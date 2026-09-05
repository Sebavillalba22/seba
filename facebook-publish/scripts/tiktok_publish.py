#!/usr/bin/env python3
"""Publicar videos en TikTok (@estacionlineok) vía Content Posting API. Stdlib only.

Credenciales en tiktok.json (client key/secret + access_token 24h + refresh_token 1 año).
El access_token se renueva solo con el refresh_token en cada corrida.

⚠️ Mientras la app esté SIN AUDITAR (o en sandbox), TikTok limita la visibilidad
del contenido posteado a SOLO EL CREADOR (SELF_ONLY / privado). Para posteo
público automático hay que pasar la auditoría de TikTok (submit for review).

Uso:
  tiktok_publish.py --check                          # verifica token + creator info
  tiktok_publish.py --file video.mp4 --title "Título #hashtag"
  tiktok_publish.py --file v.mp4 --title "T" --privacy SELF_ONLY   # default
  tiktok_publish.py --file v.mp4 --title "T" --draft  # a la bandeja (el usuario publica en la app)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CRED_FILE = ROOT / "tiktok.json"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
API = "https://open.tiktokapis.com/v2"
CHUNK = 10 * 1024 * 1024  # 10 MB


def load_creds() -> dict:
    if not CRED_FILE.exists():
        sys.exit(f"ERROR: no encuentro {CRED_FILE}.")
    return json.loads(CRED_FILE.read_text(encoding="utf-8"))


def save_creds(c: dict) -> None:
    CRED_FILE.write_text(json.dumps(c, indent=2, ensure_ascii=False), encoding="utf-8")


def _client(creds: dict) -> tuple[str, str]:
    if creds.get("use_sandbox"):
        return creds["sandbox_client_key"], creds["sandbox_client_secret"]
    return creds["client_key"], creds["client_secret"]


def refresh_token(creds: dict) -> str:
    key, secret = _client(creds)
    data = urllib.parse.urlencode({
        "client_key": key, "client_secret": secret,
        "grant_type": "refresh_token", "refresh_token": creds["refresh_token"],
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=data, method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req) as r:
        payload = json.loads(r.read().decode())
    if "access_token" not in payload:
        sys.exit(f"ERROR renovando token: {payload}")
    creds["access_token"] = payload["access_token"]
    creds["refresh_token"] = payload.get("refresh_token", creds["refresh_token"])
    save_creds(creds)
    return creds["access_token"]


def _post(url: str, token: str, body: dict | None) -> dict:
    req = urllib.request.Request(
        url, data=json.dumps(body or {}).encode("utf-8"), method="POST",
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json; charset=UTF-8"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"http": e.code, "raw": e.read().decode("utf-8", "replace")}


def check(creds: dict) -> None:
    tok = refresh_token(creds)
    d = _post(f"{API}/post/publish/creator_info/query/", tok, {})
    data = d.get("data", {})
    err = d.get("error", {})
    if err.get("code") not in ("ok", None):
        print(json.dumps({"ok": False, "error": err}, ensure_ascii=False, indent=2)); sys.exit(1)
    print(json.dumps({"ok": True,
                      "cuenta": data.get("creator_nickname"),
                      "username": data.get("creator_username"),
                      "privacidades": data.get("privacy_level_options"),
                      "max_duracion_s": data.get("max_video_post_duration_sec"),
                      "sandbox": bool(creds.get("use_sandbox"))}, ensure_ascii=False, indent=2))


def upload_file(upload_url: str, path: str, chunk_size: int, total_chunks: int) -> None:
    """Sube el archivo en total_chunks partes de chunk_size (la última absorbe el resto)."""
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        for i in range(total_chunks):
            start = i * chunk_size
            # la última parte lleva todo lo que queda
            length = (size - start) if i == total_chunks - 1 else chunk_size
            chunk = f.read(length)
            end = start + length - 1
            req = urllib.request.Request(upload_url, data=chunk, method="PUT", headers={
                "Content-Type": "video/mp4",
                "Content-Length": str(length),
                "Content-Range": f"bytes {start}-{end}/{size}",
            })
            try:
                urllib.request.urlopen(req)
            except urllib.error.HTTPError as e:
                if e.code not in (200, 201, 206):
                    sys.exit(f"ERROR subiendo bytes HTTP {e.code}: {e.read().decode('utf-8','replace')}")
            print(f"  subido {min(end+1,size)//1024//1024}/{size//1024//1024} MB", flush=True)


def publish(creds: dict, path: str, title: str, privacy: str, draft: bool) -> None:
    if not os.path.exists(path):
        sys.exit(f"ERROR: no existe {path}")
    tok = refresh_token(creds)
    size = os.path.getsize(path)
    # Regla TikTok: total_chunk_count = size // chunk_size (la última parte absorbe
    # el resto). Archivos de hasta 64 MB van ENTEROS en un solo chunk.
    if size <= 64 * 1024 * 1024:
        chunk_size, total_chunks = size, 1
    else:
        chunk_size = CHUNK
        total_chunks = size // chunk_size
    source_info = {"source": "FILE_UPLOAD", "video_size": size,
                   "chunk_size": chunk_size, "total_chunk_count": total_chunks}

    if draft:
        endpoint = f"{API}/post/publish/inbox/video/init/"
        body = {"source_info": source_info}
    else:
        endpoint = f"{API}/post/publish/video/init/"
        body = {"post_info": {"title": title[:2200], "privacy_level": privacy,
                              "disable_duet": False, "disable_comment": False,
                              "disable_stitch": False},
                "source_info": source_info}

    d = _post(endpoint, tok, body)
    err = d.get("error", {})
    if err.get("code") not in ("ok", None):
        sys.exit(f"ERROR init: {json.dumps(d, ensure_ascii=False)}")
    data = d.get("data", {})
    publish_id = data.get("publish_id")
    upload_url = data.get("upload_url")
    if not upload_url:
        sys.exit(f"ERROR: sin upload_url -> {json.dumps(d, ensure_ascii=False)}")
    print(f"publish_id: {publish_id}", flush=True)
    print(f"subiendo {os.path.basename(path)} ({size//1024//1024} MB)...", flush=True)
    upload_file(upload_url, path, chunk_size, total_chunks)

    # esperar el procesamiento (~5 min máx; los videos grandes tardan)
    for _ in range(60):
        time.sleep(5)
        st = _post(f"{API}/post/publish/status/fetch/", tok, {"publish_id": publish_id})
        s = st.get("data", {}).get("status")
        if s in ("PUBLISH_COMPLETE", "SEND_TO_USER_INBOX"):
            print(json.dumps({"ok": True, "status": s, "publish_id": publish_id,
                              "modo": "borrador" if draft else f"direct post ({privacy})"},
                             ensure_ascii=False, indent=2))
            return
        if s == "FAILED":
            sys.exit(f"FALLO: {json.dumps(st, ensure_ascii=False)}")
        print(f"  estado: {s}...", flush=True)
    sys.exit(f"TIMEOUT esperando el procesamiento; el video puede llegar igual. "
             f"Chequear luego: --status {publish_id}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    ap.add_argument("--title", default="")
    ap.add_argument("--privacy", default="SELF_ONLY",
                    choices=["PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "SELF_ONLY", "FOLLOWER_OF_CREATOR"])
    ap.add_argument("--draft", action="store_true", help="a la bandeja de TikTok (publicás desde la app).")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--status", metavar="PUBLISH_ID", help="consulta el estado de un envío.")
    args = ap.parse_args()

    creds = load_creds()
    if args.check:
        check(creds)
        return
    if args.status:
        tok = refresh_token(creds)
        st = _post(f"{API}/post/publish/status/fetch/", tok, {"publish_id": args.status})
        print(json.dumps(st, ensure_ascii=False, indent=2))
        return
    if not args.file:
        sys.exit("ERROR: falta --file.")
    if not args.draft and not args.title:
        sys.exit("ERROR: falta --title.")
    publish(creds, args.file, args.title, args.privacy, args.draft)


if __name__ == "__main__":
    main()
