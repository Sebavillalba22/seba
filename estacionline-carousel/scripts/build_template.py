"""
build_template.py — Template for generating a 7-slide Estacionline carousel.

THIS FILE IS THE SINGLE SOURCE OF TRUTH FOR THE DESIGN.
Copy it, fill in ONLY the variables in the CONFIG section, and run it.
NEVER rewrite the CSS in the slide builders — every design rule
(wordmark, paddings, font sizes, gradients) is already encoded here.
references/layouts.md documents WHEN to use each layout; the CSS lives here.

Workflow:
    1. Copy this file into your working dir
    2. Fill the CONFIG section (palette name + content variables)
    3. python build_template.py          -> writes slide1.html ... slide7.html
    4. python scripts/render.py <dir>    -> renders slide1.png ... slide7.png
"""
from pathlib import Path

# =============================================================================
# CONFIG — this is the ONLY section you should edit
# =============================================================================

WORK_DIR = '/home/claude/my_carrusel'   # directory where HTMLs will be saved

# Palette — pick ONE: violaceo | verde | rosa | acero | atardecer | ocre
PALETA = 'violaceo'

# Paths to b64-encoded photos (output of process_photos.py)
FOTO_COVER = Path(f'{WORK_DIR}/cover_b64.txt').read_text().strip()
FOTO_SLIDE3 = Path(f'{WORK_DIR}/slide3_b64.txt').read_text().strip()
FOTO_SLIDE5 = Path(f'{WORK_DIR}/slide5_b64.txt').read_text().strip()
# Add more as needed

# Content for each slide
EYEBROW_COVER = "Sección de la nota"        # e.g. "Historias de vida"
COVER_TITLE = 'Título principal,<br><span class="accent">en dos líneas</span>.'
COVER_SUB = "Subtítulo que resume la nota en una oración."

QUOTE_TEXT = '"Cita textual del protagonista <span class="accent">con énfasis</span>."'
QUOTE_NAME = "Nombre Apellido"
QUOTE_ROLE = "Cargo o descripción"

SLIDE3_EYEBROW = "El comienzo"
SLIDE3_TITLE = 'Título <span class="accent">corto</span> y potente.'
SLIDE3_BAJADA = "Bajada que da contexto sobre lo que muestra la foto."
SLIDE3_OBJ_POS = "center 25%"   # adjust to show subject's face

BIG_NUMBER = "53"
BIG_NUMBER_SIZE = 380   # px. Literal number, 1-4 digits: 380. 5+ chars or
                        # symbols (%, −, +): reduce to 200-260 so it fits.
NUMBER_EYEBROW = "Los números"
NUMBER_UNIT = "unidades"          # e.g. "años", "títulos", "millones"
NUMBER_DESC = "Descripción del número con contexto."

SLIDE5_EYEBROW = "El detalle"
SLIDE5_TITLE = 'Otro título <span class="accent">destacado</span>.'
SLIDE5_BAJADA = "Bajada de la segunda foto."
SLIDE5_OBJ_POS = "center 25%"

LIST_EYEBROW = "Distribución"
LIST_TITLE = 'Lista <span class="accent">por categoría</span>.'
LIST_ITEMS = [
    ("01", "Primer ítem", "Descripción del primer ítem."),
    ("02", "Segundo ítem", "Descripción del segundo ítem."),
    ("03", "Tercer ítem", "Descripción del tercer ítem."),
]

CLOSE_EYEBROW = "El compromiso"
CLOSE_TITLE = 'Cita o frase <span class="accent">final</span>.'
CLOSE_QUOTE = "Cita que cierra la historia."
CTA_TEXT = "Leé la nota completa →"

# =============================================================================
# PALETTES — values match SKILL.md exactly. Do not edit per-carousel.
# =============================================================================

PALETTES = {
    # Violáceo — default
    'violaceo':  dict(PRIMARY='#A855F7', LIGHT='#D8B4FE', DARK='#4C1D95', BG_DARK='#0F0817'),
    # Verde (lima) — Funes / Roldán
    'verde':     dict(PRIMARY='#A3C616', LIGHT='#CEEC55', DARK='#445309', BG_DARK='#0F1008'),
    # Rosa — mujer / género / salud
    'rosa':      dict(PRIMARY='#EC4899', LIGHT='#F9A8D4', DARK='#831843', BG_DARK='#1A0814'),
    # Acero — Muni Rosario / Converge / institucional
    'acero':     dict(PRIMARY='#5B8FB9', LIGHT='#B6CEDC', DARK='#1E3A5F', BG_DARK='#0A1220'),
    # Atardecer — provincia / economía / crisis (gradiente especial de 5 stops)
    'atardecer': dict(PRIMARY='#F97316', LIGHT='#FBBF24', DARK='#7C2D6F', BG_DARK='#1A0510'),
    # Amarillo ocre — random / gaming / premium
    'ocre':      dict(PRIMARY='#D4A53A', LIGHT='#E8C474', DARK='#5C3D0F', BG_DARK='#14100A'),
}


