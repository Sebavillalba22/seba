"""
build_template.py — Template for generating a 7-slide Estacionline carousel.

THIS FILE IS THE SINGLE SOURCE OF TRUTH FOR THE DESIGN.
Copy it, fill in ONLY the variables in the CONFIG section, and run it.
NEVER rewrite the CSS in the slide builders — every design rule
(wordmark, paddings, font sizes, gradients) is already encoded here.
../referencias/layouts.md documents WHEN to use each layout; the CSS lives here.

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

WORK_DIR = '/home/claude/PIEZA'          # carpeta de trabajo de la pieza

# Paleta: violaceo | verde | rosa | acero | atardecer | ocre | rojo
# OBLIGATORIO elegirla por pieza. Queda en None a propósito: si copiás este
# build de otra pieza, el script ABORTA en vez de heredarle la paleta anterior.
# La manda el TEMA, no el feed. Tabla de decisión y desempate: ../SKILL.md
PALETA = None

FOTO_COVER = Path(f'{WORK_DIR}/cover_b64.txt').read_text().strip()
FOTO_FLYER = Path(f'{WORK_DIR}/flyer_b64.txt').read_text().strip()

# ---- 1 portada (SIEMPRE con foto, a sangre) --------------------------------
EYEBROW_COVER = "Volanta · Lugar"
COVER_TITLE_SIZE = 88                    # ajustar con verificar_renglones.py, máx 3 renglones
COVER_TITLE = ('Primer renglón<br>segundo renglón<br>'
               '<span class="accent">tercero con acento</span>.')
COVER_OBJ_POS = "center 50%"             # elegir con simular_encuadre.py
COVER_SUB = ("Bajada de portada, dos renglones, con el dato más accionable.")

# ---- 2 cita ----------------------------------------------------------------
Q2_TEXT = ('"Texto de la cita con <span class="accent">lo importante acentuado</span>"')
Q2_LABEL = "— La volanta de la cita"
Q2_NAME = "Nombre Apellido"
Q2_ROLE = "Cargo o referencia"

# ---- 3 número grande -------------------------------------------------------
BIG_NUMBER = "000"
BIG_NUMBER_SIZE = 340                    # 380 si son 1-2 dígitos; 250-300 con símbolos
NUMBER_EYEBROW = "Volanta"
NUMBER_UNIT = "de qué es ese número"
NUMBER_DESC = ("Contexto del número, siempre atribuido a la fuente.")

# ---- 4 foto o video enmarcado ----------------------------------------------
FRAME_EYEBROW = "Volanta"
FRAME_TITLE = 'Título de <span class="accent">dos a cinco palabras</span>.'
FRAME_BAJADA = ("Bajada de la foto enmarcada.")
FRAME_CREDIT = "Foto · Fuente"
FRAME_MAX_H = 500

# ---- 5 lista ---------------------------------------------------------------
LIST_EYEBROW = "Volanta"
LIST_TITLE = 'Título <span class="accent">corto</span>.'
LIST_ITEMS = [
    ("01", "Título del ítem", "Descripción breve del ítem."),
    ("02", "Título del ítem", "Descripción breve del ítem."),
    ("03", "Título del ítem", "Descripción breve del ítem."),
]

# ---- 6 filas de datos ------------------------------------------------------
ROWS_EYEBROW = "Volanta"
ROWS_TITLE = 'Título <span class="accent">corto</span>.'
ROWS_ITEMS = [
    ("Etiqueta", "Valor"),
    ("Etiqueta", "Valor"),
    ("Etiqueta", "Valor"),
    ("Etiqueta", "Valor"),
]

# ---- 7 placa de texto ------------------------------------------------------
P7_EYEBROW = "Volanta"
P7_TITLE = 'Título de la <span class="accent">placa de texto</span>.'
P7_SIZE = 58
P7_CUERPO = ("Párrafo de la placa de texto, hasta cinco o seis renglones.")

# ---- 8 cierre (NUNCA con pregunta) -----------------------------------------
CLOSE_EYEBROW = "Volanta"
CLOSE_TITLE = 'Cierre <span class="accent">afirmativo</span>.'
CLOSE_QUOTE = ("Párrafo de cierre con el dato que le queda al lector.")
CTA_TEXT = "Más en estacionline.com →"

# =============================================================================
# PALETTES — fuente de verdad de los colores. NO editar por carrusel.
# ../SKILL.md documenta CUÁNDO usar cada una; los hex viven acá.
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
    # Rojo — alertas / situacional / política caliente
    'rojo':      dict(PRIMARY='#EF4444', LIGHT='#FCA5A5', DARK='#7F1D1D', BG_DARK='#170707'),
}


def _rgb(hex_color: str) -> str:
    h = hex_color.lstrip('#')
    return f'{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)}'


if PALETA is None:
    raise SystemExit(
        "PALETA sin definir.\n"
        "Elegila por TEMA (no por la pieza anterior): "
        + " | ".join(PALETTES) + "\n"
        "Desempate: actor institucional > lugar > rubro. Ver ../SKILL.md")
if PALETA not in PALETTES:
    raise SystemExit(f"PALETA '{PALETA}' no existe. Opciones: " + " | ".join(PALETTES))

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
.swipe {{ position: absolute; bottom: 70px; right: 80px; z-index: 4;
    font-size: 20px; font-weight: 600; color: {LIGHT};
    text-transform: uppercase; letter-spacing: 3px; }}
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
    object-fit: cover; object-position: {COVER_OBJ_POS}; z-index: 1; }}
.overlay {{ position: absolute; inset: 0; z-index: 2; background: {photo_overlay_bottom()}; }}
.cover-content {{ position: absolute; inset: 0; z-index: 3;
    display: flex; flex-direction: column; justify-content: flex-end;
    padding: 0 80px 140px 80px; }}
.eyebrow {{ font-size: 28px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 5px; color: {LIGHT}; margin-bottom: 32px; }}
.cover-title {{ font-size: {COVER_TITLE_SIZE}px; font-weight: 900; line-height: 0.98;
    color: white; letter-spacing: -3px; margin-bottom: 32px; }}
.cover-title .accent {{ background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
.cover-sub {{ font-size: 32px; font-weight: 500; color: rgba(255,255,255,0.92);
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

def quote_slide(texto, label, nombre, rol):
        return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
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
    .attrib {{ font-size: 24px; font-weight: 600; text-transform: uppercase;
        letter-spacing: 3px; color: {PRIMARY}; }}
    .attrib-name {{ color: white; font-size: 32px; margin-top: 6px;
        text-transform: none; letter-spacing: 0; font-weight: 700; }}
    .attrib-role {{ color: rgba(255,255,255,0.7); font-size: 23px; margin-top: 4px;
        font-weight: 500; }}
    </style></head><body>
    <div class="slide">
      <div class="quote-bg"></div>
      <div class="quote-wrap">
        <div class="big-quote-mark">"</div>
        <p class="big-quote">{texto}</p>
        <div class="attrib">{label}</div>
        <div class="attrib-name">{nombre}</div>
        <div class="attrib-role">{rol}</div>
      </div>
      <div class="swipe">Deslizá →</div>
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
.eyebrow {{ font-size: 28px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 4px; color: {LIGHT}; margin-bottom: 24px; }}
.title {{ font-size: 70px; font-weight: 800; line-height: 1.05;
    color: white; letter-spacing: -2px; margin-bottom: 32px; }}
.title .accent {{ background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
.bajada {{ font-size: 34px; font-weight: 400; line-height: 1.4;
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
.num-unit {{ font-size: 58px; font-weight: 700; color: white;
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
  <div class="swipe">Deslizá →</div>
  {WM}
</div></body></html>"""


