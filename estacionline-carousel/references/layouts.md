# Layout References

> **⚠️ FUENTE DE VERDAD**: la implementación canónica del CSS vive en
> `scripts/carousel.py`. Este archivo documenta **cuándo** usar cada layout
> y qué controla cada pieza. Si este documento y `carousel.py` alguna vez
> difieren, **gana `carousel.py`**. No escribas CSS de slides desde cero:
> componé las funciones `slide_*` de la librería.
>
> Mapa layout → función: Layout 1 → `slide_cover` · Layout 2 → `slide_quote`
> · Layout 3a/3b → `slide_photo_text` (text_pos `'bottom'`/`'top'`) ·
> Layout 3c → `slide_photo_contain` · Layout 4 → `slide_number` ·
> Layout 5a → `slide_list` (`'numbered'` o `'check'`) · Layout 5b →
> `slide_table` · Layout 6 → `slide_close` · Layout 7 → `slide_text`.

## Estética vigente (calibrada contra placas aprobadas, julio 2026)

- **Gradiente de marca**: claro arriba → color pleno abajo:
  `linear-gradient(180deg, {LIGHT} 0%, {PRIMARY} 100%)`.
  Excepción: paleta "atardecer" usa su gradiente multicolor de 5 stops.
- **Títulos**: 64px, peso 800, line-height 1.12, letter-spacing -1.5px,
  blancos con `<span class="accent">` en gradiente para la parte destacada.
- **Cuerpo**: 34px, peso 400, line-height 1.45, rgba(255,255,255,0.92),
  con `<b>` para resaltar nombres/datos (queda blanco puro, peso 700).
- **Comillas tipográficas** " " en todos los textos, nunca rectas.
- **Citas**: barra lateral de 6px con gradiente + texto 40-46px peso 600
  (NO italic, NO comillón gigante). Atribución en una línea:
  **Nombre** `· rol` (rol en rgba blanco 0.6).
- **CTA**: pill con gradiente claro (`135deg, LIGHT → PRIMARY`) y **texto
  oscuro** ({BG_DARK}), 26px peso 800.
- **"Deslizá →"**: abajo a la derecha en TODAS las slides menos la final
  (20px, 600, uppercase, color LIGHT, ls 3px). Las funciones lo ponen solas
  (`swipe=True` default; `slide_close` no lo lleva).
- **Crédito de foto**: `credit='Foto: @handle'` abajo a la izquierda
  (22px, 600, rgba blanco 0.5). Va en las slides con foto y puede repetirse
  en la final.
- **Fondo sin foto**: BG_DARK con glow radial sutil de la paleta (lo pone
  `_bg_glow()` — automático en todas las slides sin foto).

## Wordmark — arriba a la derecha, GRANDE (estándar desde mayo 2026)

Presente en **todas** las slides; lo inserta `_doc()` automáticamente.
Reemplaza al viejo zócalo inferior de 84px, que está **DEPRECADO**.

```css
.wordmark { position: absolute; top: 50px; right: 60px; z-index: 10; text-align: right;
    filter: drop-shadow(0 2px 8px rgba(0,0,0,0.45)); }
.wordmark .brand { display: block; font-size: 52px; font-weight: 900; letter-spacing: -1.5px;
    background: {GRADIENT}; -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; }
.wordmark .site { display: block; font-size: 20px; font-weight: 600; margin-top: 2px;
    color: rgba(255,255,255,0.7); }
```

Reglas derivadas:

- El gradiente del brand **siempre** usa la paleta del carousel.
- **Slides sin foto**: el contenido arranca a 220-230px de arriba para no
  chocar con el wordmark (las funciones ya lo hacen).
- **Slides con foto**: variante `on-photo` con drop-shadow más fuerte.

---

## Layout 1: Cover — `slide_cover(foto, eyebrow, title, sub, obj_pos, credit)`

Slide 1 (intro). Foto de fondo que funde al navy de la paleta hacia abajo,
texto abajo: eyebrow + título 64px (3 líneas máx) + bajada 30px. Crédito de
foto abajo-izquierda, Deslizá abajo-derecha.

- `obj_pos`: `'center 30%'` default; ajustar para encuadrar la cara.
- El título lleva la parte clave (nombre de la canción, la cifra, el quién)
  en `<span class="accent">`.

## Layout 2: Cita — `slide_quote(text, name, role, eyebrow=None)`

Cita textual protagonista, sin foto. Barra lateral gradiente + cita 46px
peso 600 blanca + atribución **Nombre** · rol. Para la cita-hero del
carousel (slide 2 típica).

## Layout 3a/3b: Foto + texto — `slide_photo_text(..., text_pos='bottom'|'top')`

Foto de fondo con overlay + eyebrow/título/bajada. `'bottom'` (default)
cuando la cara está en la mitad superior de la foto; `'top'` cuando está
en la mitad inferior (invierte el overlay; el texto arranca a 230px para
despejar el wordmark).

## Layout 3c: Foto entera — `slide_photo_contain(foto, eyebrow, title, bajada)`

Fallback cuando el usuario no acepta el recorte de una foto horizontal:
foto completa arriba (object-fit contain, 760px), texto debajo.

## Layout 4: Dato gigante — `slide_number(eyebrow, number, desc, unit=None)`

El dato LITERAL de la nota como tipografía gigante en gradiente. Sirve
para números ("53") y para palabras-concepto ("Épica"). `desc` admite
`<b>`; `unit` ("años", "familias") es opcional.

Tamaño automático según largo: ≤4 caracteres → 300px · 5-6 → 220px ·
7+ → 160px. `size=` explícito solo para ajustes finos. El bloque lleva
`min-width: 440px` y `line-height 1.08 + padding 8px 0` (anti-clipping).
Si no entra, reformular el dato ("1,25 millones") antes que bajar de 140px.

## Layout 5a: Lista — `slide_list(eyebrow, title, items, style)`

`style='numbered'` numera 01/02/03; `style='check'` usa tildes ✓ (para
requisitos, "qué incluye", checklists). items = `[(titulo, desc), ...]`;
la descripción puede ser `''` para listas de una sola línea. 2-5 ítems.

## Layout 5b: Tabla — `slide_table(eyebrow, title, rows)`

Desgloses localidad/cantidad. rows = `[(loc, amt), ...]`. El monto va en
gradiente, 38px peso 900.

## Layout 6: Cierre — `slide_close(quote, name, role, cta, eyebrow=None, title=None, credit=None)`

Última slide: cita con barra (40px) + atribución + **CTA claro con texto
oscuro**. `eyebrow`/`title` opcionales para cierres con frase editorial
propia. No lleva Deslizá. CTA ejemplos: "Leé la entrevista completa →",
"Más en estacionline.com →".

## Layout 7: Texto — `slide_text(eyebrow, title, body, quote=None)`

Desarrollo del tema sin foto: eyebrow + título 64px + cuerpo 34px (con
`<b>` en nombres/datos) + cita italic opcional en color LIGHT. Es el
layout para "cómo nació", "el contexto", "qué dijo sobre X".

---

## Object-position cheat sheet

When user asks to "move the photo":
- "más a la izquierda" → lower the first percentage (e.g., 50% → 35% → 25%)
- "más a la derecha" → raise the first percentage (e.g., 50% → 65% → 75%)
- "no le tapes la cara" → identify where the face is in the source photo, adjust accordingly
- "más arriba" (show more of the top) → lower second value (50% → 30% → 15%)
- "más abajo" → raise second value
