---
name: estacionline-publish
description: Master publishing skill for Estacionline — full pipeline from photos/content to published post. Designs the carousel (slides, order, colors), writes the caption in Estacionline's style, shows the caption for approval, publishes to Instagram (@estacionline) and automatically shares/reposts to the Facebook Page without asking again. Use whenever the user asks to "publicar", "armar el posteo", "subir el carrusel", "hacer el post de X", or hands over photos/material for a post. Stdlib-only Python, no dependencies.
---

# estacionline-publish — Skill master de publicación

Pipeline completo: material → carrusel → copy → **aprobación del usuario** →
Instagram → Facebook automático. Una sola skill, un solo flujo.

## Flujo obligatorio (en este orden, sin saltear pasos)

### 1. Entrada y análisis
El usuario entrega fotos/imágenes/material y (opcional) instrucciones:
producto, promoción, estilo, colores, cantidad de slides, tono, datos
comerciales. Analizar el material antes de decidir nada.

### 2. Diseño del carrusel (decidir solo, no preguntar)
- **Si el usuario indicó** cantidad de slides, colores o estilo → respetarlo
  al pie de la letra.
- **Si no indicó**, decidir automáticamente según el contenido:
  - Cantidad de slides: la mínima que cuente la historia con claridad
    (3-6 es lo habitual; 1 sola si el material no da para más; máx. 10).
  - Estructura: **portada** (gancho grande + imagen más fuerte) → **slides
    intermedios** (un dato/beneficio por slide, texto corto y legible) →
    **cierre** (llamado a la acción + marca).
  - Identidad visual Estacionline: ver `IDENTIDAD.md` (colores, logo,
    tipografía). Prioridad: claridad comercial, legibilidad, atractivo.
- Formato: **1080×1350 (4:5)**. Todas las slides al mismo aspecto (IG
  recorta el carrusel al aspecto de la primera).
- Generación de slides: armar HTML por slide y capturar con Playwright a
  1080×1350, o usar las fotos directas si el usuario ya las trae listas.
- NO pedir confirmación por decisiones menores de diseño. Preguntar solo si
  falta información crítica (ej.: precio de una promo que hay que publicar).

### 3. Copy (formato Estacionline)
Si está instalada la skill de copys de Estacionline, usar ese formato y
parámetros. Si no, usar este formato por defecto:

```
[GANCHO/TÍTULO — corto, fuerte, puede llevar 1 emoji]

[Descripción comercial: qué es, para quién, por qué importa. 2-4 líneas.]

[Beneficios en viñetas, si aplica:]
✅ beneficio 1
✅ beneficio 2

[CTA: "📲 Escribinos al +54 9 341 546-0424" / "👉 Link en bio" /
 "Visitanos en ..." — según el objetivo del post]

[bloque final de hashtags: locales + rubro, 5-10]
#Funes #Roldán #SantaFe ...
```

Reglas del copy:
- Pensado para Instagram, pero tiene que funcionar tal cual en Facebook
  (el crosspost usa el mismo texto). Nada de "deslizá" que no aplique en FB.
- Links en el caption de IG **no son clickeables** → usar "link en bio" si
  hace falta dirigir a la web.
- Tono: cercano, comercial, argentino, sin exagerar mayúsculas.

### 4. APROBACIÓN — puerta obligatoria
**Mostrar SIEMPRE al usuario, antes de publicar:** el caption final completo
y la lista/preview de slides en orden. Esperar respuesta:
- Pide cambios → aplicarlos y volver a mostrar.
- Aprueba → recién ahí pasar al paso 5.
**PROHIBIDO publicar (en IG o FB) sin la aprobación explícita del caption.**
El script lo refuerza: sin `--approved` solo muestra la vista previa.

### 5. Publicar (un solo comando, IG + FB automático)
Con el caption aprobado, ejecutar **sin volver a preguntar nada** (la
aprobación del caption YA incluye Facebook — no pedir confirmación extra):

```bash
python3 scripts/master_publish.py --caption-file caption.txt \
  --image "https://.../1.jpg" --image "https://.../2.jpg" --approved
```

- Guardar el caption aprobado en un archivo (`caption.txt`) y usar
  `--caption-file` (evita problemas de comillas/UTF-8 en Windows).
- Las imágenes van EN ORDEN. Pueden ser URLs públicas o rutas locales (las
  locales se suben solas a WordPress si existe `wordpress.json`).
- El script hace todo: chequeo anti-duplicado → publica en IG → espera hasta
  3 min el **crosspost automático de Meta** en la página → si no aparece,
  repostea por API (un solo post de feed con `attached_media`, **nunca un
  álbum**, sin el bloque de hashtags).
- `--skip-fb` solo si el usuario pide explícitamente no tocar Facebook.

### 6. Reporte final
Devolver al usuario: link e ID del post de IG, link e ID del post de FB,
cómo se resolvió FB (`auto-crosspost` = lo compartió Meta solo;
`repost-api` = lo publicó el script) y cualquier aviso. El detalle de cada
paso queda en `logs/publicaciones.log`.

## Manejo de errores (mensajes claros, mirar el log)
- **Token vencido / permisos**: correr `python3 scripts/ig_publish.py --check`
  y `python3 scripts/publish.py --check`; si fallan, regenerar tokens (app
  "Estacionline Poster", scopes `pages_manage_posts`, `instagram_basic`,
  `instagram_content_publish`, etc.).
- **Imagen rechazada por IG**: verificar URL pública accesible, JPG/PNG,
  aspecto 4:5 a 1.91:1, < 8MB.
- **Container en ERROR / timeout**: reintentar una vez; si persiste, revisar
  formato de la imagen.
- **Post de FB que "no está disponible"**: diagnóstico con
  `python3 scripts/publish.py --post-status POST_ID` y
  `python3 scripts/publish.py --list-feed`. Si FB lo eliminó por duplicado,
  NO reintentar (probablemente el crosspost automático ya existe).
- Cada paso loguea en `logs/publicaciones.log` con timestamp — usarlo para
  saber exactamente dónde falló.

## Setup (una sola vez)
- `instagram.json`: `{username, ig_user_id, page_id, access_token}` (token
  de Página con scopes de IG).
- `.credentials.json`: `{page_id, access_token}` de la página de Facebook.
- `wordpress.json` (opcional, para subir slides locales):
  `{base_url, username, app_password}` — ver `wordpress.example.json`.
- Alternativa por env vars: `FB_PAGE_ID`, `FB_PAGE_ACCESS_TOKEN`.
- **Nunca hardcodear tokens en el código ni commitearlos** (están en
  `.gitignore`). Verificar: `ig_publish.py --check` y `publish.py --check`.

## Herramientas sueltas (para casos puntuales, no para el flujo normal)
- `scripts/ig_publish.py` — publicar en IG directo (foto/carrusel), `--dry-run`.
- `scripts/ig_story.py` — historias (imagen 9:16 o video ≤60s).
- `scripts/fb_repost_ig.py` — repostear en FB un post que ya está en IG
  (`--latest`, `--permalink`). Antes de usarlo, chequear que el crosspost
  automático no esté ya en la página (evitar duplicados).
- `scripts/publish.py` — publicar solo en FB; diagnóstico `--post-status`,
  `--list-feed`.
- `scripts/wp_upload.py` — subir imágenes a WordPress y obtener URLs.
