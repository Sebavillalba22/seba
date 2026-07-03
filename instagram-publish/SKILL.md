---
name: instagram-publish
description: Publish directly to Instagram (@estacionline) via the Meta Graph API — single photos, carousels (2-10 images), and stories (image or video). Use whenever the user asks to "publicar en Instagram", "subir un carrusel", "postear en IG", "subir una historia", or push content to Instagram. Optionally reposts the same post to the Facebook Page. Stdlib-only Python, no dependencies.
---

# instagram-publish

Publica directo en Instagram (@estacionline) usando la Graph API de Meta.
Soporta foto única, carrusel de 2 a 10 imágenes, e historias (imagen o video).

## Cuándo usar

- "publicá esto en Instagram" / "subí el carrusel a IG" / "posteá en IG"
- "subí una historia" (imagen o video)
- Opcional: repostear el mismo post en la página de Facebook

## Setup de credenciales (una sola vez)

Guardar en `instagram.json` (al lado de este archivo):

```json
{
  "username": "estacionline",
  "ig_user_id": "17841...",
  "page_id": "2249...",
  "access_token": "EAAG..."
}
```

El token es un **Page Access Token** con scopes `instagram_basic` e
`instagram_content_publish` (además de los de páginas). Sale del Graph API
Explorer igual que el de Facebook. Verificar:

```bash
python3 scripts/ig_publish.py --check
```

⚠️ **Instagram exige URLs públicas para las imágenes/videos** (no acepta
archivos locales). Subilas a un host público (ej. la biblioteca de medios de
WordPress de estacionline.com) y pasá las URLs.

## Uso

```bash
# foto única
python3 scripts/ig_publish.py --caption "Texto del posteo" --image "https://.../foto.jpg"

# carrusel (2-10 imágenes, EN ORDEN)
python3 scripts/ig_publish.py --caption "Texto" \
  --image "https://.../1.jpg" --image "https://.../2.jpg" --image "https://.../3.jpg"

# probar sin publicar (arma los containers y verifica, NO postea)
python3 scripts/ig_publish.py --dry-run --caption "x" --image "https://.../1.jpg"

# historia (imagen 9:16 1080x1920, o video MP4 9:16 ≤60s ≤100MB)
python3 scripts/ig_story.py --image-url "https://.../story.jpg"
python3 scripts/ig_story.py --video-url "https://.../story.mp4"
```

La salida es JSON con `ok`, el `media_id` y el `permalink` del post.

## Repost a la página de Facebook (opcional)

Requiere además `.credentials.json` con el token de la página
(`{"page_id": ..., "access_token": ...}`).

```bash
# publicar en IG y repostear en FB en el mismo comando
python3 scripts/ig_publish.py --caption "Texto" --image "URL1" --image "URL2" --repost-fb

# repostear un post que YA está en IG (el último, o por link)
python3 scripts/fb_repost_ig.py --latest
python3 scripts/fb_repost_ig.py --permalink "https://www.instagram.com/p/ABC123/"
```

El repost es UN solo posteo de feed con las fotos adjuntas — **nunca crea un
álbum**. ⚠️ Antes de repostear, mirá el feed de la página: si el crosspost
automático de Meta ya publicó el carrusel (post con "Publicado por
Instagram"), NO lo repitas — Facebook elimina el duplicado.

## Notas

- Carrusel: 2 a 10 imágenes; todas se recortan al aspecto de la primera
  (1080×1350, 4:5, es el formato ideal).
- En IG el link del caption **no es clickeable** — usar "link en bio".
- No hay posts de solo texto en IG.
- Errores de la Graph API se reportan con el mensaje exacto de Meta.
- Nunca commitear `instagram.json` ni `.credentials.json` — contienen tokens
  (ya están en `.gitignore`).
