#!/usr/bin/env python3
"""Flujo maestro de publicación de Estacionline: Instagram + Facebook en un paso.

Qué hace (en orden, con log de cada paso en logs/publicaciones.log):
  1. Valida las imágenes (URLs públicas; las locales se suben a WordPress si
     hay wordpress.json).
  2. Chequea duplicados: si un post reciente de IG tiene el mismo caption,
     aborta (salvo --force).
  3. Publica el carrusel/foto en Instagram.
  4. Espera y verifica si el crosspost automático de Meta apareció en la
     página de Facebook (post con el mismo texto). Si apareció, NO duplica.
  5. Si no apareció, repostea en la página: UN solo post de feed con las
     fotos adjuntas (attached_media) — nunca un álbum.
  6. Devuelve JSON con links/IDs de IG y FB y cómo se resolvió FB.

SEGURO ANTI-PUBLICACIÓN ACCIDENTAL: sin --approved no publica nada; muestra
el plan (caption + imágenes) y sale. El flag --approved solo debe pasarse
después de que el usuario aprobó el caption.

Credenciales (nunca hardcodeadas): instagram.json, .credentials.json y
wordpress.json al lado de SKILL.md, o env vars (FB_PAGE_ID,
FB_PAGE_ACCESS_TOKEN; ver publish.py).

Ejemplos:
  # vista previa (NO publica)
  master_publish.py --caption-file caption.txt --image https://.../1.jpg --image https://.../2.jpg

  # publicar (caption ya aprobado por el usuario)
  master_publish.py --caption-file caption.txt --image ... --image ... --approved

  # solo Instagram, sin tocar Facebook
  master_publish.py --caption "..." --image ... --approved --skip-fb
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
from publish import GRAPH, _die, _get, load_credentials, publish_multi_photo_post, upload_photo

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"

# cuánto esperar el crosspost automático de Meta antes de repostear a mano
AUTO_SHARE_WAIT_S = 180
AUTO_SHARE_POLL_S = 30


# ─────────────────────────── logging ───────────────────────────────

def log(step: str, msg: str) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    line = f"{_dt.datetime.now().isoformat(timespec='seconds')} [{step}] {msg}"
    print(f"  {line}", file=sys.stderr)
    with open(LOG_DIR / "publicaciones.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def die(step: str, msg: str) -> None:
    log(step, f"ERROR: {msg}")
    _die(f"[{step}] {msg}")


# ─────────────────────────── helpers ───────────────────────────────

def _fb_get(path: str, params: dict, token: str) -> dict:
    params = dict(params, access_token=token)
    return _get(f"{GRAPH}/{path}?" + urllib.parse.urlencode(params))


def _norm_text(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "")).strip().lower()


def strip_hashtag_block(caption: str) -> str:
    """Saca el bloque final de hashtags (para el repost manual en FB,
    donde los hashtags no suman)."""
    lines = caption.rstrip().splitlines()
    while lines:
        last = lines[-1].strip()
        if last and all(w.startswith("#") for w in last.split()):
            lines.pop()
        elif not last:
            lines.pop()
        else:
            break
    return "\n".join(lines).rstrip()


def resolve_images(images: list[str]) -> list[str]:
    """Convierte las imágenes a URLs públicas. Las rutas locales se suben a
    WordPress (requiere wordpress.json; ver wp_upload.py)."""
    out = []
    locals_ = [i for i in images if not i.startswith(("http://", "https://"))]
    if locals_:
        wp_file = ROOT / "wordpress.json"
        if not wp_file.exists():
            die("imagenes", f"hay {len(locals_)} imagen(es) locales pero no existe "
                            f"{wp_file}. Subilas a un host público y pasá las URLs, "
                            "o configurá wordpress.json (ver wordpress.example.json).")
        import wp_upload
        for img in images:
            if img.startswith(("http://", "https://")):
                out.append(img)
            else:
                url = wp_upload.upload(Path(img))
                log("imagenes", f"subida a WordPress: {img} -> {url}")
                out.append(url)
        return out
    return images


def check_ig_duplicate(ig_id: str, ig_token: str, caption: str) -> None:
    r = _fb_get(f"{ig_id}/media", {"fields": "id,caption,permalink", "limit": 10}, ig_token)
    want = _norm_text(caption)[:80]
    for m in r.get("data") or []:
        if want and _norm_text(m.get("caption", ""))[:80] == want:
            die("duplicados", f"ya existe un post de IG con este caption: "
                              f"{m.get('permalink')} — si es intencional, usá --force.")
    log("duplicados", "ok, no hay post reciente con el mismo caption")


def wait_for_auto_crosspost(page_id: str, page_token: str, caption: str,
                            since_ts: float) -> dict | None:
    """Espera a que el crosspost automático de Meta aparezca en el feed de la
    página. Devuelve el post si aparece, None si no."""
    want = _norm_text(caption)[:60]
    deadline = time.time() + AUTO_SHARE_WAIT_S
    while time.time() < deadline:
        time.sleep(AUTO_SHARE_POLL_S)
        r = _fb_get(f"{page_id}/feed",
                    {"fields": "id,message,created_time,permalink_url", "limit": 5},
                    page_token)
        for post in r.get("data") or []:
            created = post.get("created_time", "")
            try:
                cts = _dt.datetime.fromisoformat(created.replace("+0000", "+00:00")).timestamp()
            except ValueError:
                cts = 0
            if cts >= since_ts - 60 and want and _norm_text(post.get("message", "")).startswith(want):
                return post
        log("facebook", "todavía no apareció el crosspost automático, sigo esperando...")
    return None


# ─────────────────────────── main flow ─────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="Publicación maestra Estacionline (IG + FB).")
    ap.add_argument("--caption", help="caption aprobado (texto directo).")
    ap.add_argument("--caption-file", help="archivo con el caption aprobado (mejor para textos largos).")
    ap.add_argument("--image", "-i", action="append", default=[],
                    help="URL pública o ruta local (se sube a WP). Repetir en orden (1-10).")
    ap.add_argument("--approved", action="store_true",
                    help="OBLIGATORIO para publicar. Solo pasarlo después de que el usuario aprobó el caption.")
    ap.add_argument("--skip-fb", action="store_true", help="publicar solo en Instagram.")
    ap.add_argument("--force", action="store_true", help="saltear el chequeo de duplicados.")
    ap.add_argument("--fb-keep-hashtags", action="store_true",
                    help="en el repost manual a FB, conservar el bloque de hashtags.")
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

    # 1. imágenes → URLs públicas
    urls = resolve_images(args.image)
    log("imagenes", f"{len(urls)} imagen(es) listas")

    # 2. vista previa si no está aprobado
    if not args.approved:
        print(json.dumps({"ok": True, "preview": True,
                          "note": "NO publicado. Revisar caption y volver a correr con --approved.",
                          "caption": caption, "images": urls}, ensure_ascii=False, indent=2))
        sys.exit(2)

    # 3. anti-duplicado
    if not args.force:
        check_ig_duplicate(ig_id, ig_token, caption)

    # 4. publicar en Instagram
    log("instagram", f"publicando {'carrusel' if len(urls) > 1 else 'foto'} ({len(urls)} imagen/es)")
    t0 = time.time()
    media_id = ig_publish.publish(ig_id, ig_token, caption, urls)
    if not media_id:
        die("instagram", "no obtuve media_id de la publicación.")
    perma = _fb_get(media_id, {"fields": "permalink"}, ig_token).get("permalink")
    log("instagram", f"publicado: {perma} (media_id {media_id})")

    result = {"ok": True, "instagram": {"media_id": media_id, "permalink": perma}}

    # 5. Facebook: primero esperar el crosspost automático de Meta
    if args.skip_fb:
        result["facebook"] = {"mode": "skipped"}
    else:
        page_id, page_token = load_credentials(None, None)
        log("facebook", f"esperando hasta {AUTO_SHARE_WAIT_S}s el crosspost automático de Meta...")
        auto = wait_for_auto_crosspost(page_id, page_token, caption, t0)
        if auto:
            log("facebook", f"crosspost automático detectado: {auto.get('permalink_url')}")
            result["facebook"] = {"mode": "auto-crosspost", "post_id": auto.get("id"),
                                  "permalink": auto.get("permalink_url")}
        else:
            # 6. no apareció → repost manual (un solo post multi-foto, sin álbum)
            fb_caption = caption if args.fb_keep_hashtags else strip_hashtag_block(caption)
            log("facebook", "sin crosspost automático; reposteo por API (attached_media)")
            if len(urls) == 1:
                r = upload_photo(page_id, page_token, urls[0], caption=fb_caption)
            else:
                r = publish_multi_photo_post(page_id, page_token, fb_caption, urls)
            post_id = r.get("post_id") or r.get("id")
            fb_perma = None
            if post_id:
                info = _fb_get(post_id, {"fields": "permalink_url"}, page_token)
                fb_perma = info.get("permalink_url")
            log("facebook", f"reposteado: {fb_perma or post_id}")
            result["facebook"] = {"mode": "repost-api", "post_id": post_id, "permalink": fb_perma}

    log("fin", "flujo completo")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
