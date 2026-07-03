#!/usr/bin/env python3
"""«jarvis haz lo tuyo» — publicación en Instagram para Estacionline.

REGLA FACEBOOK (fija): este script NO publica en Facebook. Nunca. No hay
post separado, no hay réplica manual, no hay fallback. La única vía admitida
es la réplica NATIVA de Meta (el auto-share de Accounts Center, que corre
del lado de Meta sin intervención). Con --wait-native N se puede verificar
pasivamente si esa réplica apareció en la página (solo LECTURA del feed).
Si no existe/no aparece, se registra en el log:
  "Facebook cancelado: no se publica copia separada"

Qué hace:
  1. Valida las imágenes (URLs públicas; las locales se suben a WordPress
     si hay wordpress.json).
  2. Anti-duplicado: caption contra el registro local (logs/publicados.jsonl)
     y contra los últimos posts de IG.
  3. Publica foto/carrusel en Instagram (previa aprobación: sin --approved
     solo muestra la vista previa y sale).
  4. Registra la publicación (media_id, permalink, caption, fecha, assets)
     en logs/publicados.jsonl.
  5. Facebook: cancelado (ver regla arriba). Opcionalmente verifica la
     réplica nativa.
  6. Devuelve JSON con todo + el código de inserción (embed) del post,
     listo para usar en la nota web.

Ejemplos:
  # vista previa (NO publica)
  master_publish.py --caption-file caption.txt --image URL1 --image URL2

  # publicar (caption aprobado por el usuario)
  master_publish.py --caption-file caption.txt --image URL1 --image URL2 --approved

  # publicar y verificar 90s si Meta replicó nativamente en la página
  master_publish.py --caption-file caption.txt --image URL1 --approved --wait-native 90
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

import ig_publish
from ig_publish import GRAPH, _die, _get

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"
REGISTRY = LOG_DIR / "publicados.jsonl"
FB_CRED_FILE = ROOT / ".credentials.json"

FB_CANCEL_MSG = "Facebook cancelado: no se publica copia separada"


# ─────────────────────────── logging / registro ────────────────────

def log(step: str, msg: str) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    line = f"{_dt.datetime.now().isoformat(timespec='seconds')} [{step}] {msg}"
    print(f"  {line}", file=sys.stderr)
    with open(LOG_DIR / "publicaciones.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def die(step: str, msg: str) -> None:
    log(step, f"ERROR: {msg}")
    _die(f"[{step}] {msg}")


def registry_append(entry: dict) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    with open(REGISTRY, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def registry_entries() -> list[dict]:
    if not REGISTRY.exists():
        return []
    out = []
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


# ─────────────────────────── helpers ───────────────────────────────

def _norm_text(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "")).strip().lower()


def _ig_get(path: str, params: dict, token: str) -> dict:
    return _get(path, dict(params, access_token=token))


def resolve_images(images: list[str]) -> list[str]:
    """Convierte las imágenes a URLs públicas. Las rutas locales se suben a
    WordPress (requiere wordpress.json; ver wp_upload.py)."""
    locals_ = [i for i in images if not i.startswith(("http://", "https://"))]
    if not locals_:
        return images
    wp_file = ROOT / "wordpress.json"
    if not wp_file.exists():
        die("imagenes", f"hay {len(locals_)} imagen(es) locales pero no existe "
                        f"{wp_file}. Subilas a un host público y pasá las URLs, "
                        "o configurá wordpress.json (ver wordpress.example.json).")
    import wp_upload
    out = []
    for img in images:
        if img.startswith(("http://", "https://")):
            out.append(img)
        else:
            url = wp_upload.upload(Path(img))
            log("imagenes", f"subida a WordPress: {img} -> {url}")
            out.append(url)
    return out


def check_duplicates(ig_id: str, ig_token: str, caption: str) -> None:
    want = _norm_text(caption)[:80]
    if not want:
        return
    # 1. registro local de esta skill
    for e in registry_entries():
        if _norm_text(e.get("caption", ""))[:80] == want:
            die("duplicados", f"este contenido ya fue publicado el {e.get('fecha')}: "
                              f"{e.get('permalink')} — si es intencional, usá --force.")
    # 2. últimos posts reales de IG
    r = _ig_get(f"{ig_id}/media", {"fields": "id,caption,permalink", "limit": 10}, ig_token)
    for m in r.get("data") or []:
        if _norm_text(m.get("caption", ""))[:80] == want:
            die("duplicados", f"ya existe un post de IG con este caption: "
                              f"{m.get('permalink')} — si es intencional, usá --force.")
    log("duplicados", "ok, contenido no publicado antes")


def build_embed(permalink: str) -> str:
    """Código de inserción oficial de Instagram (blockquote + embed.js).
    No requiere API: embed.js lo transforma en el post embebido real."""
    p = permalink.rstrip("/") + "/"
    return (
        f'<blockquote class="instagram-media" data-instgrm-captioned '
        f'data-instgrm-permalink="{p}?utm_source=ig_embed" data-instgrm-version="14" '
        f'style="background:#FFF; border:0; border-radius:3px; margin:1px auto; '
        f'max-width:540px; min-width:326px; padding:0; width:99.375%;">'
        f'<a href="{p}" target="_blank" rel="noopener">Ver esta publicación en Instagram</a>'
        f'</blockquote>\n'
        f'<script async src="https://www.instagram.com/embed.js"></script>'
    )


def check_native_replica(caption: str, since_ts: float, wait_s: int) -> dict:
    """SOLO LECTURA: mira el feed de la página para ver si la réplica nativa
    de Meta apareció. Jamás publica."""
    if not FB_CRED_FILE.exists():
        return {"checked": False, "note": "sin .credentials.json; no se verificó la réplica nativa"}
    try:
        cred = json.loads(FB_CRED_FILE.read_text(encoding="utf-8"))
        page_id, token = cred["page_id"], cred["access_token"]
    except (json.JSONDecodeError, KeyError, OSError) as e:
        return {"checked": False, "note": f"no pude leer credenciales de página: {e}"}
    want = _norm_text(caption)[:60]
    deadline = time.time() + max(wait_s, 1)
    while True:
        try:
            r = _get(f"{page_id}/feed", {"fields": "id,message,created_time,permalink_url",
                                         "limit": 5, "access_token": token})
        except SystemExit:
            return {"checked": False, "note": "error leyendo el feed de la página"}
        for post in r.get("data") or []:
            try:
                cts = _dt.datetime.fromisoformat(
                    post.get("created_time", "").replace("+0000", "+00:00")).timestamp()
            except ValueError:
                cts = 0
            if cts >= since_ts - 60 and want and _norm_text(post.get("message", "")).startswith(want):
                return {"checked": True, "native_replica": True,
                        "post_id": post.get("id"), "permalink": post.get("permalink_url")}
        if time.time() >= deadline:
            return {"checked": True, "native_replica": False}
        log("facebook", "réplica nativa todavía no visible; sigo mirando (solo lectura)...")
        time.sleep(min(30, wait_s))


# ─────────────────────────── main flow ─────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="jarvis haz lo tuyo — publicar en Instagram (FB cancelado).")
    ap.add_argument("--caption", help="caption aprobado (texto directo).")
    ap.add_argument("--caption-file", help="archivo con el caption aprobado (mejor para textos largos).")
    ap.add_argument("--image", "-i", action="append", default=[],
                    help="URL pública o ruta local (se sube a WP). Repetir en orden (1-10).")
    ap.add_argument("--approved", action="store_true",
                    help="OBLIGATORIO para publicar. Solo pasarlo después de que el usuario aprobó el caption.")
    ap.add_argument("--force", action="store_true", help="saltear el chequeo de duplicados.")
    ap.add_argument("--wait-native", type=int, default=0, metavar="SEG",
                    help="verificar (solo lectura) hasta SEG segundos si la réplica nativa "
                         "de Meta apareció en la página. 0 = no verificar.")
    args = ap.parse_args()

    if args.caption_file:
        caption = Path(args.caption_file).read_text(encoding="utf-8").strip()
    elif args.caption is not None:
        caption = args.caption
    else:
        die("entrada", "falta el caption: --caption o --caption-file.")
    if not args.image:
        die("entrada", "falta al menos una --image.")

    ig_id, ig_token = ig_publish.load_ig()

    urls = resolve_images(args.image)
    log("imagenes", f"{len(urls)} imagen(es) listas")

    if not args.approved:
        print(json.dumps({"ok": True, "preview": True,
                          "note": "NO publicado. Revisar caption y volver a correr con --approved.",
                          "caption": caption, "images": urls}, ensure_ascii=False, indent=2))
        sys.exit(2)

    if not args.force:
        check_duplicates(ig_id, ig_token, caption)

    log("instagram", f"publicando {'carrusel' if len(urls) > 1 else 'foto'} ({len(urls)} imagen/es)")
    t0 = time.time()
    media_id = ig_publish.publish(ig_id, ig_token, caption, urls)
    if not media_id:
        die("instagram", "no obtuve media_id de la publicación.")
    perma = _ig_get(media_id, {"fields": "permalink"}, ig_token).get("permalink")
    log("instagram", f"publicado: {perma} (media_id {media_id})")

    fecha = _dt.datetime.now().isoformat(timespec="seconds")
    registry_append({"fecha": fecha, "media_id": media_id, "permalink": perma,
                     "caption": caption, "assets": urls})
    log("registro", f"guardado en {REGISTRY.name}")

    # Facebook: CANCELADO. Solo se admite la réplica nativa de Meta.
    facebook: dict = {"status": "cancelado", "note": FB_CANCEL_MSG}
    log("facebook", FB_CANCEL_MSG)
    if args.wait_native > 0:
        nat = check_native_replica(caption, t0, args.wait_native)
        facebook["native_check"] = nat
        if nat.get("native_replica"):
            log("facebook", f"réplica NATIVA de Meta detectada (no la hicimos nosotros): "
                            f"{nat.get('permalink')}")
        else:
            log("facebook", "réplica nativa no detectada; no se hace nada (regla: sin copia separada)")

    result = {
        "ok": True,
        "instagram": {"media_id": media_id, "permalink": perma, "fecha": fecha,
                      "embed_html": build_embed(perma) if perma else None},
        "facebook": facebook,
    }
    log("fin", "flujo completo")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
