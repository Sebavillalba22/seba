#!/usr/bin/env python3
"""Publicar en la PÁGINA (organización) de LinkedIn de Estacionline. Stdlib only.

Usa la Community Management API (Posts API). Lee credenciales de linkedin.json
(al lado de SKILL.md): access_token + org_urn. Multiplataforma.

Ejemplos:
  python scripts/linkedin_publish.py --check
  python scripts/linkedin_publish.py \
      --message "Título\n\nBajada" \
      --link https://estacionline.com/nota/ \
      --title "Título" --description "Bajada"
  python scripts/linkedin_publish.py --message "Solo texto, sin link"
  python scripts/linkedin_publish.py --dry-run --message "x" --link https://...

Notas:
- El token dura ~60 días. Si vence, regenerar con scripts/linkedin_refresh.py
  (usa el refresh_token, válido ~1 año) o rehaciendo el OAuth.
- El link en LinkedIn SÍ es clickeable (se arma una tarjeta de artículo).
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

ROOT = Path(__file__).resolve().parent.parent
CRED_FILE = ROOT / "linkedin.json"
API = "https://api.linkedin.com/rest"
VERSION = "202607"

# Caracteres reservados que LinkedIn exige escapar en el campo commentary.
_RESERVED = "\\|{}@[]()<>#*_~"


def load_creds() -> dict:
    if not CRED_FILE.exists():
        sys.exit(f"ERROR: no encuentro {CRED_FILE}.")
    return json.loads(CRED_FILE.read_text(encoding="utf-8"))


def escape_commentary(text: str) -> str:
    for ch in _RESERVED:
        text = text.replace(ch, "\\" + ch)
    return text


def fetch_og_image(url: str) -> str | None:
    """Levanta la og:image de la nota para adjuntarla como miniatura.
    Subir la miniatura a mano es MUCHO más confiable que dejar que LinkedIn
    scrapee la página (el scrape falla seguido y la tarjeta sale sin foto)."""
    import re
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError):
        return None
    for pat in (r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image'):
        m = re.search(pat, html, re.I)
        if m:
            return m.group(1)
    return None


def upload_image(creds: dict, image_url: str) -> str:
    """Sube una imagen (desde una URL pública) a LinkedIn y devuelve su URN."""
    token = creds["access_token"]
    # 1) initializeUpload -> uploadUrl + image URN
    _, payload, _ = _req(
        "POST", f"{API}/images?action=initializeUpload", token,
        {"initializeUploadRequest": {"owner": creds["org_urn"]}},
    )
    value = payload.get("value", {})
    upload_url = value["uploadUrl"]
    image_urn = value["image"]
    # 2) descargar bytes de la imagen (UA de navegador: estacionline está detrás
    #    de Cloudflare y rechaza el UA por defecto de urllib con 403)
    dl = urllib.request.Request(image_url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    })
    with urllib.request.urlopen(dl) as r:
        img_bytes = r.read()
    # 3) PUT de los bytes al uploadUrl
    put = urllib.request.Request(upload_url, data=img_bytes, method="PUT")
    put.add_header("Authorization", f"Bearer {token}")
    put.add_header("Content-Type", "application/octet-stream")
    try:
        urllib.request.urlopen(put)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        sys.exit(f"ERROR subiendo imagen HTTP {e.code}: {raw}")

    # 4) esperar a que LinkedIn termine de PROCESAR la imagen. Si se postea antes
    #    de que esté "AVAILABLE", la tarjeta puede salir SIN foto. Best-effort:
    #    si no tenemos permiso de lectura, hacemos una espera fija y seguimos.
    status_url = f"{API}/images/{urllib.parse.quote(image_urn, safe='')}"
    for _ in range(15):
        time.sleep(1)
        chk = urllib.request.Request(status_url, method="GET")
        chk.add_header("Authorization", f"Bearer {token}")
        chk.add_header("X-Restli-Protocol-Version", "2.0.0")
        chk.add_header("LinkedIn-Version", VERSION)
        try:
            with urllib.request.urlopen(chk) as r:
                if json.loads(r.read().decode("utf-8")).get("status") == "AVAILABLE":
                    break
        except urllib.error.HTTPError:
            # sin permiso de lectura del estado de la imagen -> espera fija generosa
            # (si posteás antes de que LinkedIn termine de procesar, la tarjeta sale
            # SIN foto). Alternativa más robusta: NO pasar --image-url y dejar que
            # LinkedIn levante la og:image de la nota.
            time.sleep(18)
            break
    return image_urn


def _req(method: str, url: str, token: str, body: dict | None = None) -> tuple[int, dict, str]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-Restli-Protocol-Version", "2.0.0")
    req.add_header("LinkedIn-Version", VERSION)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            post_id = resp.headers.get("x-restli-id") or resp.headers.get("x-linkedin-id") or ""
            payload = json.loads(raw) if raw.strip() else {}
            return resp.status, payload, post_id
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        sys.exit(f"ERROR HTTP {e.code}: {raw}")


def check(creds: dict) -> None:
    token = creds["access_token"]
    org_id = creds["org_urn"].split(":")[-1]
    status, payload, _ = _req("GET", f"{API}/organizations/{org_id}", token)
    name = payload.get("localizedName") or payload.get("vanityName") or org_id
    print(json.dumps({"ok": True, "org": name, "org_urn": creds["org_urn"]}, ensure_ascii=False))


def publish(creds: dict, message: str, link: str | None, title: str | None,
            description: str | None, image_url: str | None, dry_run: bool) -> None:
    body = {
        "author": creds["org_urn"],
        "commentary": escape_commentary(message),
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    # Si hay link pero no pasaron miniatura, la sacamos de la og:image de la nota
    # y la SUBIMOS como thumbnail (confiable), en vez de rezar por el scrape de LinkedIn.
    if link and not image_url:
        image_url = fetch_og_image(link)
        if image_url:
            print(f"  (miniatura auto desde og:image: {image_url})", file=sys.stderr)

    thumb = None
    if image_url and not dry_run:
        thumb = upload_image(creds, image_url)

    if link:
        article = {"source": link}
        if title:
            article["title"] = title
        if description:
            article["description"] = description
        if thumb:
            article["thumbnail"] = thumb
        body["content"] = {"article": article}
    elif thumb:
        # post de imagen sin link
        body["content"] = {"media": {"id": thumb}}

    if dry_run:
        if image_url:
            body.setdefault("content", {})["_image_url"] = image_url
        print(json.dumps({"dry_run": True, "body": body}, ensure_ascii=False, indent=2))
        return

    status, payload, post_id = _req("POST", f"{API}/posts", creds["access_token"], body)
    pid = post_id or payload.get("id", "")
    url = f"https://www.linkedin.com/feed/update/{pid}/" if pid else ""
    print(json.dumps({"ok": True, "id": pid, "url": url}, ensure_ascii=False))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--message", "-m", help="texto del post (commentary).")
    ap.add_argument("--link", "-l", help="URL del artículo (tarjeta clickeable).")
    ap.add_argument("--title", help="título de la tarjeta del link.")
    ap.add_argument("--description", help="descripción de la tarjeta del link.")
    ap.add_argument("--image-url", help="URL pública de la imagen (miniatura de la tarjeta, o foto del post si no hay link).")
    ap.add_argument("--check", action="store_true", help="verifica token + página.")
    ap.add_argument("--dry-run", action="store_true", help="no publica, muestra el body.")
    args = ap.parse_args()

    creds = load_creds()
    if args.check:
        check(creds)
        return
    if not args.message:
        sys.exit("ERROR: falta --message.")
    publish(creds, args.message, args.link, args.title, args.description, args.image_url, args.dry_run)


if __name__ == "__main__":
    main()