def _rgb(hex_color: str) -> str:
    h = hex_color.lstrip('#')
    return f'{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)}'


_p = PALETTES[PALETA]
PRIMARY, LIGHT, DARK, BG_DARK = _p['PRIMARY'], _p['LIGHT'], _p['DARK'], _p['BG_DARK']
BG_RGB, PRIMARY_RGB, DARK_RGB = _rgb(BG_DARK), _rgb(PRIMARY), _rgb(DARK)

if PALETA == 'atardecer':
    # Única paleta con gradiente multicolor de 5 stops — parte del concepto.
    GRADIENT = ('linear-gradient(135deg, '
                '#FBBF24 0%, #F97316 30%, #EF4444 55%, #EC4899 75%, #A855F7 100%)')
else:
    GRADIENT = f'linear-gradient(165deg, {DARK} 0%, {PRIMARY} 50%, {LIGHT} 100%)'

# =============================================================================
# BASE TEMPLATES — the design system. DO NOT EDIT per-carousel.
# =============================================================================

BASE_CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ width: 1080px; height: 1350px; font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif; overflow: hidden; }}
.slide {{ width: 1080px; height: 1350px; position: relative; overflow: hidden; background: {BG_DARK}; }}
/* Wordmark: arriba a la derecha, GRANDE (estándar desde mayo 2026).
   El zócalo inferior de 84px está DEPRECADO — no volver a usarlo. */
.wordmark {{ position: absolute; top: 50px; right: 60px; z-index: 10; text-align: right; }}
.wordmark .brand {{ display: block; font-size: 52px; font-weight: 900; letter-spacing: -1.5px;
    line-height: 1.05;
    background: {GRADIENT}; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
.wordmark .site {{ display: block; font-size: 20px; font-weight: 600; margin-top: 2px;
    color: rgba(255,255,255,0.7); }}
/* Variante para slides con foto de fondo: sombra suave para legibilidad.
   (drop-shadow funciona con texto en gradiente; text-shadow no.) */
.wordmark.on-photo {{ filter: drop-shadow(0 2px 10px rgba(0,0,0,0.6)); }}
"""

WM = """<div class="wordmark"><span class="brand">Estacionline</span><span class="site">estacionline.com</span></div>"""
WM_PHOTO = """<div class="wordmark on-photo"><span class="brand">Estacionline</span><span class="site">estacionline.com</span></div>"""


def photo_overlay_bottom():
    return f"""linear-gradient(180deg,
        rgba({BG_RGB},0.20) 0%,
        rgba({BG_RGB},0.30) 35%,
        rgba({BG_RGB},0.85) 60%,
        rgba({BG_RGB},0.98) 80%,
        rgba({BG_RGB},1) 100%)"""

# =============================================================================
# SLIDE BUILDERS
# =============================================================================

SLIDE1 = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
{BASE_CSS}
.photo {{ position: absolute; inset: 0; width: 100%; height: 100%;
    object-fit: cover; object-position: center 30%; z-index: 1; }}
.overlay {{ position: absolute; inset: 0; z-index: 2; background: {photo_overlay_bottom()}; }}
.cover-content {{ position: absolute; inset: 0; z-index: 3;
    display: flex; flex-direction: column; justify-content: flex-end;
    padding: 0 80px 140px 80px; }}
.eyebrow {{ font-size: 26px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 5px; color: {LIGHT}; margin-bottom: 32px; }}
.cover-title {{ font-size: 92px; font-weight: 900; line-height: 0.98;
    color: white; letter-spacing: -3px; margin-bottom: 32px; }}
.cover-title .accent {{ background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
.cover-sub {{ font-size: 28px; font-weight: 500; color: rgba(255,255,255,0.92);
    line-height: 1.3; max-width: 850px; }}
.swipe {{ position: absolute; bottom: 70px; right: 80px; z-index: 4;
    font-size: 20px; font-weight: 600; color: {LIGHT};
    text-transform: uppercase; letter-spacing: 3px; }}
</style></head><body>
<div class="slide">
  <img class="photo" src="data:image/jpeg;base64,{FOTO_COVER}">
  <div class="overlay"></div>
  <div class="cover-content">
    <div class="eyebrow">{EYEBROW_COVER}</div>
    <h1 class="cover-title">{COVER_TITLE}</h1>
    <p class="cover-sub">{COVER_SUB}</p>
  </div>
  <div class="swipe">Deslizá →</div>
  {WM_PHOTO}
</div></body></html>"""

SLIDE2 = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
{BASE_CSS}
.quote-bg {{ position: absolute; inset: 0; z-index: 1; background: {BG_DARK}; }}
.quote-bg::before {{ content:''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 50% 50%, rgba({DARK_RGB},0.7) 0%, transparent 70%); }}
/* Sin foto: el cuerpo arranca a 220px para no chocar con el wordmark. */
.quote-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 90px 100px 90px; }}
.big-quote-mark {{ font-size: 200px; font-weight: 900; line-height: 0.7;
    background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 10px; }}
