#!/usr/bin/env python3
"""Publicar una HISTORIA en Instagram (imagen o video) vía Graph API. Stdlib only.

Requiere instagram.json (al lado de SKILL.md):
  {"ig_user_id": "...", "access_token": "<page token con IG scopes>"}

⚠️ La imagen/video DEBE estar en una URL pública (IG no acepta archivos locales).
   - Imagen: JPG/PNG 9:16 (1080x1920).
   - Video: MP4 (h264/aac) 9:16, ≤60s, ≤100MB.

Uso:
  ig_story.py --video-url https://estacionline.com/.../embody.mp4
  ig_story.py --image-url https://estacionline.com/.../sponsor.jpg
  ig_story.py --video-url ... --dry-run   # crea el container, NO publica
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

GRAPH = "https://graph.facebook.com/v21.0"
IG_FILE = Path(__file__).resolve().parent.parent / "instagram.json"


def _die(m):
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def load_ig():
    if not IG_FILE.exists():
        _die(f"falta {IG_FILE}")
    d = json.loads(IG_FILE.read_text(encoding="utf-8"))
    if not d.get("ig_user_id") or not d.get("access_token"):
        _die("instagram.json incompleto")
    return d["ig_user_id"], d["access_token"]


def _post(path, fields):
    data = urllib.parse.urlencode(fields).encode()
    return _do(urllib.request.Request(f"{GRAPH}/{path}", data=data, method="POST"))


def _get(path, params):
    return _do(urllib.request.Request(f"{GRAPH}/{path}?" + urllib.parse.urlencode(params), method="GET"))


def _do(req):
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(body).get("error", {}).get("message", body)
        except json.JSONDecodeError:
            msg = body
        _die(f"Graph {e.code}: {msg}")
    except urllib.error.URLError as e:
        _die(f"conexión: {e.reason}")


def _wait_ready(cid, token, tries=60):
    # Los videos tardan en procesar; esperamos a FINISHED.
    for _ in range(tries):
        st = _get(cid, {"fields": "status_code", "access_token": token})
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code == "ERROR":
            _die(f"container {cid} en ERROR")
        time.sleep(3)
    _die(f"timeout esperando container {cid}")


def post_story(ig_id, token, image_url=None, video_url=None, dry_run=False):
    if not image_url and not video_url:
        _die("pasá --image-url o --video-url (URL pública)")
    fields = {"media_type": "STORIES", "access_token": token}
    if video_url:
        fields["video_url"] = video_url
    else:
        fields["image_url"] = image_url
    cont = _post(f"{ig_id}/media", fields)
    cid = cont["id"]
    _wait_ready(cid, token)
    if dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "creation_id": cid, "note": "NO publicado"}, ensure_ascii=False))
        return
    pub = _post(f"{ig_id}/media_publish", {"creation_id": cid, "access_token": token})
    mid = pub.get("id")
    print(json.dumps({"ok": True, "media_id": mid, "type": "story"}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image-url")
    ap.add_argument("--video-url")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    ig_id, token = load_ig()
    post_story(ig_id, token, image_url=args.image_url, video_url=args.video_url, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
