"""
carousel.py — LIBRERÍA DE DISEÑO Estacionline. ÚNICA FUENTE DE VERDAD.

Todo el CSS del sistema de diseño vive acá. Para armar un carousel de
CUALQUIER cantidad y combinación de slides, componé llamadas a las
funciones slide_* — NUNCA escribas HTML/CSS de slides a mano.

Uso:

    import sys; sys.path.insert(0, '/ruta/a/la/skill/scripts')
    import carousel as c

    c.use_palette('violaceo')   # violaceo|verde|rosa|acero|atardecer|ocre

    slides = [
        c.slide_cover(c.photo('cover_b64.txt'), 'Gobierno abierto',
                      'Mapa <span class="accent">digital</span> para vigilar obras.',
                      'Prence propone transparencia en tiempo real.'),
        c.slide_list('Sistema municipal', 'Qué incluye el <span class="accent">proyecto</span>.',
                     [('Presupuesto oficial y ejecución', ''),
                      ('Plazos reales de finalización', '')], style='check'),
        c.slide_close('El objetivo', 'Cada rosarino sabrá dónde van <span class="accent">sus impuestos</span>.',
                      quote='Plazo: 90 días para implementar el sistema.',
                      cta='Más en estacionline.com →'),
    ]
    c.write_slides('/ruta/workdir', slides)
    # después: python render.py /ruta/workdir

Notas:
- El span <span class="accent">...</span> aplica el gradiente de la paleta
  dentro de títulos y citas.
- Las fotos van como base64 (usar photo('archivo_b64.txt') o pasar el
  string base64 directo). Nunca CSS background.
"""
from pathlib import Path

# =============================================================================
# PALETAS — valores exactos de SKILL.md. No editar por-carousel.
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

_P = None  # paleta activa (dict con PRIMARY, LIGHT, DARK, BG_DARK, *_RGB, GRADIENT)


def _rgb(hex_color: str) -> str:
    h = hex_color.lstrip('#')
    return f'{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)}'


def use_palette(name: str) -> dict:
    """Activa una paleta. Llamar SIEMPRE antes de construir slides."""
    global _P
    if name not in PALETTES:
        raise ValueError(f"Paleta '{name}' no existe. Opciones: {', '.join(PALETTES)}")
    p = dict(PALETTES[name])
    p['NAME'] = name
    p['BG_RGB'] = _rgb(p['BG_DARK'])
    p['PRIMARY_RGB'] = _rgb(p['PRIMARY'])
    p['DARK_RGB'] = _rgb(p['DARK'])
    if name == 'atardecer':
        # Única paleta con gradiente multicolor de 5 stops — parte del concepto.
        p['GRADIENT'] = ('linear-gradient(135deg, '
                         '#FBBF24 0%, #F97316 30%, #EF4444 55%, #EC4899 75%, #A855F7 100%)')
    else:
        p['GRADIENT'] = f"linear-gradient(165deg, {p['DARK']} 0%, {p['PRIMARY']} 50%, {p['LIGHT']} 100%)"
    _P = p
    return p


def _pal() -> dict:
    if _P is None:
        raise RuntimeError('Llamá use_palette(...) antes de construir slides.')
    return _P


def photo(source: str) -> str:
    """Devuelve el base64 de una foto: acepta un path a *_b64.txt o el string b64."""
    p = Path(source)
    if p.exists():
        return p.read_text().strip()
    return source.strip()

# =============================================================================
# BASE — wordmark + reset. Presente en toda slide, no se toca.
# =============================================================================


def _base_css() -> str:
    P = _pal()
    return f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
