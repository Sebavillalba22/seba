#!/usr/bin/env python3
"""Renovar el access_token de LinkedIn usando el refresh_token. Stdlib only.

El access_token dura ~60 días; el refresh_token ~1 año. Cuando el access_token
esté por vencer, correr esto: usa el refresh_token + client_id/secret de
linkedin.json para pedir un access_token nuevo y reescribe linkedin.json.

  python scripts/linkedin_refresh.py

(Si el refresh_token también venció, hay que rehacer el OAuth desde cero.)
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CRED_FILE = ROOT / "linkedin.json"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"


def main() -> None:
    if not CRED_FILE.exists():
        sys.exit(f"ERROR: no encuentro {CRED_FILE}.")
    creds = json.loads(CRED_FILE.read_text(encoding="utf-8"))
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": creds["refresh_token"],
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
    }).encode("utf-8")
    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        sys.exit(f"ERROR HTTP {e.code}: {raw}\n(Si el refresh_token venció, rehacer el OAuth.)")

    creds["access_token"] = payload["access_token"]
    if payload.get("refresh_token"):
        creds["refresh_token"] = payload["refresh_token"]
    CRED_FILE.write_text(json.dumps(creds, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "expires_in": payload.get("expires_in")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