.big-quote {{ font-size: 60px; font-weight: 700; line-height: 1.15;
    color: white; letter-spacing: -1.5px; margin-bottom: 50px; }}
.big-quote .accent {{ color: {LIGHT}; }}
.attrib {{ font-size: 22px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 3px; color: {PRIMARY}; }}
.attrib-name {{ color: white; font-size: 28px; margin-top: 6px;
    text-transform: none; letter-spacing: 0; font-weight: 700; }}
.attrib-role {{ color: rgba(255,255,255,0.7); font-size: 20px; margin-top: 4px;
    font-weight: 500; }}
</style></head><body>
<div class="slide">
  <div class="quote-bg"></div>
  <div class="quote-wrap">
    <div class="big-quote-mark">"</div>
    <p class="big-quote">{QUOTE_TEXT}</p>
    <div class="attrib">— Sus palabras</div>
    <div class="attrib-name">{QUOTE_NAME}</div>
    <div class="attrib-role">{QUOTE_ROLE}</div>
  </div>
  {WM}
</div></body></html>"""

def photo_text_bottom_slide(foto_b64, obj_pos, eyebrow, title, bajada):
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
{BASE_CSS}
.photo {{ position: absolute; inset: 0; width: 100%; height: 100%;
    object-fit: cover; object-position: {obj_pos}; z-index: 1; }}
.overlay {{ position: absolute; inset: 0; z-index: 2; background: {photo_overlay_bottom()}; }}
.content {{ position: absolute; inset: 0; z-index: 3;
    display: flex; flex-direction: column; justify-content: flex-end;
    padding: 80px 80px 110px 80px; }}
.eyebrow {{ font-size: 26px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 4px; color: {LIGHT}; margin-bottom: 24px; }}
.title {{ font-size: 70px; font-weight: 800; line-height: 1.05;
    color: white; letter-spacing: -2px; margin-bottom: 32px; }}
.title .accent {{ background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
.bajada {{ font-size: 28px; font-weight: 400; line-height: 1.4;
    color: rgba(255,255,255,0.92); }}
</style></head><body>
<div class="slide">
  <img class="photo" src="data:image/jpeg;base64,{foto_b64}">
  <div class="overlay"></div>
  <div class="content">
    <div class="eyebrow">{eyebrow}</div>
    <h1 class="title">{title}</h1>
    <p class="bajada">{bajada}</p>
  </div>
  {WM_PHOTO}
</div></body></html>"""

SLIDE3 = photo_text_bottom_slide(FOTO_SLIDE3, SLIDE3_OBJ_POS, SLIDE3_EYEBROW, SLIDE3_TITLE, SLIDE3_BAJADA)

SLIDE4 = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
{BASE_CSS}
.num-bg {{ position: absolute; inset: 0; z-index: 1; background: {BG_DARK}; }}
.num-bg::before {{ content:''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 30% 30%, rgba({PRIMARY_RGB},0.25) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 90%, rgba({DARK_RGB},0.5) 0%, transparent 55%); }}
.num-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 80px 100px 80px; }}
.num-eyebrow {{ font-size: 26px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 4px; color: {LIGHT}; margin-bottom: 30px; }}
/* line-height 1.1 + padding vertical: previenen el clipping del gradiente.
   min-width 440px: evita corte horizontal con símbolos (%, −, +). */
.big-num {{ font-size: {BIG_NUMBER_SIZE}px; font-weight: 900;
    line-height: 1.1; padding: 8px 0; min-width: 440px;
    background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -10px; margin-bottom: 10px; }}
.num-unit {{ font-size: 56px; font-weight: 700; color: white;
    margin-bottom: 40px; letter-spacing: -1px; }}
.num-desc {{ font-size: 32px; font-weight: 500; line-height: 1.35;
    color: rgba(255,255,255,0.9); max-width: 880px; }}
</style></head><body>
<div class="slide">
  <div class="num-bg"></div>
  <div class="num-wrap">
    <div class="num-eyebrow">{NUMBER_EYEBROW}</div>
    <div class="big-num">{BIG_NUMBER}</div>
    <div class="num-unit">{NUMBER_UNIT}</div>
    <p class="num-desc">{NUMBER_DESC}</p>
  </div>
  {WM}