/* color:#fff en body = red de seguridad: nada puede salir negro por defecto */
body {{ width: 1080px; height: 1350px; font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
    overflow: hidden; color: #fff; }}
.slide {{ width: 1080px; height: 1350px; position: relative; overflow: hidden; background: {P['BG_DARK']}; }}
.accent {{ background: {P['GRADIENT']};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
/* Wordmark: arriba a la derecha, GRANDE (estándar desde mayo 2026).
   El zócalo inferior de 84px está DEPRECADO — no volver a usarlo. */
.wordmark {{ position: absolute; top: 50px; right: 60px; z-index: 10; text-align: right; }}
.wordmark .brand {{ display: block; font-size: 52px; font-weight: 900; letter-spacing: -1.5px;
    line-height: 1.05;
    background: {P['GRADIENT']}; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
.wordmark .site {{ display: block; font-size: 20px; font-weight: 600; margin-top: 2px;
    color: rgba(255,255,255,0.7); }}
/* Variante para slides con foto: drop-shadow (no text-shadow, que se ve mal
   con texto en gradiente). */
.wordmark.on-photo {{ filter: drop-shadow(0 2px 10px rgba(0,0,0,0.6)); }}
"""


def _wm(on_photo: bool = False) -> str:
    cls = 'wordmark on-photo' if on_photo else 'wordmark'
    return (f'<div class="{cls}"><span class="brand">Estacionline</span>'
            f'<span class="site">estacionline.com</span></div>')


def _doc(css: str, body: str, on_photo: bool = False) -> str:
    return (f'<!DOCTYPE html><html><head><meta charset="UTF-8"><style>'
            f'{_base_css()}{css}</style></head><body>'
            f'<div class="slide">{body}{_wm(on_photo)}</div></body></html>')


def _overlay_bottom() -> str:
    P = _pal()
    return f"""linear-gradient(180deg,
        rgba({P['BG_RGB']},0.20) 0%,
        rgba({P['BG_RGB']},0.30) 35%,
        rgba({P['BG_RGB']},0.85) 60%,
        rgba({P['BG_RGB']},0.98) 80%,
        rgba({P['BG_RGB']},1) 100%)"""


def _overlay_top() -> str:
    P = _pal()
    return f"""linear-gradient(180deg,
        rgba({P['BG_RGB']},0.98) 0%,
        rgba({P['BG_RGB']},0.92) 22%,
        rgba({P['BG_RGB']},0.55) 55%,
        rgba({P['BG_RGB']},0.25) 100%)"""

# =============================================================================
# SLIDES — componé las que necesites, en el orden que necesites
# =============================================================================


def slide_cover(foto_b64: str, eyebrow: str, title: str, sub: str,
                obj_pos: str = 'center 30%', swipe: str = 'Deslizá →') -> str:
    """Layout 1: portada con foto de fondo, overlay oscuro abajo, texto abajo."""
    P = _pal()
    css = f"""
.photo {{ position: absolute; inset: 0; width: 100%; height: 100%;
    object-fit: cover; object-position: {obj_pos}; z-index: 1; }}
.overlay {{ position: absolute; inset: 0; z-index: 2; background: {_overlay_bottom()}; }}
.cover-content {{ position: absolute; inset: 0; z-index: 3;
    display: flex; flex-direction: column; justify-content: flex-end;
    padding: 0 80px 140px 80px; }}
.eyebrow {{ font-size: 26px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 5px; color: {P['LIGHT']}; margin-bottom: 32px; }}
.cover-title {{ font-size: 92px; font-weight: 900; line-height: 0.98;
    color: white; letter-spacing: -3px; margin-bottom: 32px; }}
.cover-sub {{ font-size: 28px; font-weight: 500; color: rgba(255,255,255,0.92);
    line-height: 1.3; max-width: 850px; }}
.swipe {{ position: absolute; bottom: 70px; right: 80px; z-index: 4;
    font-size: 20px; font-weight: 600; color: {P['LIGHT']};
    text-transform: uppercase; letter-spacing: 3px; }}
"""
    body = f"""
  <img class="photo" src="data:image/jpeg;base64,{foto_b64}">
  <div class="overlay"></div>
  <div class="cover-content">
    <div class="eyebrow">{eyebrow}</div>
    <h1 class="cover-title">{title}</h1>
    <p class="cover-sub">{sub}</p>
  </div>
  <div class="swipe">{swipe}</div>"""
    return _doc(css, body, on_photo=True)


def slide_quote(text: str, name: str, role: str,
                attrib_label: str = '— Sus palabras') -> str:
    """Layout 2: pull-quote grande sin foto, con atribución."""
    P = _pal()
    css = f"""
.quote-bg {{ position: absolute; inset: 0; z-index: 1; background: {P['BG_DARK']}; }}
.quote-bg::before {{ content:''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 50% 50%, rgba({P['DARK_RGB']},0.7) 0%, transparent 70%); }}
/* Sin foto: top 220px despeja el wordmark. */
.quote-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 90px 100px 90px; }}
.big-quote-mark {{ font-size: 200px; font-weight: 900; line-height: 0.7;
    background: {P['GRADIENT']};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 10px; }}
.big-quote {{ font-size: 60px; font-weight: 700; line-height: 1.15;
    color: white; letter-spacing: -1.5px; margin-bottom: 50px; }}
.big-quote .accent {{ background: none; -webkit-text-fill-color: {P['LIGHT']}; color: {P['LIGHT']}; }}
.attrib {{ font-size: 22px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 3px; color: {P['PRIMARY']}; }}
.attrib-name {{ color: white; font-size: 28px; margin-top: 6px; font-weight: 700; }}
.attrib-role {{ color: rgba(255,255,255,0.7); font-size: 20px; margin-top: 4px;
    font-weight: 500; }}
"""
    body = f"""
  <div class="quote-bg"></div>
  <div class="quote-wrap">
    <div class="big-quote-mark">"</div>
    <p class="big-quote">{text}</p>
    <div class="attrib">{attrib_label}</div>
    <div class="attrib-name">{name}</div>
    <div class="attrib-role">{role}</div>
  </div>"""
    return _doc(css, body)


def slide_photo_text(foto_b64: str, eyebrow: str, title: str, bajada: str,
                     obj_pos: str = 'center 25%', text_pos: str = 'bottom') -> str:
    """Layout 3a/3b: foto de fondo + texto abajo (default) o arriba.

    text_pos='top' cuando la cara del sujeto está en la mitad INFERIOR de la foto.
    """
    P = _pal()
    if text_pos == 'bottom':
        overlay, justify, padding = _overlay_bottom(), 'flex-end', '80px 80px 110px 80px'
    else:
        overlay, justify, padding = _overlay_top(), 'flex-start', '220px 80px 110px 80px'
    css = f"""
.photo {{ position: absolute; inset: 0; width: 100%; height: 100%;
    object-fit: cover; object-position: {obj_pos}; z-index: 1; }}
.overlay {{ position: absolute; inset: 0; z-index: 2; background: {overlay}; }}
.content {{ position: absolute; inset: 0; z-index: 3;
    display: flex; flex-direction: column; justify-content: {justify};
    padding: {padding}; }}
.eyebrow {{ font-size: 26px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 4px; color: {P['LIGHT']}; margin-bottom: 24px; }}
.title {{ font-size: 70px; font-weight: 800; line-height: 1.05;
    color: white; letter-spacing: -2px; margin-bottom: 32px; }}
.bajada {{ font-size: 28px; font-weight: 400; line-height: 1.4;
    color: rgba(255,255,255,0.92); }}
"""
    body = f"""
  <img class="photo" src="data:image/jpeg;base64,{foto_b64}">
  <div class="overlay"></div>
  <div class="content">
    <div class="eyebrow">{eyebrow}</div>
    <h1 class="title">{title}</h1>
    <p class="bajada">{bajada}</p>
  </div>"""
    return _doc(css, body, on_photo=True)


def slide_photo_contain(foto_b64: str, eyebrow: str, title: str, bajada: str) -> str:
    """Layout 3c (fallback): foto entera arriba (contain), texto debajo.

    Usar cuando el usuario no quiere que se recorten los sujetos de una
    foto horizontal.
    """
    P = _pal()
    css = f"""
.bg {{ position: absolute; inset: 0; z-index: 1; background: {P['BG_DARK']}; }}
.photo {{ position: absolute; top: 0; left: 0; right: 0;
    width: 100%; height: 760px;
    object-fit: contain; z-index: 2; background: {P['BG_DARK']}; }}
.content {{ position: absolute; top: 780px; left: 0; right: 0; bottom: 0; z-index: 3;
    display: flex; flex-direction: column; justify-content: flex-start;
    padding: 30px 80px 60px 80px; }}
.eyebrow {{ font-size: 26px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 4px; color: {P['LIGHT']}; margin-bottom: 22px; }}
.title {{ font-size: 56px; font-weight: 800; line-height: 1.05;
    color: white; letter-spacing: -1.5px; margin-bottom: 24px; }}
.bajada {{ font-size: 22px; font-weight: 400; line-height: 1.4;
    color: rgba(255,255,255,0.85); }}
"""
    body = f"""
  <div class="bg"></div>
  <img class="photo" src="data:image/jpeg;base64,{foto_b64}">
  <div class="content">
    <div class="eyebrow">{eyebrow}</div>
    <h1 class="title">{title}</h1>
    <p class="bajada">{bajada}</p>
  </div>"""
    return _doc(css, body, on_photo=True)


def slide_number(eyebrow: str, number: str, unit: str, desc: str,
                 size: int = None) -> str:
    """Layout 4: dato numérico LITERAL gigante.

    size se calcula solo según el largo del número; pasalo explícito solo
    si hace falta ajustar.
    """
    P = _pal()
    if size is None:
        n = len(number)
        size = 380 if n <= 4 else (240 if n <= 6 else 170)
    css = f"""
.num-bg {{ position: absolute; inset: 0; z-index: 1; background: {P['BG_DARK']}; }}
.num-bg::before {{ content:''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 30% 30%, rgba({P['PRIMARY_RGB']},0.25) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 90%, rgba({P['DARK_RGB']},0.5) 0%, transparent 55%); }}
.num-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 80px 100px 80px; }}
.num-eyebrow {{ font-size: 26px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 4px; color: {P['LIGHT']}; margin-bottom: 30px; }}
/* line-height 1.1 + padding vertical: previenen clipping del gradiente.
   min-width 440px: evita corte horizontal con símbolos (%, −, +). */
