---
name: jarvis-haz-lo-tuyo
description: Grandmaster publishing skill for Estacionline — the full pipeline from raw material to published content. Triggers on "jarvis haz lo tuyo", "jarvis", or when the user hands over photos/placas/material to publish. Designs the carousel, writes the Estacionline-style caption, waits for caption approval, publishes to Instagram, NEVER posts a separate copy to Facebook, then asks "¿Armo web?" and (only if confirmed) creates the web article via the existing web-publishing skill with the real Instagram embed inside. Stdlib-only Python, no dependencies.
---

# jarvis haz lo tuyo — Skill grandmaster de Estacionline

Pipeline: material → copy → **aprobación** → Instagram → *(Facebook
cancelado)* → **"¿Armo web?"** → nota web con el embed real del post de IG.

**Regla central: Instagram es el origen.** La web toma como referencia el
post de IG recién publicado y lo inserta como embed real. Facebook queda
cancelado salvo réplica nativa de Meta — nunca una publicación separada.

## ⛔ REGLA FACEBOOK (leer antes que nada)

- **NUNCA publicar en Facebook como post separado.** Ni con `publish.py`, ni
  con `fb_repost_ig.py`, ni con álbum, ni con foto+caption, ni "solo esta vez".
  Esos scripts NO existen en esta skill a propósito.
- **NUNCA usar la skill facebook-publish como réplica manual del post de IG.**
- **NO hay fallback**: si la réplica nativa no está disponible, Facebook se
  cancela y punto. `master_publish.py` lo deja en el log:
  `"Facebook cancelado: no se publica copia separada"`.
- La única vía admitida es la **réplica nativa de Meta** (el auto-share de
  Accounts Center, corre del lado de Meta solo). Se puede *verificar* con
  `--wait-native 90` (solo lectura del feed), jamás provocar por API.
- La prioridad es **Instagram + Web**. No gastar tiempo en Facebook.

## Flujo obligatorio

### 1. Recibir material
El usuario entrega fotos, placas, portada o material ya preparado, con o sin
indicaciones (producto, promo, estilo, colores, slides, tono, datos).
- Detectar a qué apunta el material: **Instagram**, **web** o **ambos**
  (placas 4:5 → IG; texto largo/nota → web; foto + info → probablemente ambos).
- Si el usuario indicó slides/colores/estilo → respetarlo. Si no, decidir
  solo (estructura portada → intermedios → cierre, identidad de
  `IDENTIDAD.md`, 1080×1350). No preguntar por decisiones menores.
- Si faltan datos importantes para una noticia (fecha, lugar, fuente,
  precio), se pueden **inferir con criterio editorial**, pero SIEMPRE marcar
  qué se infirió al mostrar el caption/la nota, antes de publicar.

### 2. Copy de Instagram + aprobación
- Generar el caption con el formato Estacionline (gancho, descripción,
  beneficios si aplica, CTA, hashtags — ver plantilla abajo). Si está
  instalada la skill de copys de Estacionline, usar su formato exacto.
- **Mostrar el caption completo al usuario y esperar.** Cambios → corregir y
  volver a mostrar. **PROHIBIDO publicar sin aprobación explícita.**
- El script lo refuerza: sin `--approved` solo hay vista previa.

### 3. Publicar en Instagram
```bash
python3 scripts/master_publish.py --caption-file caption.txt \
  --image "https://.../1.jpg" --image "https://.../2.jpg" --approved
```
- Imágenes EN ORDEN; URLs públicas o rutas locales (se suben solas a
  WordPress si hay `wordpress.json`).
- El script chequea duplicados (registro local `logs/publicados.jsonl` +
  últimos posts de IG) y aborta si el contenido ya se publicó (`--force`
  solo si el usuario lo confirma).
- Guarda automáticamente: media_id, permalink, caption final, fecha/hora y
  assets usados, y devuelve además el `embed_html` del post.
- Facebook: el propio script registra la cancelación. No hacer nada más.

### 4. Preguntar SIEMPRE: "¿Armo web?"
Después de publicar en IG, preguntar al usuario exactamente eso: **"¿Armo
web?"** (puede haber otra persona trabajando la misma noticia).
- **No** → reportar resultado (paso 8) y terminar.
- **Sí** → recién ahí empieza el armado web. **PROHIBIDO crear borradores o
  publicar en la web antes de esta confirmación.**

### 5. Crear la noticia web (con la skill web existente)
- **Primero buscar la skill de publicación web de Estacionline ya
  instalada** (en `~/.claude/skills/` — nombres tipo `web-publish`,
  `estacionline-web`, `wordpress-*`, `notas-*`) y usar ESA skill con su
  flujo habitual (estado borrador/revisión/publicado según su
  configuración). No inventar un flujo nuevo si ya existe.