def list_slide(eyebrow, title, items):
    """Layout 5a — lista numerada. Mismo CSS del template, parametrizado."""
    list_items_html = "\n".join([
        f'''<div class="item">
      <div class="num">{n}</div>
      <div class="item-body"><h3>{t}</h3><p>{d}</p></div>
    </div>'''
        for n, t, d in items
    ])
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
{BASE_CSS}
.list-bg {{ position: absolute; inset: 0; z-index: 1; background: {BG_DARK}; }}
.list-bg::before {{ content:''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 100% 0%, rgba({PRIMARY_RGB},0.2) 0%, transparent 55%),
                radial-gradient(ellipse at 0% 100%, rgba({DARK_RGB},0.5) 0%, transparent 55%); }}
.list-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 80px 100px 80px; }}
.list-eyebrow {{ font-size: 28px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 4px; color: {LIGHT}; margin-bottom: 24px; }}
.list-title {{ font-size: 64px; font-weight: 800; line-height: 1.05;
    color: white; letter-spacing: -2px; margin-bottom: 60px; }}
.list-title .accent {{ background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
.item {{ display: flex; gap: 28px; margin-bottom: 40px; align-items: flex-start; }}
.num {{ flex-shrink: 0;
    font-size: 34px; font-weight: 800;
    background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    padding-top: 8px; min-width: 50px; }}
.item-body h3 {{ font-size: 42px; font-weight: 700; color: white;
    line-height: 1.15; margin-bottom: 8px; letter-spacing: -1px; }}
.item-body p {{ font-size: 30px; font-weight: 400; color: rgba(255,255,255,0.78);
    line-height: 1.4; }}
</style></head><body>
<div class="slide">
  <div class="list-bg"></div>
  <div class="list-wrap">
    <div class="list-eyebrow">{eyebrow}</div>
    <h1 class="list-title">{title}</h1>
    {list_items_html}
  </div>
  <div class="swipe">Deslizá →</div>
  {WM}
</div></body></html>"""


def rows_slide(eyebrow, title, rows):
    """Layout 5b — filas de datos. CSS de ../referencias/layouts.md."""
    rows_html = "\n".join([
        f'''<div class="row"><div class="loc">{a}</div><div class="amt">{b}</div></div>'''
        for a, b in rows
    ])
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
{BASE_CSS}
.list-bg {{ position: absolute; inset: 0; z-index: 1; background: {BG_DARK}; }}
.list-bg::before {{ content:''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 100% 0%, rgba({PRIMARY_RGB},0.2) 0%, transparent 55%),
                radial-gradient(ellipse at 0% 100%, rgba({DARK_RGB},0.5) 0%, transparent 55%); }}
.list-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 80px 100px 80px; }}
.list-eyebrow {{ font-size: 28px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 4px; color: {LIGHT}; margin-bottom: 24px; }}
.list-title {{ font-size: 64px; font-weight: 800; line-height: 1.05;
    color: white; letter-spacing: -2px; margin-bottom: 60px; }}
.list-title .accent {{ background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
.row {{ display: flex; justify-content: space-between; align-items: baseline;
    gap: 40px; padding: 22px 0; border-bottom: 1px solid rgba(255,255,255,0.12); }}
.loc {{ font-size: 36px; font-weight: 700; color: white; letter-spacing: -0.5px; }}
.amt {{ font-size: 44px; font-weight: 900; white-space: nowrap;
    background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
</style></head><body>
<div class="slide">
  <div class="list-bg"></div>
  <div class="list-wrap">
    <div class="list-eyebrow">{eyebrow}</div>
    <h1 class="list-title">{title}</h1>
    {rows_html}
  </div>
  <div class="swipe">Deslizá →</div>
  {WM}
</div></body></html>"""


def text_slide(eyebrow, title, cuerpo, title_size=64):
    """Placa de texto: volanta + titulo + parrafo, con los tokens del sistema."""
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
{BASE_CSS}
.list-bg {{ position: absolute; inset: 0; z-index: 1; background: {BG_DARK}; }}
.list-bg::before {{ content:''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 100% 0%, rgba({PRIMARY_RGB},0.2) 0%, transparent 55%),
                radial-gradient(ellipse at 0% 100%, rgba({DARK_RGB},0.5) 0%, transparent 55%); }}
.list-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 80px 100px 80px; }}
.list-eyebrow {{ font-size: 28px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 4px; color: {LIGHT}; margin-bottom: 24px; }}
.list-title {{ font-size: {title_size}px; font-weight: 800; line-height: 1.05;
    color: white; letter-spacing: -2px; margin-bottom: 40px; }}