.big-num {{ font-size: {size}px; font-weight: 900;
    line-height: 1.1; padding: 8px 0; min-width: 440px;
    background: {P['GRADIENT']};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -10px; margin-bottom: 10px; }}
.num-unit {{ font-size: 56px; font-weight: 700; color: white;
    margin-bottom: 40px; letter-spacing: -1px; }}
.num-desc {{ font-size: 32px; font-weight: 500; line-height: 1.35;
    color: rgba(255,255,255,0.9); max-width: 880px; }}
"""
    body = f"""
  <div class="num-bg"></div>
  <div class="num-wrap">
    <div class="num-eyebrow">{eyebrow}</div>
    <div class="big-num">{number}</div>
    <div class="num-unit">{unit}</div>
    <p class="num-desc">{desc}</p>
  </div>"""
    return _doc(css, body)


def slide_list(eyebrow: str, title: str, items: list, style: str = 'numbered') -> str:
    """Layout 5a: lista de ítems. items = [(titulo, descripcion), ...].

    style='numbered' -> 01/02/03 ...   style='check' -> tildes ✓
    La descripción puede ser '' para ítems de una sola línea.
    """
    P = _pal()
    rows = []
    for idx, (t, d) in enumerate(items, 1):
        marker = f'{idx:02d}' if style == 'numbered' else '✓'
        desc_html = f'<p>{d}</p>' if d else ''
        rows.append(f'''<div class="item">
      <div class="num">{marker}</div>
      <div class="item-body"><h3>{t}</h3>{desc_html}</div>
    </div>''')
    items_html = '\n'.join(rows)
    css = f"""
