# Layout References

All layouts assume these variables defined in the build script:

```python
PRIMARY = '#...'  # palette primary
LIGHT = '#...'
DARK = '#...'
BG_DARK = '#...'
GRADIENT = f'linear-gradient(165deg, {DARK} 0%, {PRIMARY} 50%, {LIGHT} 100%)'
```

And this base CSS prepended to every slide:

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; }
body { width: 1080px; height: 1350px; font-family: 'Inter', sans-serif; overflow: hidden; }
.slide { width: 1080px; height: 1350px; position: relative; overflow: hidden; background: {BG_DARK}; }
```

## Wordmark — arriba a la derecha, GRANDE

> El **zócalo inferior de 84px quedó deprecado en mayo de 2026**. Esta sección
> documentaba el zócalo y contradecía a SKILL.md: si viste esa versión, está
> mal. El wordmark va arriba a la derecha y lo genera `build_template.py`
> (constantes `WM` / `WM_PHOTO`) — no lo escribas a mano.

```html
<div class="wordmark"><span class="brand">Estacionline</span><span class="site">estacionline.com</span></div>
```

Sobre foto de fondo va la variante `on-photo`, que sólo agrega una sombra:

```html
<div class="wordmark on-photo">…</div>
```

```css
.wordmark { position: absolute; top: 50px; right: 60px; z-index: 10; text-align: right; }
.wordmark .brand { display: block; font-size: 52px; font-weight: 900; letter-spacing: -1.5px;
    line-height: 1.05;
    background: {GRADIENT}; -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; }
.wordmark .site { display: block; font-size: 20px; font-weight: 600; margin-top: 2px;
    color: rgba(255,255,255,0.7); }
/* drop-shadow funciona con texto en gradiente; text-shadow no. */
.wordmark.on-photo { filter: drop-shadow(0 2px 10px rgba(0,0,0,0.6)); }
```

- Las dos líneas son **"Estacionline" + "estacionline.com"**, no negociable.
- En slides **sin** foto, el cuerpo arranca con `padding-top: 220px` para no
  chocar con el wordmark.
- Refuerzo de sombra: **UNA sola**, y sólo si la mediana de luminancia de la
  zona (`crop 600,45,1020,140`) supera **110**. Dos sombras ensucian el halo.
- Al copiar un build de otra pieza, **borrar el override de `.wordmark.on-photo`**
  antes de renderizar: se arrastra solo.

---

## Layout 1: Cover with photo background + text bottom

For slide 1 (intro). Photo background, dark overlay bottom-weighted, text at bottom.

```css
.photo { position: absolute; inset: 0; width: 100%; height: 100%;
    object-fit: cover; object-position: center 30%; z-index: 1; }
.overlay { position: absolute; inset: 0; z-index: 2;
    background: linear-gradient(180deg,
        rgba(X,X,X,0.20) 0%,
        rgba(X,X,X,0.35) 40%,
        rgba(X,X,X,0.88) 65%,
        rgba(X,X,X,0.98) 85%,
        rgba(X,X,X,1) 100%); }
.cover-content { position: absolute; inset: 0; z-index: 3;
    display: flex; flex-direction: column; justify-content: flex-end;
    padding: 0 80px 180px 80px; }
.eyebrow { font-size: 26px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 5px; color: {LIGHT}; margin-bottom: 32px; }
.cover-title { font-size: 92px; font-weight: 900; line-height: 0.98;
    color: white; letter-spacing: -3px; margin-bottom: 32px; }
.cover-title .accent { background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
.cover-sub { font-size: 28px; font-weight: 500; color: rgba(255,255,255,0.92);
    line-height: 1.3; max-width: 850px; }
.swipe { position: absolute; bottom: 110px; right: 80px; z-index: 4;
    font-size: 20px; font-weight: 600; color: {LIGHT};
    text-transform: uppercase; letter-spacing: 3px; }
```

Replace `rgba(X,X,X,...)` with the BG_DARK rgb values.

---

## Layout 2: Quote (no photo)

Large pull-quote with attribution. Centered, no photo.

```css
.quote-bg { position: absolute; inset: 0; z-index: 1; background: {BG_DARK}; }
.quote-bg::before { content:''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 50% 50%, rgba(DARK_RGB,0.7) 0%, transparent 70%); }
.quote-wrap { position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 0 90px 84px 90px; }
.big-quote-mark { font-size: 200px; font-weight: 900; line-height: 0.7;
    background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 10px; }
.big-quote { font-size: 60px; font-weight: 700; line-height: 1.15;
    color: white; letter-spacing: -1.5px; margin-bottom: 50px; }
.big-quote .accent { color: {LIGHT}; }
.attrib { font-size: 22px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 3px; color: {PRIMARY}; }
.attrib-name { color: white; font-size: 28px; margin-top: 6px;
    text-transform: none; letter-spacing: 0; font-weight: 700; }
.attrib-role { color: rgba(255,255,255,0.7); font-size: 20px; margin-top: 4px;
    font-weight: 500; }
```

---

## Layout 3a: Photo + text (text at BOTTOM) — DEFAULT

Use when the subject's face is in the upper half of the photo. The text goes at the bottom, padding 160px to clear the wordmark.

```css
.photo { position: absolute; inset: 0; width: 100%; height: 100%;
    object-fit: cover; object-position: center 25%; z-index: 1; }
.overlay { position: absolute; inset: 0; z-index: 2;
    background: linear-gradient(180deg,
        rgba(X,X,X,0.20) 0%,
        rgba(X,X,X,0.30) 35%,
        rgba(X,X,X,0.85) 60%,
        rgba(X,X,X,0.98) 80%,
        rgba(X,X,X,1) 100%); }
