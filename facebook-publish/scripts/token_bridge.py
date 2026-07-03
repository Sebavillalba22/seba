#!/usr/bin/env python3
"""Loopback bridge: receives a short-lived USER token from the browser,
exchanges it for a non-expiring PAGE token, writes .credentials.json.

The secret never passes through the model: the browser POSTs the user token
to 127.0.0.1, this process does the Graph calls and writes the file, then
returns only {page_id, page_name} (non-secret) and shuts down.

Env: FB_APP_ID, FB_APP_SECRET. Optional FB_PAGE_ID to disambiguate.
Listens on 127.0.0.1:8765.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

GRAPH = "https://graph.facebook.com/v21.0"
CRED_FILE = Path(__file__).resolve().parent.parent / ".credentials.json"
APP_ID = os.environ["FB_APP_ID"]
APP_SECRET = os.environ["FB_APP_SECRET"]
WANT_PAGE = os.environ.get("FB_PAGE_ID")

_result: dict = {}


def _get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def exchange(user_token: str) -> dict:
    q = urllib.parse.urlencode({
        "grant_type": "fb_exchange_token",
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "fb_exchange_token": user_token,
    })
    long_lived = _get(f"{GRAPH}/oauth/access_token?{q}").get("access_token")
    if not long_lived:
        return {"error": "no long-lived user token"}
    accounts = _get(
        f"{GRAPH}/me/accounts?fields=id,name,access_token&access_token="
        f"{urllib.parse.quote(long_lived)}"
    )
    pages = accounts.get("data", [])
    if not pages:
        return {"error": "no pages (missing pages_show_list or no admin pages)"}
    if WANT_PAGE:
        chosen = next((p for p in pages if str(p["id"]) == str(WANT_PAGE)), None)
        if not chosen:
            return {"error": "page not found", "pages": [{"id": p["id"], "name": p.get("name")} for p in pages]}
    elif len(pages) == 1:
        chosen = pages[0]
    else:
        return {"error": "multiple pages", "pages": [{"id": p["id"], "name": p.get("name")} for p in pages]}
    CRED_FILE.write_text(
        json.dumps({"page_id": chosen["id"], "access_token": chosen["access_token"]},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    try:
        CRED_FILE.chmod(0o600)
    except OSError:
        pass
    return {"ok": True, "page_id": chosen["id"], "page_name": chosen.get("name")}


class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "https://developers.facebook.com")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "content-type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        try:
            user_token = json.loads(body).get("user_token", "")
        except json.JSONDecodeError:
            user_token = ""
        if not user_token:
            out = {"error": "no user_token in body"}
        else:
            try:
                out = exchange(user_token)
            except urllib.error.HTTPError as e:
                out = {"error": f"graph {e.code}: {e.read().decode('utf-8', errors='replace')[:300]}"}
            except Exception as e:  # noqa: BLE001
                out = {"error": str(e)}
        payload = json.dumps(out, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload)
        global _result
        _result = out

    def log_message(self, *a):  # silence
        pass


def main():
    srv = HTTPServer(("127.0.0.1", 8765), H)
    # Serve until we get a successful credential write (or many attempts).
    for _ in range(50):
        srv.handle_request()
        if _result.get("ok"):
            print(json.dumps(_result, ensure_ascii=False))
            return
        if _result.get("error"):
            print(json.dumps(_result, ensure_ascii=False), file=sys.stderr)
            # keep serving in case the browser retries, unless it's fatal
    print(json.dumps(_result, ensure_ascii=False))


if __name__ == "__main__":
    main()
