# facebook-publish — Facebook + Instagram (Windows / Mac / Linux)

Publicar en las páginas de Facebook de la red **y** en Instagram (@estacionline),
por la Graph API de Meta. Solo Python estándar, sin dependencias.

> ⚠️ Esta carpeta contiene `.credentials.json`, `pages.json` e `instagram.json`
> con **tokens que NO expiran** (secretos). No la subas a la nube pública, no la
> commitees a git, no la compartas por link público.

---

## 1. Requisitos

- **Python 3** instalado.
  - Windows: probá `python --version`. Si no está, instalalo de
    https://www.python.org/downloads/ (tildá "Add python.exe to PATH").
  - Mac/Linux: `python3 --version` (ya viene en Mac).
- No hace falta nada más.

## 2. Dónde poner la carpeta

Da igual la ubicación: los scripts buscan las credenciales relativo a la
carpeta, no a una ruta fija. Ej.: `C:\Users\TU_USUARIO\facebook-publish\`
o `~/facebook-publish/`.

En los comandos de abajo:
- **Windows:** `python scripts\publish.py ...`
- **Mac/Linux:** `python3 scripts/publish.py ...`

---

## 3. FACEBOOK

### Verificar
```
python scripts/publish.py --check
```

### Publicar a la página por defecto (Estacionline)
```
python scripts/publish.py --message "Título

Bajada de la nota" --link "https://estacionline.com/..."
```

### Publicar a cualquier página por nombre
```
python scripts/publish_to.py --list

python scripts/publish_to.py --page estacionline --message "Título

Bajada" --link "https://estacionline.com/..."
python scripts/publish_to.py --page funes   --message "..." --link "https://..."
python scripts/publish_to.py --page roldan  --message "..." --link "https://..."
python scripts/publish_to.py --page timbues --message "..." --link "https://puertotimbues.com/..."
```

### Con foto (archivo local o URL)
```
python scripts/publish_to.py --page estacionline --message "Epígrafe" --image "ruta/foto.jpg"
python scripts/publish_to.py --page estacionline --message "Epígrafe" --image "https://.../foto.jpg"
```

### Varias fotos en UN solo posteo (repost de carrusel, SIN álbum)
```
python scripts/publish_to.py --page estacionline --message "Epígrafe" \
  --image "https://.../1.jpg" --image "https://.../2.jpg" --image "https://.../3.jpg"
```
Sube cada foto sin publicar y crea un único post de feed con las fotos
adjuntas (`attached_media`). En el celular se deslizan de a una. Nunca usa
álbumes.

### Repostear en FB un post que ya está en Instagram
```
python scripts/fb_repost_ig.py --latest                                # el último post de IG
python scripts/fb_repost_ig.py --permalink "https://www.instagram.com/p/ABC123/"
python scripts/fb_repost_ig.py --latest --dry-run                      # ver sin publicar
```
Trae caption + imágenes del post de IG por API y publica el posteo multi-foto
de arriba en la página por defecto (Estacionline). Nota: la Graph API no
expone el crosspost nativo de IG (el "automático" del teléfono); este posteo
multi-foto es el equivalente orgánico — la única diferencia es el preview del
feed (mosaico en vez de puntitos).

Páginas configuradas: **Estacionline, Estación Funes, Estación Roldán, Puerto Timbúes.**
Formato acordado: **título + (línea en blanco) + bajada + link.**

---

## 4. INSTAGRAM (@estacionline) — fotos y carruseles

Verificar:
```
python scripts/ig_publish.py --check
```

⚠️ **Instagram exige URLs públicas para las imágenes** (no acepta archivos
locales). Subí las imágenes a un host público (ej. la biblioteca de medios de
WordPress de estacionline.com) y pasá las URLs.

Foto única:
```
python scripts/ig_publish.py --caption "Texto del posteo" --image "https://.../foto.jpg"
```

Carrusel (2 a 10 imágenes, en orden):
```
python scripts/ig_publish.py --caption "Texto" \
  --image "https://.../1.jpg" --image "https://.../2.jpg" --image "https://.../3.jpg"