- Solo si no hay ninguna skill web instalada: avisar al usuario y ofrecer el
  respaldo `scripts/wp_post.py` (crea la nota por la REST API de WordPress,
  estado `draft` por defecto).
- La nota debe incluir: **título periodístico**, **bajada/resumen**,
  **cuerpo bien escrito**, **portada** como siempre, **categoría y
  etiquetas**, **SEO básico** (si la skill web lo maneja), **slug limpio** e
  **imagen destacada**.

### 6. Insertar el embed REAL del post de Instagram
- Obtener el código de inserción del post recién publicado:
  ```bash
  python3 scripts/ig_embed.py --media-id <MEDIA_ID_DEL_PASO_3>
  ```
  (usa oEmbed de la API si hay permiso; si no, genera el blockquote oficial
  de Instagram + `embed.js` — el mismo código del botón "Insertar").
  `master_publish.py` ya devuelve `embed_html` listo también.
- Insertar ese HTML **dentro del cuerpo de la nota**, después del primer o
  segundo párrafo (o antes del cierre si conviene editorialmente). Debe
  quedar el post embebido visible — **no un link pegado ni texto plano**.
  Si la web soporta un bloque/shortcode de embed propio, usarlo.
- Si por algún motivo NO se pudo obtener el embed: **no publicar la nota
  sin embed en silencio**. Preguntar al usuario: *"No pude obtener el código
  de inserción de Instagram. ¿Querés que deje la nota como borrador sin
  embed o lo resolvemos antes?"*

### 7. Chequeo de duplicados web (antes de crear la nota)
```bash
python3 scripts/wp_post.py --find "palabras clave del título"
```
Revisar por: título parecido, slug parecido, imagen repetida, fecha cercana,
post de IG ya embebido, tema/keywords similares (buscar 2-3 variantes de
palabras clave). Si aparece un posible duplicado → **avisar al usuario y
esperar su decisión** antes de continuar.

### 8. Reporte final (siempre)
Devolver al usuario:
- Link e ID del post de Instagram.
- Estado de Facebook: **"cancelado / no se publicó copia separada"** (o el
  link de la réplica nativa si `--wait-native` la detectó).
- Si se hizo web: link/ID de la nota + confirmación de que el embed de IG
  quedó insertado (y en qué posición).
- Resumen de acciones + qué datos se infirieron.
- Si algo falló: el paso exacto (está en `logs/publicaciones.log`).

## Plantilla de copy (si no está la skill de copys)
```
[GANCHO/TÍTULO — corto, fuerte, puede llevar 1 emoji]

[Descripción: qué es, para quién, por qué importa. 2-4 líneas.]

✅ beneficio/dato 1
✅ beneficio/dato 2   (solo si aplica)

[CTA: "📲 Escribinos al +54 9 341 546-0424" / "👉 Link en bio" / "Más info en estacionline.com"]

#Funes #Roldán #SantaFe [+ hashtags del rubro, 5-10]
```
Tono: cercano, comercial, argentino. Links de IG no clickeables → "link en
bio". Sin "deslizá" ni referencias que no funcionen fuera de IG.

## Manejo de errores
- Token/permisos: `python3 scripts/ig_publish.py --check`; si falla,
  regenerar tokens (app "Estacionline Poster", scopes `instagram_basic`,
  `instagram_content_publish`, `pages_*`).
- Imagen rechazada: URL pública accesible, JPG/PNG, aspecto 4:5–1.91:1, <8MB.
- Container ERROR/timeout: reintentar 1 vez; revisar formato.
- WordPress 401/403: regenerar el application password (`wordpress.json`).
- Cada paso queda con timestamp en `logs/publicaciones.log`; el historial de
  publicaciones en `logs/publicados.jsonl`.

## Setup (una sola vez)
- `instagram.json`: `{username, ig_user_id, page_id, access_token}`.
- `.credentials.json` (opcional): token de la página de FB — SOLO se usa
  para la verificación de lectura `--wait-native`, jamás para publicar.
- `wordpress.json` (recomendado): `{base_url, username, app_password}` —
  habilita subir slides/portadas y el respaldo `wp_post.py`.
- Tokens SIEMPRE en estos archivos (gitignoreados) o env vars — nunca
  hardcodeados en el código.

## Herramientas
- `scripts/master_publish.py` — el flujo principal (IG + registro + FB cancelado).
- `scripts/ig_embed.py` — código de inserción del post de IG.
- `scripts/wp_post.py` — respaldo web: `--find` duplicados / crear nota draft.
- `scripts/wp_upload.py` — subir imágenes a WordPress (URLs públicas).
- `scripts/ig_publish.py` / `scripts/ig_story.py` — IG directo / historias.