.list-bg {{ position: absolute; inset: 0; z-index: 1; background: {P['BG_DARK']}; }}
.list-bg::before {{ content:''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 100% 0%, rgba({P['PRIMARY_RGB']},0.2) 0%, transparent 55%),
                radial-gradient(ellipse at 0% 100%, rgba({P['DARK_RGB']},0.5) 0%, transparent 55%); }}
.list-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 80px 100px 80px; }}
.list-eyebrow {{ font-size: 26px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 4px; color: {P['LIGHT']}; margin-bottom: 24px; }}
.list-title {{ font-size: 64px; font-weight: 800; line-height: 1.05;
    color: white; letter-spacing: -2px; margin-bottom: 60px; }}
.item {{ display: flex; gap: 28px; margin-bottom: 40px; align-items: flex-start; }}
.num {{ flex-shrink: 0;
    font-size: 32px; font-weight: 800;
    background: {P['GRADIENT']};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    padding-top: 8px; min-width: 50px; }}
.item-body h3 {{ font-size: 38px; font-weight: 700; color: white;
    line-height: 1.15; margin-bottom: 8px; letter-spacing: -1px; }}
.item-body p {{ font-size: 24px; font-weight: 400; color: rgba(255,255,255,0.78);
    line-height: 1.4; }}