.list-title .accent {{ background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
.cuerpo {{ font-size: 36px; font-weight: 400; line-height: 1.45;
    color: rgba(255,255,255,0.88); max-width: 900px; }}
</style></head><body>
<div class="slide">
  <div class="list-bg"></div>
  <div class="list-wrap">
    <div class="list-eyebrow">{eyebrow}</div>
    <h1 class="list-title">{title}</h1>
    <p class="cuerpo">{cuerpo}</p>
  </div>
  <div class="swipe">Deslizá →</div>
  {WM}
</div></body></html>"""


def split_video_slide(foto_b64, eyebrow, title, cuerpo, credito,
                      video_h=780, video_ratio=476/850, title_size=54):
    """Placa partida: video vertical enmarcado a la izquierda, texto a la derecha.
    Se usa cuando el material es vertical y en el marco centrado queda ilegible."""
    video_w = int(round(video_h * video_ratio))
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
{BASE_CSS}
.list-bg {{ position: absolute; inset: 0; z-index: 1; background: {BG_DARK}; }}
.list-bg::before {{ content:\'\'; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 100% 0%, rgba({PRIMARY_RGB},0.2) 0%, transparent 55%),
                radial-gradient(ellipse at 0% 100%, rgba({DARK_RGB},0.5) 0%, transparent 55%); }}
.split {{ position: absolute; inset: 0; z-index: 2;
    display: flex; align-items: center; gap: 46px;
    padding: 200px 80px 100px 80px; }}
.col-video {{ flex-shrink: 0; display: flex; flex-direction: column; align-items: center; }}
.frame {{ background: {GRADIENT}; padding: 5px; border-radius: 8px; }}
.frame img {{ display: block; width: {video_w}px; height: {video_h}px;
    object-fit: cover; border-radius: 4px; }}
.credito {{ font-size: 22px; font-weight: 600; color: rgba(255,255,255,0.6);
    margin-top: 14px; letter-spacing: 0.5px; }}
.col-texto {{ flex: 1; }}
.list-eyebrow {{ font-size: 28px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 4px; color: {LIGHT}; margin-bottom: 22px; }}
.list-title {{ font-size: {title_size}px; font-weight: 800; line-height: 1.08;
    color: white; letter-spacing: -1.5px; margin-bottom: 32px; }}
.list-title .accent {{ background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
.cuerpo {{ font-size: 31px; font-weight: 400; line-height: 1.42;
    color: rgba(255,255,255,0.9); }}
</style></head><body>
<div class="slide">
  <div class="list-bg"></div>
  <div class="split">
    <div class="col-video">
      <div class="frame"><img src="data:image/jpeg;base64,{foto_b64}"></div>
      <div class="credito">{credito}</div>
    </div>
    <div class="col-texto">
      <div class="list-eyebrow">{eyebrow}</div>
      <h1 class="list-title">{title}</h1>
      <p class="cuerpo">{cuerpo}</p>
    </div>
  </div>
  <div class="swipe">Deslizá →</div>
  {WM}
</div></body></html>"""


def framed_photo_slide(foto_b64, eyebrow, title, bajada, credito, max_h=600):
    """Foto enmarcada (variante de Layout 3c): la imagen entera dentro de un
    marco con el borde en gradiente de la paleta. Se usa cuando la foto no
    tolera sangrado (grupos con caras a media altura, flyers, material de
    terceros)."""
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
{BASE_CSS}
.list-bg {{ position: absolute; inset: 0; z-index: 1; background: {BG_DARK}; }}
.list-bg::before {{ content:''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 100% 0%, rgba({PRIMARY_RGB},0.2) 0%, transparent 55%),
                radial-gradient(ellipse at 0% 100%, rgba({DARK_RGB},0.5) 0%, transparent 55%); }}
.list-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 80px 100px 80px; }}
.list-eyebrow {{ font-size: 28px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 4px; color: {LIGHT}; margin-bottom: 24px; }}
.list-title {{ font-size: 64px; font-weight: 800; line-height: 1.05;
    color: white; letter-spacing: -2px; margin-bottom: 44px; }}