.content { position: absolute; inset: 0; z-index: 3;
    display: flex; flex-direction: column; justify-content: flex-end;
    padding: 80px 80px 160px 80px; }
.eyebrow { font-size: 26px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 4px; color: {LIGHT}; margin-bottom: 24px; }
.title { font-size: 70px; font-weight: 800; line-height: 1.05;
    color: white; letter-spacing: -2px; margin-bottom: 32px; }
.title .accent { background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
.bajada { font-size: 28px; font-weight: 400; line-height: 1.4;
    color: rgba(255,255,255,0.92); }
```

## Layout 3b: Photo + text (text at TOP)

Use when the subject's face is in the lower half of the photo. Inverts the overlay gradient.

```css
.photo { position: absolute; inset: 0; width: 100%; height: 100%;
    object-fit: cover; object-position: center 30%; z-index: 1; }
.overlay { position: absolute; inset: 0; z-index: 2;
    background: linear-gradient(180deg,
        rgba(X,X,X,0.98) 0%,
        rgba(X,X,X,0.92) 22%,
        rgba(X,X,X,0.55) 55%,
        rgba(X,X,X,0.25) 100%); }
.content { position: absolute; inset: 0; z-index: 3;
    display: flex; flex-direction: column; justify-content: flex-start;
    padding: 110px 80px 160px 80px; }
/* eyebrow, title, bajada same as 3a */
```

## Layout 3c: Photo entera (contain) + text below — FALLBACK

When the user complains that subjects are cut and refuses zoom-out via object-fit cover, fall back to this: foto entera arriba con barras de fondo, texto debajo.

```css
.bg { position: absolute; inset: 0; z-index: 1; background: {BG_DARK}; }
.photo { position: absolute; top: 0; left: 0; right: 0;
    width: 100%; height: 760px;
    object-fit: contain; z-index: 2; background: {BG_DARK}; }
.content { position: absolute; top: 780px; left: 0; right: 0; bottom: 0; z-index: 3;
    display: flex; flex-direction: column; justify-content: flex-start;
    padding: 30px 80px 84px 80px; }
.eyebrow { font-size: 26px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 4px; color: {LIGHT}; margin-bottom: 22px; }
.title { font-size: 56px; font-weight: 800; line-height: 1.05;
    color: white; letter-spacing: -1.5px; margin-bottom: 24px; }
.bajada { font-size: 22px; font-weight: 400; line-height: 1.4;
    color: rgba(255,255,255,0.85); }
```

---

## Layout 4: Big number

The literal data point as huge type. Crucial: `line-height: 1.1` + `padding: 8px 0` to prevent vertical clipping of the gradient text.

```css
.num-bg { position: absolute; inset: 0; z-index: 1; background: {BG_DARK}; }
.num-bg::before { content:''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 30% 30%, rgba(PRIMARY_RGB,0.25) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 90%, rgba(DARK_RGB,0.5) 0%, transparent 55%); }
.num-wrap { position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 0 80px 84px 80px; }
.num-eyebrow { font-size: 26px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 4px; color: {LIGHT}; margin-bottom: 30px; }
.big-num { font-size: 380px; font-weight: 900;
    line-height: 1.1; padding: 8px 0;
    background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -10px; margin-bottom: 10px; }
.num-unit { font-size: 56px; font-weight: 700; color: white;
    margin-bottom: 40px; letter-spacing: -1px; }
.num-desc { font-size: 32px; font-weight: 500; line-height: 1.35;
    color: rgba(255,255,255,0.9); max-width: 880px; }
```

For long numbers (5+ digits): reduce `.big-num` font-size to 68-78px.

---

## Layout 5a: List (numbered, 3 items)

```css
.item { display: flex; gap: 28px; margin-bottom: 40px; align-items: flex-start; }
.num { flex-shrink: 0;
    font-size: 32px; font-weight: 800;
    background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    padding-top: 8px; min-width: 50px; }
.item-body h3 { font-size: 38px; font-weight: 700; color: white;
    line-height: 1.15; margin-bottom: 8px; letter-spacing: -1px; }
.item-body p { font-size: 24px; font-weight: 400; color: rgba(255,255,255,0.78);
    line-height: 1.4; }
```

## Layout 5b: Table rows (locality + count)

For breakdowns by location, count, etc.

```css
.row { display: flex; justify-content: space-between; align-items: baseline;
    padding: 22px 0; border-bottom: 1px solid rgba(255,255,255,0.12); }
.loc { font-size: 30px; font-weight: 700; color: white; letter-spacing: -0.5px; }
.amt { font-size: 38px; font-weight: 900;
    background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
```

---

## Layout 6: Closing slide with CTA

Final slide. Big title + quote + CTA button.

```css
.close-quote { position: relative; padding-left: 32px;
    font-size: 30px; font-weight: 500; line-height: 1.4;
    color: rgba(255,255,255,0.92); font-style: italic;
    margin-bottom: 50px; max-width: 880px; }
.close-quote::before { content:''; position: absolute; left: 0; top: 4px; bottom: 4px;
    width: 6px; background: {GRADIENT}; border-radius: 4px; }
.cta { display: inline-block; align-self: flex-start;
    padding: 22px 44px; background: {GRADIENT};
    color: white; font-size: 24px; font-weight: 800;
    border-radius: 100px; letter-spacing: -0.5px; }
```

CTA text examples: "Leé la nota completa →", "Más en estacionline.com →"

---

## Object-position cheat sheet

When user asks to "move the photo":
- "más a la izquierda" → lower the first percentage (e.g., 50% → 35% → 25%)
- "más a la derecha" → raise the first percentage (e.g., 50% → 65% → 75%)
- "no le tapes la cara" → identify where the face is in the source photo, adjust accordingly
- "más arriba" (show more of the top) → lower second value (50% → 30% → 15%)
- "más abajo" → raise second value
