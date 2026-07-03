#!/usr/bin/env python3
"""Turn a short-lived user token into a non-expiring Page token + write creds.

You give it: app id, app secret, and a short-lived USER token generated in the
Graph API Explorer (with pages_show_list + pages_manage_posts +
pages_read_engagement granted). It:
  1. Exchanges the user token for a long-lived one.
  2. Calls /me/accounts to list the pages you admin (with their page tokens,
     which are non-expiring when derived from a long-lived user token).
  3. If exactly one page (or --page-id matches), writes .credentials.json.

Usage:
  setup_token.py --app-id 123 --app-secret abc --user-token EAA...
  setup_token.py --app-id 123 --app-secret abc --user-token EAA... --page-id 456
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

GRAPH = "https://graph.facebook.com/v21.0"
CRED_FILE = Path(__file__).resolve().parent.parent / ".credentials.json"


def _get(url: str) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            msg = json.loads(body).get("error", {}).get("message", body)
        except json.JSONDecodeError:
            msg = body
        print(f"ERROR Graph {e.code}: {msg}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR de conexión: {e.reason}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--app-id", required=True)
    ap.add_argument("--app-secret", required=True)
    ap.add_argument("--user-token", required=True, help="Short-lived user token del Graph Explorer.")
    ap.add_argument("--page-id", help="Si admin de varias páginas, cuál usar.")
    args = ap.parse_args()

    # 1. short-lived user token -> long-lived user token
    q = urllib.parse.urlencode({
        "grant_type": "fb_exchange_token",
        "client_id": args.app_id,
        "client_secret": args.app_secret,
        "fb_exchange_token": args.user_token,
    })
    long_lived = _get(f"{GRAPH}/oauth/access_token?{q}").get("access_token")
    if not long_lived:
        print("ERROR: no obtuve long-lived user token.", file=sys.stderr)
        sys.exit(1)

    # 2. list pages + their (non-expiring) page tokens
    accounts = _get(
        f"{GRAPH}/me/accounts?fields=id,name,access_token&access_token="
        f"{urllib.parse.quote(long_lived)}"
    )
    pages = accounts.get("data", [])
    if not pages:
        print("ERROR: tu usuario no administra ninguna página (o falta el permiso pages_show_list).", file=sys.stderr)
        sys.exit(1)

    if args.page_id:
        chosen = next((p for p in pages if str(p["id"]) == str(args.page_id)), None)
        if not chosen:
            print(f"ERROR: no encontré la página {args.page_id}. Páginas disponibles:", file=sys.stderr)
            for p in pages:
                print(f"  {p['id']}  {p.get('name')}", file=sys.stderr)
            sys.exit(1)
    elif len(pages) == 1:
        chosen = pages[0]
    else:
        print("Administrás varias páginas — corré de nuevo con --page-id <id>:", file=sys.stderr)
        for p in pages:
            print(f"  {p['id']}  {p.get('name')}", file=sys.stderr)
        sys.exit(1)

    CRED_FILE.write_text(
        json.dumps({"page_id": chosen["id"], "access_token": chosen["access_token"]},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({
        "ok": True,
        "page_id": chosen["id"],
        "page_name": chosen.get("name"),
        "saved_to": str(CRED_FILE),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