.list-title .accent {{ background: {GRADIENT};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
.frame {{ background: {GRADIENT}; padding: 5px; border-radius: 8px;
    align-self: center; max-width: 880px; }}
.frame img {{ display: block; max-width: 100%; max-height: {max_h}px;
    width: auto; border-radius: 4px; }}
.credito {{ font-size: 23px; font-weight: 600; color: rgba(255,255,255,0.6);
    align-self: center; margin-top: 16px; letter-spacing: 0.5px; }}
.bajada {{ font-size: 34px; font-weight: 400; line-height: 1.4;
    color: rgba(255,255,255,0.92); margin-top: 40px; }}
</style></head><body>
<div class="slide">
  <div class="list-bg"></div>
  <div class="list-wrap">
    <div class="list-eyebrow">{eyebrow}</div>
    <h1 class="list-title">{title}</h1>
    <div class="frame"><img src="data:image/jpeg;base64,{foto_b64}"></div>
    <div class="credito">{credito}</div>
    <p class="bajada">{bajada}</p>
  </div>
  <div class="swipe">Deslizá →</div>
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
    font-size: 34px; font-weight: 500; line-height: 1.4;
    color: rgba(255,255,255,0.92); font-style: italic;
    margin-bottom: 50px; max-width: 880px; }}
