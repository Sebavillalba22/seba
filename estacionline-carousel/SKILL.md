---
name: estacionline-carousel
description: Generate Instagram carousels (1080x1350px) for Estacionline news outlet using Python + HTML + Playwright. Use when the user provides a news article, photos, or asks for a "carrusel", "carousel", "slides para Instagram", or wants to turn a news story into an Instagram post for @estacionline. Triggers include any mention of carrusel, slides, instagram post about news, or providing a news article URL/text with photos to convert into a visual story.
---

# Estacionline Instagram Carousel Skill

Generate professional Instagram carousels (1080×1350px, 4:5 ratio) for @estacionline news outlet. This skill encodes hard-won design rules from dozens of carousel productions.

## 🔒 REGLA DE ORO — el diseño no se reescribe

**`scripts/build_template.py` es la única fuente de verdad del diseño.**
Para generar un carousel: copiá ese archivo, completá SOLO la sección CONFIG
(paleta + variables de contenido) y ejecutalo. **NUNCA escribas el CSS de una
slide desde cero, "de memoria", ni lo modifiques** salvo que el usuario pida
explícitamente un cambio de diseño puntual — y en ese caso, tocá solo la
propiedad pedida y nada más. Ajustes permitidos sin preguntar: variables de
CONFIG (`SLIDE3_OBJ_POS`, `BIG_NUMBER_SIZE`, textos, paleta) y agregar/quitar
slides duplicando los builders existentes. Todo lo demás (wordmark, paddings,
tamaños tipográficos, gradientes, overlays) ya está resuelto en el template
y se copia tal cual. `references/layouts.md` explica cuándo usar cada layout;
si difiere del template, gana el template.

## When to use

The user provides news content (text + photos, or URL) and wants to produce an Instagram carousel. They will typically ask:
- "Armemos un carrusel sobre [tema]"
- "Slides para Instagram sobre [nota]"
- "¿Vamos al copy?" (means they want the Instagram caption)

## Workflow

### 1. Capture inputs (ALWAYS ask before generating)

Before generating, ask the user for these three things using the `ask_user_input_v0` tool:

1. **Ángulo** (the editorial angle / protagonist)
2. **Paleta** — seis opciones:
   - Violáceo (purple)
   - Verde (green) — Funes / Roldán
   - Rosa (pink) — mujer / género / salud
   - Acero (azul metálico frío) — Muni Rosario / Converge / institucional
   - Atardecer (multicolor: amarillo→naranja→rojo→magenta→violeta) — provincia
   - Amarillo ocre (arena/dorado elegante) — random / gaming
3. **Cantidad de slides** — typically 5-10, default 7

If the article has a **specific numeric data point** that could anchor a slide (age, years, count, etc.), also ask which number to feature. Critical rule: this number must be **literal** from the source text, never an editorial metaphor.

### 2. Plan slides before generating

Propose a slide-by-slide plan and confirm with the user. Typical 7-slide structure:

1. **Cover** — Photo background + eyebrow + big title + subtitle
2. **Quote grande** — Pull-quote, no photo, with attribution
3. **Foto + texto** — Photo with text overlay (either top or bottom — see rules)
4. **Número grande** — Single literal data point, huge type
5. **Foto + texto** — Another photo slide
6. **Lista** — 3-item list (numbered) OR table-style rows (locality + count)
7. **Cierre** — Closing quote + CTA button

### 3. Process photos

Photos are typically uploaded to `/mnt/user-data/uploads/`. For each photo:
- Open with PIL, apply `ImageOps.exif_transpose()` to fix orientation
- Convert to RGB if needed
- Resize with `thumbnail((1600, 1600))` or `(1800, 1800)` for portraits
- Save as JPEG quality 88, optimize=True
- Encode as base64 and save to a `.txt` file in the working dir
- Embed in HTML as `<img src="data:image/jpeg;base64,...">` — NEVER use CSS background

### 4. Generate HTML + render with Playwright

- **Copiá `scripts/build_template.py` al working dir y completá SOLO la
  sección CONFIG** (ver Regla de Oro). Ese script escribe un HTML por slide
  con el CSS canónico ya resuelto.
- Render con `scripts/render.py <work_dir>`: viewport 1080x1350,
  device_scale_factor=2