</div></body></html>"""

SLIDE5 = photo_text_bottom_slide(FOTO_SLIDE5, SLIDE5_OBJ_POS, SLIDE5_EYEBROW, SLIDE5_TITLE, SLIDE5_BAJADA)

list_items_html = "\n".join([
    f'''<div class="item">
      <div class="num">{n}</div>
      <div class="item-body"><h3>{t}</h3><p>{d}</p></div>
    </div>'''
    for n, t, d in LIST_ITEMS
])

SLIDE6 = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
{BASE_CSS}
.list-bg {{ position: absolute; inset: 0; z-index: 1; background: {BG_DARK}; }}
.list-bg::before {{ content:''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 100% 0%, rgba({PRIMARY_RGB},0.2) 0%, transparent 55%),
                radial-gradient(ellipse at 0% 100%, rgba({DARK_RGB},0.5) 0%, transparent 55%); }}
.list-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 80px 100px 80px; }}
.list-eyebrow {{ font-size: 26px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 4px; color: {LIGHT}; margin-bottom: 24px; }}
.list-title {{ font-size: 64px; font-weight: 800; line-height: 1.05;
    color: white; letter-spacing: -2px; margin-bottom: 60px; }}
.list-title .accent {{ background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
.item {{ display: flex; gap: 28px; margin-bottom: 40px; align-items: flex-start; }}
.num {{ flex-shrink: 0;
    font-size: 32px; font-weight: 800;
    background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    padding-top: 8px; min-width: 50px; }}
.item-body h3 {{ font-size: 38px; font-weight: 700; color: white;
    line-height: 1.15; margin-bottom: 8px; letter-spacing: -1px; }}
.item-body p {{ font-size: 24px; font-weight: 400; color: rgba(255,255,255,0.78);
    line-height: 1.4; }}
</style></head><body>
<div class="slide">
  <div class="list-bg"></div>
  <div class="list-wrap">
    <div class="list-eyebrow">{LIST_EYEBROW}</div>
    <h1 class="list-title">{LIST_TITLE}</h1>
    {list_items_html}
  </div>
  {WM}
</div></body></html>"""

SLIDE7 = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
{BASE_CSS}
.close-bg {{ position: absolute; inset: 0; z-index: 1; background: {BG_DARK}; }}
.close-bg::before {{ content:''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 50% 30%, rgba({PRIMARY_RGB},0.3) 0%, transparent 60%),
                radial-gradient(ellipse at 50% 100%, rgba({DARK_RGB},0.7) 0%, transparent 60%); }}
.close-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 80px 100px 80px; }}
.close-eyebrow {{ font-size: 26px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 5px; color: {LIGHT}; margin-bottom: 36px; }}
.close-title {{ font-size: 84px; font-weight: 900; line-height: 1.0;
    color: white; letter-spacing: -3px; margin-bottom: 50px; }}
.close-title .accent {{ background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
.close-quote {{ position: relative; padding-left: 32px;
    font-size: 28px; font-weight: 500; line-height: 1.4;
    color: rgba(255,255,255,0.92); font-style: italic;
    margin-bottom: 50px; max-width: 880px; }}
.close-quote::before {{ content:''; position: absolute; left: 0; top: 4px; bottom: 4px;
    width: 6px; background: {GRADIENT}; border-radius: 4px; }}
.cta {{ display: inline-block; align-self: flex-start;
    padding: 22px 44px; background: {GRADIENT};
    color: white; font-size: 24px; font-weight: 800;
    border-radius: 100px; letter-spacing: -0.5px; }}
</style></head><body>
<div class="slide">
  <div class="close-bg"></div>
  <div class="close-wrap">
    <div class="close-eyebrow">{CLOSE_EYEBROW}</div>
    <h1 class="close-title">{CLOSE_TITLE}</h1>
    <p class="close-quote">{CLOSE_QUOTE}</p>
    <div class="cta">{CTA_TEXT}</div>
  </div>
  {WM}
</div></body></html>"""

# =============================================================================
# WRITE FILES
# =============================================================================
if __name__ == '__main__':
    out = Path(WORK_DIR)
    out.mkdir(parents=True, exist_ok=True)
    slides = [SLIDE1, SLIDE2, SLIDE3, SLIDE4, SLIDE5, SLIDE6, SLIDE7]
    for i, html in enumerate(slides, 1):
        (out / f'slide{i}.html').write_text(html)
    print(f'{len(slides)} slides written to {WORK_DIR} (paleta: {PALETA})')
    print(f'Next: python scripts/render.py {WORK_DIR}')
