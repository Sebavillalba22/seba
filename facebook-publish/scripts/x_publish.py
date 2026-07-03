#!/usr/bin/env python3
"""Publicar en X (Twitter) vía API v2 con OAuth 1.0a. Stdlib only.

Credenciales en x_credentials.json (al lado de SKILL.md):
  {"api_key": "...", "api_secret": "...",
   "access_token": "...", "access_secret": "..."}

Uso:
  x_publish.py --text "Título  https://estacionline.com/..."
  x_publish.py --check        # verifica auth (GET /2/users/me), no postea
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CRED = Path(__file__).resolve().parent.parent / "x_credentials.json"
API = "https://api.x.com"


def _die(m):
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def load():
    if not CRED.exists():
        _die(f"falta {CRED}")
    d = json.loads(CRED.read_text(encoding="utf-8"))
    for k in ("api_key", "api_secret", "access_token", "access_secret"):
        if not d.get(k):
            _die(f"falta {k} en x_credentials.json")
    return d


def _enc(s):
    return urllib.parse.quote(str(s), safe="~")


def _auth_header(method, url, creds, query=None):
    oauth = {
        "oauth_consumer_key": creds["api_key"],
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": creds["access_token"],
        "oauth_version": "1.0",
    }
    # Para firmar se combinan params oauth + query (NO el body JSON).
    sign_params = dict(oauth)
    if query:
        sign_params.update(query)
    param_str = "&".join(
        f"{_enc(k)}={_enc(v)}" for k, v in sorted(sign_params.items())
    )
    base = "&".join([method.upper(), _enc(url), _enc(param_str)])
    signing_key = f"{_enc(creds['api_secret'])}&{_enc(creds['access_secret'])}"
    sig = base64.b64encode(
        hmac.new(signing_key.encode(), base.encode(), hashlib.sha1).digest()
    ).decode()
    oauth["oauth_signature"] = sig
    header = "OAuth " + ", ".join(
        f'{_enc(k)}="{_enc(v)}"' for k, v in sorted(oauth.items())
    )
    return header


def _do(req):
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            pass
        return e.code, body


def check(creds):
    url = f"{API}/2/users/me"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", _auth_header("GET", url, creds))
    code, body = _do(req)
    if code == 200:
        print(json.dumps({"ok": True, "user": body.get("data")}, ensure_ascii=False, indent=2))
    else:
        _die(f"auth falló ({code}): {body}")


def tweet(creds, text):
    if not text:
        _die("pasá --text")
    if len(text) > 280:
        print(f"AVISO: el texto tiene {len(text)} caracteres (>280). X puede rechazarlo.", file=sys.stderr)
    url = f"{API}/2/tweets"
    data = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", _auth_header("POST", url, creds))
    req.add_header("Content-Type", "application/json")
    code, body = _do(req)
    if code in (200, 201):
        tid = body.get("data", {}).get("id")
        out = {"ok": True, "id": tid}
        if tid:
            out["url"] = f"https://x.com/estacionline/status/{tid}"
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        _die(f"no se pudo publicar ({code}): {body}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", "-t")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    creds = load()
    if args.check:
        check(creds)
    else:
        tweet(creds, args.text)


if __name__ == "__main__":
    main()