- **Critical**: render.py ya espera imágenes **y fuentes** antes del
  screenshot. Si por algún motivo renderizás a mano, replicá ambas esperas:
  ```python
  await page.evaluate("""() => Promise.all(Array.from(document.images).map(img =>
      img.complete ? null : new Promise(r => { img.onload = img.onerror = r; })))""")
  await page.evaluate("() => document.fonts.ready")  # sin esto, sale la fuente fallback
  await page.wait_for_timeout(400)
  ```
- Screenshot at 2x, then thumbnail down to 1080×1350 with PIL.LANCZOS
- Save final PNG to `/mnt/user-data/outputs/[topic]_carrusel/slideN.png`

### 5. Present and iterate

- Use `present_files` to show all 7 slides
- User will give feedback like "corre la foto a la derecha", "no le tapes la cara", "ese título no me gusta"
- For positioning issues: adjust `object-position` of the photo (0% = far left, 100% = far right)
- For face-cropping in horizontal photos on vertical slides: there's a tradeoff between showing all subjects vs cropping faces. If user wants no cropping, use foto-arriba-contain layout (see references)

### 6. Copy

When user says "copy" or "¿vamos al copy?", generate the Instagram caption. See `references/copy.md`.

## Critical design rules (heredadas)

These rules are non-negotiable — they encode prior debugging. **Todas ya
están implementadas en `scripts/build_template.py`**; esta lista sirve para
verificar el resultado, no para reescribir CSS a mano:

- **1080×1350px exact** (Instagram 4:5 portrait)
- **Wordmark position: arriba a la derecha, GRANDE** (default desde mayo 2026, reemplaza al zócalo inferior). Especificaciones (clase `.wordmark` del template):
  - Posición: `top: 50px; right: 60px;` alineado a la derecha
  - "Estacionline" en 52px peso 900, con gradiente de la paleta
  - Línea secundaria "estacionline.com" en 20px peso 600, rgba(255,255,255,0.7)
  - **No usar más el zócalo inferior de 84px** para carousels nuevos. Si querés agregar bajada/crédito abajo, va como texto suelto, no como zócalo.
- Cuando el carousel cierra con CTA explícito (slide final), el wordmark sigue arriba pero la slide puede sumar un botón "Más en estacionline.com →" abajo
- **Brand mark gradient must always match the titular palette**
- Slides con foto de fondo: wordmark con sombra suave para legibilidad (clase `.wordmark.on-photo` — usa `filter: drop-shadow`, no `text-shadow`, que se ve mal con texto en gradiente)
- Para slides sin foto: el contenido del cuerpo arranca con padding-top 220px para no chocar con el wordmark
- Large numbers (slide 4 style): `line-height: 1.1` y `padding: 8px 0` para prevenir clipping vertical
- Números con símbolos (%, −, +) o muy largos: el bloque ya tiene `min-width: 440px`; ajustar `BIG_NUMBER_SIZE` en CONFIG (380 default, 200-260 para 5-6 caracteres, 160-180 para 7+)
- Step numbers en list slides: 32px
- **Photos embedded as base64**, nunca CSS background — confiabilidad de Playwright
- Siempre `await ImagePromiseAll` + `document.fonts.ready` antes del screenshot — sino se filtra el alt text o la fuente fallback

## Color palettes (memorize these)

Las seis paletas ya están cargadas en `build_template.py` con estos valores
exactos — se eligen con la variable `PALETA` en CONFIG (`violaceo`, `verde`,
`rosa`, `acero`, `atardecer`, `ocre`). No redefinir los hex a mano.

### Violáceo
```python
PRIMARY = '#A855F7'
LIGHT = '#D8B4FE'
DARK = '#4C1D95'
BG_DARK = '#0F0817'
```

### Verde (lima)
```python
PRIMARY = '#A3C616'
LIGHT = '#CEEC55'
DARK = '#445309'
BG_DARK = '#0F1008'
```

### Rosa
```python
PRIMARY = '#EC4899'
LIGHT = '#F9A8D4'
DARK = '#831843'
BG_DARK = '#1A0814'
```

### Amarillo ocre (arena / elegante)
```python
PRIMARY = '#D4A53A'   # amarillo ocre / dorado apagado
LIGHT = '#E8C474'     # arena clara (acento)
DARK = '#5C3D0F'      # marrón cálido oscuro (sombra)
BG_DARK = '#14100A'   # fondo casi negro con tinte cálido
```

Usar para notas "random" sin tema fuerte, ofertas premium, tecnología, gaming. Da un aire dorado/champagne más elegante que el atardecer.

