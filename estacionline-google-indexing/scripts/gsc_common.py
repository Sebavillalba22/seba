#!/usr/bin/env python3
"""Módulo común para los scripts de Google Search Console (OAuth + HTTP).

Todo con la librería estándar (urllib). No necesita google-auth ni
cryptography porque usamos OAuth "app de escritorio": el refresh token se
canjea por un access token con un POST HTTPS normal, sin firmar nada.

Archivos (todos al lado de SKILL.md, gitignoreados):
  oauth_client.json  → el JSON del "ID de cliente OAuth" que descargás de
                       Google Cloud (formato {"installed": {...}}).
  .gsc_token.json    → lo genera gsc_auth.py; guarda el refresh_token y
                       cachea el access_token con su vencimiento.

Propiedad por defecto: https://estacionline.com/  (propiedad de prefijo de
URL, tal cual aparece en el resource_id de Search Console). Se puede cambiar
con --site en cada script (también admite sc-domain:estacionline.com).
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLIENT_FILE = ROOT / "oauth_client.json"
TOKEN_FILE = ROOT / ".gsc_token.json"

DEFAULT_SITE = "https://estacionline.com/"
# webmasters (completo) cubre lectura + envío de sitemaps + URL Inspection.
SCOPE = "https://www.googleapis.com/auth/webmasters"
AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"
SC_BASE = "https://searchconsole.googleapis.com/v1"
WM_BASE = "https://www.googleapis.com/webmasters/v3"


def die(msg: str):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


# --------------------------------------------------------------------------- #
#  Credenciales                                                               #
# --------------------------------------------------------------------------- #
def load_client() -> dict:
    if not CLIENT_FILE.exists():
        die(f"falta {CLIENT_FILE.name} (ver oauth_client.example.json y SETUP-OAUTH.txt).")
    data = json.loads(CLIENT_FILE.read_text(encoding="utf-8"))
    node = data.get("installed") or data.get("web") or data
    cid = node.get("client_id")
    secret = node.get("client_secret")
    if not cid or not secret:
        die("oauth_client.json no tiene client_id / client_secret.")
    return {"client_id": cid, "client_secret": secret,
            "token_uri": node.get("token_uri", TOKEN_URI)}


def load_token() -> dict:
    if not TOKEN_FILE.exists():
        die(f"falta {TOKEN_FILE.name}: corré primero  python3 scripts/gsc_auth.py")
    return json.loads(TOKEN_FILE.read_text(encoding="utf-8"))


def save_token(tok: dict):
    TOKEN_FILE.write_text(json.dumps(tok, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        TOKEN_FILE.chmod(0o600)
    except OSError:
        pass


# --------------------------------------------------------------------------- #
#  HTTP                                                                        #
# --------------------------------------------------------------------------- #
def _request(url: str, method: str = "GET", data: bytes | None = None,
             headers: dict | None = None, timeout: float = 30.0):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            return resp.getcode(), raw
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except urllib.error.URLError as e:
        die(f"error de red llamando a {url}: {getattr(e, 'reason', e)}")


def post_form(url: str, fields: dict, timeout: float = 30.0) -> dict:
    body = urllib.parse.urlencode(fields).encode()
    code, raw = _request(url, "POST", body,
                         {"Content-Type": "application/x-www-form-urlencoded"}, timeout)
    try:
        payload = json.loads(raw.decode("utf-8", "replace"))
    except json.JSONDecodeError:
        die(f"respuesta no-JSON de {url}: {raw[:200]!r}")
    if code >= 400:
        die(f"OAuth {code}: {payload.get('error')} — {payload.get('error_description', '')}")
    return payload


# --------------------------------------------------------------------------- #
#  Access token (refresh automático con cache en disco)                       #
# --------------------------------------------------------------------------- #
def get_access_token() -> str:
    tok = load_token()
    now = time.time()
    if tok.get("access_token") and tok.get("expiry", 0) - 60 > now:
        return tok["access_token"]
    client = load_client()
    if not tok.get("refresh_token"):
        die("no hay refresh_token guardado: volvé a correr gsc_auth.py")
    payload = post_form(tok.get("token_uri", TOKEN_URI), {
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
        "refresh_token": tok["refresh_token"],
        "grant_type": "refresh_token",
    })
    tok["access_token"] = payload["access_token"]
    tok["expiry"] = now + int(payload.get("expires_in", 3600))
    save_token(tok)
    return tok["access_token"]


def api(method: str, url: str, body: dict | None = None, timeout: float = 30.0) -> dict:
    """Llamada autenticada a la API de Google. Devuelve el JSON (dict).
    Aborta con mensaje claro ante errores 4xx/5xx."""
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    code, raw = _request(url, method, data, headers, timeout)
    text = raw.decode("utf-8", "replace") if raw else ""
    payload: dict = {}
    if text.strip():
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = {"_raw": text}
    if code >= 400:
        err = payload.get("error", {})
        msg = err.get("message") if isinstance(err, dict) else err
        die(f"API {code} en {url}: {msg or text[:300]}")
    return payload


# --------------------------------------------------------------------------- #
#  Utilidades de propiedad / sitios                                           #
# --------------------------------------------------------------------------- #
def site_path(site_url: str) -> str:
    """Codifica la propiedad para meterla en la ruta de la Webmasters API."""
    return urllib.parse.quote(site_url, safe="")
