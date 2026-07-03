---
name: facebook-publish
description: Publish posts to a Facebook Page (fan page) via the Meta Graph API — text, photos, multi-photo posts (IG-carousel reposts), and link shares. Use whenever the user asks to "publicar en Facebook", "subir a la fan page", "postear en la página", "repostear el carrusel de Instagram en Facebook", share a note/photo on the Facebook page, or push content to Facebook. Stdlib-only Python, no dependencies.
---

# facebook-publish

Publica en una Página de Facebook (fan page) usando la Graph API de Meta.
Soporta texto, foto (archivo local o URL), varias fotos en un solo posteo
(repost de carrusel de IG) y compartir un link con preview.

## Cuándo usar

- "publicá esto en Facebook" / "subilo a la fan page" / "posteá en la página"
- "reposteá el carrusel de Instagram en Facebook"
- Compartir una nota de estacionline u otra URL en la Página
- Subir una foto (o varias) con epígrafe a la Página

## Setup de credenciales (una sola vez)

Publicar en una Página **siempre** requiere un **Page Access Token** de Meta.
Guardar las credenciales en `.credentials.json` (al lado de este archivo):

```json
{
  "page_id": "1234567890",
  "access_token": "EAAG..."
}
```

Alternativamente, exportar `FB_PAGE_ID` y `FB_PAGE_ACCESS_TOKEN` como env vars.

Cómo conseguir el token (token de Página que **no expira**):
1. Crear una app en https://developers.facebook.com/ (tipo "Business").
2. En Graph API Explorer, elegir la app y la Página, pedir permisos
   `pages_show_list`, `pages_manage_posts`, `pages_read_engagement`.
3. Generar un **User Access Token**, cambiarlo por uno de larga duración, y
   pedir `GET /me/accounts` para obtener el **Page Access Token** de la Página
   (ese no expira mientras el user token de larga duración siga vivo).
4. El `page_id` sale de `GET /me/accounts` también.

Verificar que quedó bien:

```bash
python3 scripts/publish.py --check
```

## Uso

```bash
# texto
python3 scripts/publish.py --message "Hola Funes 👋"

# texto + foto local
python3 scripts/publish.py --message "Mirá esto" --image /ruta/foto.jpg

# texto + foto por URL
python3 scripts/publish.py --message "Mirá esto" --image https://.../foto.jpg

# varias fotos (2-10) en UN solo posteo — repost estilo carrusel de IG
python3 scripts/publish.py --message "Mirá esto" \
  --image https://.../1.jpg --image https://.../2.jpg --image https://.../3.jpg

# compartir un link (tarjeta con preview)
python3 scripts/publish.py --message "Nota nueva en el portal" --link https://estacionline.com/...
```

La salida es JSON con `ok`, el `result` de la API y un `permalink` al posteo.

## Repostear un carrusel de Instagram en Facebook (SIN álbum)

**Regla fija: cuando el pedido es repostear un carrusel de IG en la página,
publicar UN solo posteo de feed con las fotos adjuntas. NUNCA crear un álbum
(`/albums`), NUNCA publicar las fotos como posts sueltos, y NO ofrecer
alternativas ni preguntar: ejecutar directo el flujo de abajo.**

La vía preferida — repostear un post que **ya está publicado en IG** (trae
solo el caption y las imágenes; no hay que pasar nada a mano):

```bash
# el último post de IG
python3 scripts/fb_repost_ig.py --latest

# por link del post de IG
python3 scripts/fb_repost_ig.py --permalink "https://www.instagram.com/p/ABC123/"

# por media id (lo devuelve ig_publish.py)
python3 scripts/fb_repost_ig.py --media-id 1789...

# ver qué haría sin publicar
python3 scripts/fb_repost_ig.py --latest --dry-run
```

O todo junto: publicar el carrusel en IG y repostearlo en FB en un comando:

```bash
python3 scripts/ig_publish.py --caption "Texto" \
  --image https://.../1.jpg --image https://.../2.jpg --repost-fb
```

Cómo funciona por dentro (lo hace solo `publish.py` con varias `--image`):
cada foto se sube a `/{page-id}/photos` con `published=false` (no genera
posteo propio) y después se crea **un único** post de `/{page-id}/feed` con
`attached_media`. En el celular las fotos se deslizan de a una, como el
crosspost automático del teléfono.

Nota técnica (para no volver a ofrecer "opciones"): la Graph API no expone el
crosspost nativo de IG→FB (el del teléfono lo hace Meta por adentro y el
auto-share de Accounts Center no se dispara para posts publicados por API).
El posteo multi-foto de arriba es el equivalente orgánico que existe por API;
la única diferencia es cosmética: el preview del feed puede mostrarse como
mosaico en vez de "primera foto con puntitos". No es un álbum.

## Notas

- Con una sola `--image`, el post se crea como foto (`/{page-id}/photos`) y
  `--message` pasa a ser el epígrafe. Con varias `--image` (2-10), un solo
  post de feed con `attached_media`. Sin imagen, post de feed (`/{page-id}/feed`).
- `--image` y `--link` no se combinan en un mismo posteo.
- Errores de la Graph API se reportan con el mensaje exacto de Meta (token
  vencido, permiso faltante, etc.).
- Nunca commitear `.credentials.json`, `pages.json`, `instagram.json` ni
  `x_credentials.json` — contienen tokens (ya están en `.gitignore`).