"""
    body = f"""
  <div class="list-bg"></div>
  <div class="list-wrap">
    <div class="list-eyebrow">{eyebrow}</div>
    <h1 class="list-title">{title}</h1>
    {items_html}
  </div>"""
    return _doc(css, body)


def slide_table(eyebrow: str, title: str, rows: list) -> str:
    """Layout 5b: filas localidad + cantidad. rows = [(loc, amt), ...]."""
    P = _pal()
    rows_html = '\n'.join(
        f'<div class="row"><span class="loc">{loc}</span><span class="amt">{amt}</span></div>'
        for loc, amt in rows
    )
    css = f"""
.list-bg {{ position: absolute; inset: 0; z-index: 1; background: {P['BG_DARK']}; }}
.list-bg::before {{ content:''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 100% 0%, rgba({P['PRIMARY_RGB']},0.2) 0%, transparent 55%),
                radial-gradient(ellipse at 0% 100%, rgba({P['DARK_RGB']},0.5) 0%, transparent 55%); }}
.list-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 80px 100px 80px; }}
.list-eyebrow {{ font-size: 26px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 4px; color: {P['LIGHT']}; margin-bottom: 24px; }}
.list-title {{ font-size: 64px; font-weight: 800; line-height: 1.05;
    color: white; letter-spacing: -2px; margin-bottom: 50px; }}
.row {{ display: flex; justify-content: space-between; align-items: baseline;
    padding: 22px 0; border-bottom: 1px solid rgba(255,255,255,0.12); }}
.loc {{ font-size: 30px; font-weight: 700; color: white; letter-spacing: -0.5px; }}
.amt {{ font-size: 38px; font-weight: 900;
    background: {P['GRADIENT']};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
"""
    body = f"""
  <div class="list-bg"></div>
  <div class="list-wrap">
    <div class="list-eyebrow">{eyebrow}</div>
    <h1 class="list-title">{title}</h1>
    {rows_html}
  </div>"""
    return _doc(css, body)


def slide_close(eyebrow: str, title: str, quote: str = None,
                cta: str = 'Más en estacionline.com →') -> str:
    """Layout 6: cierre con título grande, cita opcional y botón CTA."""
    P = _pal()
    quote_html = f'<p class="close-quote">{quote}</p>' if quote else ''
    css = f"""
.close-bg {{ position: absolute; inset: 0; z-index: 1; background: {P['BG_DARK']}; }}
.close-bg::before {{ content:''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 50% 30%, rgba({P['PRIMARY_RGB']},0.3) 0%, transparent 60%),
                radial-gradient(ellipse at 50% 100%, rgba({P['DARK_RGB']},0.7) 0%, transparent 60%); }}
.close-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 80px 100px 80px; }}
.close-eyebrow {{ font-size: 26px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 5px; color: {P['LIGHT']}; margin-bottom: 36px; }}
.close-title {{ font-size: 84px; font-weight: 900; line-height: 1.0;
    color: white; letter-spacing: -3px; margin-bottom: 50px; }}
.close-quote {{ position: relative; padding-left: 32px;
    font-size: 28px; font-weight: 500; line-height: 1.4;
    color: rgba(255,255,255,0.92); font-style: italic;
    margin-bottom: 50px; max-width: 880px; }}
.close-quote::before {{ content:''; position: absolute; left: 0; top: 4px; bottom: 4px;
    width: 6px; background: {P['GRADIENT']}; border-radius: 4px; }}
.cta {{ display: inline-block; align-self: flex-start;
    padding: 22px 44px; background: {P['GRADIENT']};
    color: white; font-size: 24px; font-weight: 800;
    border-radius: 100px; letter-spacing: -0.5px; }}
"""
    body = f"""
  <div class="close-bg"></div>
  <div class="close-wrap">
    <div class="close-eyebrow">{eyebrow}</div>
    <h1 class="close-title">{title}</h1>
    {quote_html}
    <div class="cta">{cta}</div>
  </div>"""
    return _doc(css, body)

# =============================================================================
# SALIDA
# =============================================================================


def write_slides(work_dir: str, slides: list) -> None:
    """Escribe slide1.html ... slideN.html en work_dir, en el orden dado."""
    out = Path(work_dir)
    out.mkdir(parents=True, exist_ok=True)
    for i, html in enumerate(slides, 1):
        (out / f'slide{i}.html').write_text(html)
    print(f'{len(slides)} slides escritas en {work_dir} (paleta: {_pal()["NAME"]})')
    print(f'Siguiente paso: python render.py {work_dir}')