.close-quote::before {{ content:''; position: absolute; left: 0; top: 4px; bottom: 4px;
    width: 6px; background: {GRADIENT}; border-radius: 4px; }}
.cta {{ display: inline-block; align-self: flex-start;
    padding: 22px 44px; background: {GRADIENT};
    color: white; font-size: 26px; font-weight: 800;
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
    slides = [
        SLIDE1,                                                       # 1 portada con foto
        quote_slide(Q2_TEXT, Q2_LABEL, Q2_NAME, Q2_ROLE),             # 2 cita
        SLIDE4,                                                       # 3 número grande
        framed_photo_slide(FOTO_FLYER, FRAME_EYEBROW, FRAME_TITLE,
                           FRAME_BAJADA, FRAME_CREDIT, FRAME_MAX_H),  # 4 foto enmarcada
        list_slide(LIST_EYEBROW, LIST_TITLE, LIST_ITEMS),             # 5 lista
        rows_slide(ROWS_EYEBROW, ROWS_TITLE, ROWS_ITEMS),             # 6 filas
        text_slide(P7_EYEBROW, P7_TITLE, P7_CUERPO, P7_SIZE),         # 7 texto
        SLIDE7,                                                       # 8 cierre
    ]
    # Para material vertical de celular (9:16), reemplazar la 4 por:
    #   split_video_slide(FOTO_FLYER, FRAME_EYEBROW, FRAME_TITLE,
    #                     FRAME_BAJADA, FRAME_CREDIT, video_ratio=ANCHO/ALTO)
    for i, html in enumerate(slides, 1):
        (out / f'slide{i}.html').write_text(html)
    print(f'{len(slides)} slides written to {WORK_DIR} (paleta: {PALETA})')
    print(f'Next: python scripts/render.py {WORK_DIR}')
