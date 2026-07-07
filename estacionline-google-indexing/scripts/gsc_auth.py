#!/usr/bin/env python3
"""Autorización OAuth con Google (una sola vez) para Search Console.

Flujo "app de escritorio" con loopback en 127.0.0.1: abre el navegador,
consentís con TU cuenta de Google (la que tiene acceso a la propiedad de
Search Console), y guarda el refresh_token en .gsc_token.json. De ahí en
más los demás scripts renuevan el access_token solos.

Requisitos previos (ver SETUP-OAUTH.txt):
  1. Proyecto en Google Cloud con la "Search Console API" habilitada.
  2. "ID de cliente OAuth" tipo App de escritorio, descargado como
     oauth_client.json (al lado de SKILL.md).

Uso:
  python3 scripts/gsc_auth.py                 # abre el navegador (loopback)
  python3 scripts/gsc_auth.py --no-browser    # imprime la URL para pegar
  python3 scripts/gsc_auth.py --manual        # sin server local (pegás el code)

Solo stdlib.
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gsc_common as gc  # noqa: E402


class _Handler(BaseHTTPRequestHandler):
    code: str | None = None
    error: str | None = None

    def do_GET(self):  # noqa: N802
        qs = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(qs)
        _Handler.code = (params.get("code") or [None])[0]
        _Handler.error = (params.get("error") or [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        msg = ("✅ Autorización recibida. Ya podés cerrar esta pestaña y volver a la terminal."
               if _Handler.code else
               f"❌ Error de autorización: {_Handler.error}")
        self.wfile.write(f"<html><body style='font-family:sans-serif'><h2>{msg}</h2></body></html>"
                         .encode("utf-8"))

    def log_message(self, *args):  # silenciar el log del server
        pass


def build_auth_url(client_id: str, redirect_uri: str) -> str:
    q = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": gc.SCOPE,
        "access_type": "offline",
        "prompt": "consent",
    })
    return f"{gc.AUTH_URI}?{q}"


def exchange_code(client: dict, code: str, redirect_uri: str) -> dict:
    return gc.post_form(client["token_uri"], {
        "code": code,
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    })


def loopback_flow(client: dict, open_browser: bool):
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    port = server.server_address[1]
    redirect_uri = f"http://127.0.0.1:{port}"
    url = build_auth_url(client["client_id"], redirect_uri)
    print("\nAbrí esta URL en el navegador (con la cuenta que administra la propiedad):\n")
    print("  " + url + "\n")
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:  # noqa: BLE001
            pass
    print("Esperando la autorización en", redirect_uri, "...")
    server.handle_request()
    server.server_close()
    if _Handler.error:
        gc.die(f"Google devolvió error: {_Handler.error}")
    if not _Handler.code:
        gc.die("no se recibió el código de autorización.")
    return exchange_code(client, _Handler.code, redirect_uri)


def manual_flow(client: dict):
    # redirect a localhost pero sin server: el usuario copia el ?code=... de la barra
    redirect_uri = "http://127.0.0.1:0"
    url = build_auth_url(client["client_id"], redirect_uri)
    print("\n1) Abrí esta URL, consentí, y cuando el navegador falle al cargar")
    print("   127.0.0.1:0, copiá el valor de 'code=' de la barra de direcciones:\n")
    print("  " + url + "\n")
    code = input("2) Pegá acá el code: ").strip()
    if not code:
        gc.die("no ingresaste ningún code.")
    return exchange_code(client, code, redirect_uri)


def main():
    ap = argparse.ArgumentParser(description="OAuth con Google Search Console (una vez).")
    ap.add_argument("--no-browser", action="store_true", help="no abrir el navegador solo")
    ap.add_argument("--manual", action="store_true", help="sin server local; pegás el code a mano")
    args = ap.parse_args()

    client = gc.load_client()
    payload = manual_flow(client) if args.manual else loopback_flow(client, not args.no_browser)

    if "refresh_token" not in payload:
        gc.die("Google no devolvió refresh_token. Revocá el acceso en "
               "myaccount.google.com/permissions y reintentá (usamos prompt=consent).")

    tok = {
        "refresh_token": payload["refresh_token"],
        "access_token": payload.get("access_token"),
        "expiry": 0,
        "token_uri": client["token_uri"],
        "scope": payload.get("scope", gc.SCOPE),
    }
    gc.save_token(tok)
    print(f"\n✅ Listo. refresh_token guardado en {gc.TOKEN_FILE.name} (gitignoreado).")
    print("   Probá:  python3 scripts/gsc_sitemaps.py --list")


if __name__ == "__main__":
    main()