### Acero (azul metálico frío)
```python
PRIMARY = '#5B8FB9'   # azul acero medio
LIGHT = '#B6CEDC'     # plateado azulado claro (acento)
DARK = '#1E3A5F'      # azul profundo (sombra)
BG_DARK = '#0A1220'   # fondo casi negro con tinte azul
```

Usar para Municipalidad de Rosario, podcast Converge, infraestructura, política urbana, institucional. Aire industrial elegante, frío y limpio.

### Atardecer (multi-stop)
```python
PRIMARY = '#F97316'   # naranja vibrante
LIGHT = '#FBBF24'     # amarillo dorado (acento claro)
DARK = '#7C2D6F'      # violeta-magenta oscuro
BG_DARK = '#1A0510'   # fondo casi negro con tinte vino
```

Esta paleta usa un gradiente especial con 5 stops en lugar del template estándar:
```python
GRADIENT = ('linear-gradient(135deg, '
            '#FBBF24 0%, '       # amarillo
            '#F97316 30%, '      # naranja
            '#EF4444 55%, '      # rojo
            '#EC4899 75%, '      # magenta
            '#A855F7 100%)')     # violeta
```

Usar para notas de economía, energía, calor, política con contenido caliente o de crisis. Es la única paleta que rompe el patrón de 3 stops del gradiente estándar — el efecto multicolor es parte del concepto.

Gradient template: `linear-gradient(165deg, {DARK} 0%, {PRIMARY} 50%, {LIGHT} 100%)`

## Layout references

See `references/layouts.md` for **when to use** each slide layout and what
each CSS piece controls. The canonical CSS implementation lives in
`scripts/build_template.py` — if the two ever disagree, the template wins.

## Common pitfalls

- **Don't paraphrase quotes** — use literal quotes from the source article in quote marks
- **Slide 4 number must be literal** — if "38 años" is the data point, find it in the text first
- **Photo orientation**: always `ImageOps.exif_transpose()` first or images come out rotated
- **Face cropping on horizontal photos**: warn user that vertical aspect ratio cuts subjects. Offer foto-arriba-contain layout as alternative
- **Wordmark must include "Estacionline" + "estacionline.com"** — non-negotiable
- **Don't invent facts**: if the article doesn't say it, don't put it in a slide

## Verificación de ejemplos y casos reales

Si el usuario pide ilustrar una nota con un caso concreto (ej: "agregame un ejemplo de mecenazgo, mencioná Okupas"), **siempre verificar antes con web_search** que el ejemplo:
1. Existe / es real
2. Se relaciona efectivamente con el tema de la nota
3. Las fechas/datos cronológicos cuadran

Caso histórico: el usuario pidió mencionar "Okupas" como ejemplo de Mecenazgo cultural. Verificación reveló que Okupas (2000) se produjo seis años antes de la Ley 2264 de Mecenazgo de CABA (2006). Era un dato falso. **Negarse a producir la pieza con datos incorrectos aunque el usuario insista**, incluso si dice "no lo voy a publicar". Ofrecer buscar un caso real verificado en su lugar.

Misma regla con imágenes: stills de series/películas, fotos promocionales de productos o personajes son **copyright vigente**. No usar en piezas para Estacionline aunque el usuario insista. Excepción: fotos oficiales de press kits con crédito visible ("Foto · [Fuente]") son uso editorial aceptable.

## Marcos transparentes para video

Para acompañar videos editados en Premiere/CapCut, generar PNG 1080×1350 con **hueco transparente en el centro** (omit_background=True en Playwright). Variantes estándar:

1. **Marco centrado** — hueco 980×806 (video 5:4 general)
2. **Marco vertical lateral** — hueco 500×1000 a la izquierda, texto a la derecha (clip portrait con copete)
3. **Marco horizontal finito** — hueco 960×410 banner cinematográfico ~21:9, texto arriba y abajo
4. **Marco cuadrado** — hueco 960×960 1:1 centrado

Reglas comunes:
- Borde del hueco: gradiente de 4px de la paleta + esquinas decorativas estilo "marcas de recorte"
- Wordmark grande arriba a la derecha (misma especificación que en carousels)
- Bloques sólidos `{BG_DARK}` arriba/abajo/laterales del hueco
- Generar también un preview JPG con un fondo de muestra colorido para que el usuario vea cómo va a quedar