```

Carrusel en IG **y** repost en la página de FB, todo en un comando:
```
python scripts/ig_publish.py --caption "Texto" \
  --image "https://.../1.jpg" --image "https://.../2.jpg" --repost-fb
```

Probar sin publicar (arma el container y verifica, NO postea):
```
python scripts/ig_publish.py --dry-run --caption "x" --image "https://.../1.jpg"
```

Notas de IG: las imágenes 1080×1350 (4:5) son el formato ideal. En IG el link
del epígrafe **no es clickeable** (usar "link en bio"). No hay posts de solo texto.

---

## 4.5 X / TWITTER (@estacionline) — texto + link

Credenciales en `x_credentials.json` (OAuth 1.0a):
`{api_key, api_secret, access_token, access_secret}`.

Verificar auth (no postea):
```
python scripts/x_publish.py --check
```

Postear (texto + link, máx 280 caracteres):
```
python scripts/x_publish.py --text "Título de la nota https://estacionline.com/..."
```

⚠️ La cuenta de API de X es **pay-per-use**: necesita **crédito** (mínimo US$5,
no expira) cargado en la cuenta de desarrollador. Sin crédito, X devuelve
402 "CreditsDepleted". La suscripción personal de X (Premium) NO cubre la API.
Cargar crédito: console.x.com → Facturación → Comprar créditos.

App de X: "Estacionline" (pay-per-use), permisos Read & Write, OAuth 1.0a.

---

## 5. Si algún día deja de postear

Los tokens no expiran, pero si fallan, regeneralos desde el Graph API Explorer
de la app **Estacionline Poster** (App ID 1586763299463861) con los permisos
`pages_show_list`, `pages_manage_posts`, `pages_read_engagement`,
`instagram_basic`, `instagram_content_publish`, y volvé a generar
`pages.json` / `.credentials.json` / `instagram.json` con `scripts/setup_token.py`.

---

## Archivos

- `scripts/publish.py` — publicar a una página de FB (texto / foto(s) / link). Varias `--image` = un solo post multi-foto. `--check`.
- `scripts/publish_to.py` — wrapper para elegir página de FB por nombre.
- `scripts/fb_repost_ig.py` — repostear en FB un post ya publicado en IG (`--latest`, `--permalink`, `--media-id`). Sin álbum.
- `scripts/ig_publish.py` — publicar en Instagram (foto o carrusel). `--repost-fb` repostea en FB. `--check`, `--dry-run`.
- `scripts/x_publish.py` — publicar en X/Twitter (texto + link). `--check`.
- `scripts/ig_fetch.py` — leer posteos ya publicados en Instagram (para repostear o verificar).
- `scripts/linkedin_publish.py` / `scripts/linkedin_refresh.py` — publicar en LinkedIn y renovar su `refresh_token`. Credenciales en `linkedin.json`.
- `scripts/tiktok_publish.py` — subir video a TikTok. Credenciales en `tiktok.json`.
- `scripts/youtube_publish.py` — subir video a YouTube. Credenciales en `youtube.json`.
- `scripts/wp_publish.py` — publicar en WordPress (estacionline.com). Credenciales en `wordpress.json`.
- `scripts/setup_token.py`, `scripts/token_bridge.py` — regenerar tokens (Meta).
- `.credentials.json` — página FB por defecto (Estacionline). **SECRETO.**
- `pages.json` — las 4 páginas de FB con sus tokens. **SECRETO.**
- `instagram.json` — ig_user_id + token de IG. **SECRETO.**
- `x_credentials.json` — claves OAuth 1.0a de X. **SECRETO.**
- `app.json`, `linkedin.json`, `tiktok.json`, `youtube.json`, `wordpress.json` — credenciales de las demás plataformas. **SECRETO.** Formato en los `*.example.json`.
