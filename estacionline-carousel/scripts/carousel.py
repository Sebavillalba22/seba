"""
carousel.py — LIBRERÍA DE DISEÑO Estacionline. ÚNICA FUENTE DE VERDAD.

Todo el CSS del sistema de diseño vive acá. Para armar un carousel de
CUALQUIER cantidad y combinación de slides, componé llamadas a las
funciones slide_* — NUNCA escribas HTML/CSS de slides a mano.

La estética está calibrada contra placas reales aprobadas (julio 2026):
gradiente claro→oscuro, títulos 64px, cuerpo 34px, cita con barra lateral,
CTA claro con texto oscuro, "Deslizá →" en toda slide menos la final,
crédito de foto abajo a la izquierda.

Uso:

    import sys; sys.path.insert(0, '/ruta/a/la/skill/scripts')
    import carousel as c

    c.use_palette('celeste')  # violaceo|verde|rosa|acero|celeste|atardecer|ocre

    slides = [
        c.slide_cover(c.photo('cover_b64.txt'), 'Entrevista exclusiva',
                      'Topa lanzó <span class="accent">"Me muevo por aquí Mundial"</span>',
                      'En diálogo exclusivo con Estacionline.',
                      credit='Foto: @phsabaris'),
        c.slide_text('Cómo nació', 'De un amigo y un <span class="accent">viaje a Italia</span>',
                     'La idea llegó de la mano de su amigo <b>Pato</b>.',
                     quote='"Le cambiamos un poquito algunas cositas."'),
        c.slide_number('En una sola palabra', 'Épica',
                       desc='Así definió Topa a <b>"Me muevo por aquí Mundial"</b>.'),
        c.slide_close('"Sería icónico, sería hermoso que la pueda cantar todo el país."',
                      name='Diego Topa', role='En diálogo exclusivo con Estacionline',
                      cta='Leé la entrevista completa →', credit='Foto: @phsabaris'),
    ]
    c.write_slides('/ruta/workdir', slides)
    # después: python render.py /ruta/workdir

Notas de contenido:
- <span class="accent">…</span> aplica el gradiente de la paleta en títulos.
- <b>…</b> resalta palabras en el cuerpo (queda blanco puro, peso 700).
- Usar comillas tipográficas " " en los textos, no comillas rectas.
- Las fotos van como base64 (photo('archivo_b64.txt')). Nunca CSS background.
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
    # Celeste — Mundial / Scaloneta / deporte / albiceleste
    'celeste':   dict(PRIMARY='#4E94D6', LIGHT='#A6CEF0', DARK='#1C4E7E', BG_DARK='#0A1826'),
    # Atardecer — provincia / economía / crisis (gradiente especial de 5 stops)
    'atardecer': dict(PRIMARY='#F97316', LIGHT='#FBBF24', DARK='#7C2D6F', BG_DARK='#1A0510'),
    # Amarillo ocre — random / gaming / premium
    'ocre':      dict(PRIMARY='#D4A53A', LIGHT='#E8C474', DARK='#5C3D0F', BG_DARK='#14100A'),
}

_P = None  # paleta activa


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
        # Estética actual: claro arriba → color pleno abajo.
        p['GRADIENT'] = f"linear-gradient(180deg, {p['LIGHT']} 0%, {p['PRIMARY']} 100%)"
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
# BASE — wordmark, deslizá, crédito. Presentes según reglas, no se tocan.
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
b, strong {{ font-weight: 700; color: #fff; }}
/* Wordmark: arriba a la derecha, GRANDE (estándar desde mayo 2026).
   El zócalo inferior de 84px está DEPRECADO — no volver a usarlo. */
.wordmark {{ position: absolute; top: 50px; right: 60px; z-index: 10; text-align: right;
    filter: drop-shadow(0 2px 8px rgba(0,0,0,0.45)); }}
.wordmark .brand {{ display: block; font-size: 52px; font-weight: 900; letter-spacing: -1.5px;
    line-height: 1.05;
    background: {P['GRADIENT']}; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
.wordmark .site {{ display: block; font-size: 20px; font-weight: 600; margin-top: 2px;
    color: rgba(255,255,255,0.7); }}
.wordmark.on-photo {{ filter: drop-shadow(0 2px 10px rgba(0,0,0,0.65)); }}
/* Deslizá → en toda slide menos la final */
.swipe {{ position: absolute; bottom: 70px; right: 80px; z-index: 9;
    font-size: 20px; font-weight: 600; color: {P['LIGHT']};
    text-transform: uppercase; letter-spacing: 3px; }}
/* Crédito de foto abajo a la izquierda */
.credit {{ position: absolute; bottom: 70px; left: 80px; z-index: 9;
    font-size: 22px; font-weight: 600; color: rgba(255,255,255,0.5); }}
"""


def _wm(on_photo: bool = False) -> str:
    cls = 'wordmark on-photo' if on_photo else 'wordmark'
    return (f'<div class="{cls}"><span class="brand">Estacionline</span>'
            f'<span class="site">estacionline.com</span></div>')


def _extras(swipe: bool, credit: str = None, swipe_text: str = 'Deslizá →') -> str:
    html = ''
    if credit:
        html += f'<div class="credit">{credit}</div>'
    if swipe:
        html += f'<div class="swipe">{swipe_text}</div>'
    return html


def _doc(css: str, body: str, on_photo: bool = False,
         swipe: bool = True, credit: str = None) -> str:
    return (f'<!DOCTYPE html><html><head><meta charset="UTF-8"><style>'
            f'{_base_css()}{css}</style></head><body>'
            f'<div class="slide">{body}{_extras(swipe, credit)}{_wm(on_photo)}</div>'
            f'</body></html>')


def _overlay_bottom() -> str:
    P = _pal()
    return f"""linear-gradient(180deg,
        rgba({P['BG_RGB']},0.15) 0%,
        rgba({P['BG_RGB']},0.25) 35%,
        rgba({P['BG_RGB']},0.85) 60%,
        rgba({P['BG_RGB']},0.98) 78%,
        rgba({P['BG_RGB']},1) 100%)"""


def _overlay_top() -> str:
    P = _pal()
    return f"""linear-gradient(180deg,
        rgba({P['BG_RGB']},0.98) 0%,
        rgba({P['BG_RGB']},0.92) 22%,
        rgba({P['BG_RGB']},0.55) 55%,
        rgba({P['BG_RGB']},0.25) 100%)"""


def _bg_glow() -> str:
    """Fondo sin foto: glow radial sutil de la paleta."""
    P = _pal()
    return f"""
.bg {{ position: absolute; inset: 0; z-index: 1; background: {P['BG_DARK']}; }}
.bg::before {{ content:''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 35% 45%, rgba({P['DARK_RGB']},0.55) 0%, transparent 65%),
                radial-gradient(ellipse at 85% 90%, rgba({P['PRIMARY_RGB']},0.12) 0%, transparent 55%); }}
"""

# Tipografía compartida (estética julio 2026)
_EYEBROW = """font-size: 26px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 4px;"""
_TITLE = """font-size: 64px; font-weight: 800; line-height: 1.12;
    color: white; letter-spacing: -1.5px;"""
_BODY = """font-size: 34px; font-weight: 400; line-height: 1.45;
    color: rgba(255,255,255,0.92); max-width: 900px;"""

# =============================================================================
# SLIDES — componé las que necesites, en el orden que necesites
# =============================================================================


def slide_cover(foto_b64: str, eyebrow: str, title: str, sub: str,
                obj_pos: str = 'center 30%', credit: str = None,
                swipe: bool = True) -> str:
    """Layout 1: portada con foto de fondo, overlay que funde al navy, texto abajo."""
    P = _pal()
    css = f"""
.photo {{ position: absolute; inset: 0; width: 100%; height: 100%;
    object-fit: cover; object-position: {obj_pos}; z-index: 1; }}
.overlay {{ position: absolute; inset: 0; z-index: 2; background: {_overlay_bottom()}; }}
.cover-content {{ position: absolute; inset: 0; z-index: 3;
    display: flex; flex-direction: column; justify-content: flex-end;
    padding: 0 80px 160px 80px; }}
.eyebrow {{ {_EYEBROW} color: {P['LIGHT']}; margin-bottom: 28px; }}
.cover-title {{ {_TITLE} margin-bottom: 28px; }}
.cover-sub {{ font-size: 30px; font-weight: 400; color: rgba(255,255,255,0.88);
    line-height: 1.4; max-width: 900px; }}
"""
    body = f"""
  <img class="photo" src="data:image/jpeg;base64,{foto_b64}">
  <div class="overlay"></div>
  <div class="cover-content">
    <div class="eyebrow">{eyebrow}</div>
    <h1 class="cover-title">{title}</h1>
    <p class="cover-sub">{sub}</p>
  </div>"""
    return _doc(css, body, on_photo=True, swipe=swipe, credit=credit)


def slide_text(eyebrow: str, title: str, body: str, quote: str = None,
               swipe: bool = True, credit: str = None) -> str:
    """Layout 7: slide de texto sin foto — eyebrow + título + cuerpo +
    cita opcional en color de la paleta. Para desarrollo del tema."""
    P = _pal()
    quote_html = f'<p class="t-quote">{quote}</p>' if quote else ''
    css = _bg_glow() + f"""
.text-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: flex-start;
    padding: 230px 80px 150px 80px; }}
.eyebrow {{ {_EYEBROW} color: {P['LIGHT']}; margin-bottom: 26px; }}
.t-title {{ {_TITLE} margin-bottom: 40px; }}
.t-body {{ {_BODY} margin-bottom: 40px; }}
.t-quote {{ font-size: 33px; font-weight: 600; font-style: italic;
    line-height: 1.4; color: {P['LIGHT']}; max-width: 900px; }}
"""
    body_html = f"""
  <div class="bg"></div>
  <div class="text-wrap">
    <div class="eyebrow">{eyebrow}</div>
    <h1 class="t-title">{title}</h1>
    <p class="t-body">{body}</p>
    {quote_html}
  </div>"""
    return _doc(css, body_html, swipe=swipe, credit=credit)


def slide_quote(text: str, name: str, role: str,
                eyebrow: str = None, swipe: bool = True,
                credit: str = None) -> str:
    """Layout 2: cita protagonista con barra lateral + atribución en línea."""
    P = _pal()
    eyebrow_html = f'<div class="eyebrow">{eyebrow}</div>' if eyebrow else ''
    css = _bg_glow() + f"""
.quote-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 80px 150px 80px; }}
.eyebrow {{ {_EYEBROW} color: {P['LIGHT']}; margin-bottom: 40px; }}
.q-text {{ position: relative; padding-left: 36px;
    font-size: 46px; font-weight: 600; line-height: 1.3;
    color: white; letter-spacing: -0.5px; margin-bottom: 36px; max-width: 920px; }}
.q-text::before {{ content:''; position: absolute; left: 0; top: 8px; bottom: 8px;
    width: 6px; background: {P['GRADIENT']}; border-radius: 4px; }}
.q-attrib {{ font-size: 26px; }}
.q-attrib .name {{ font-weight: 700; color: white; }}
.q-attrib .role {{ font-weight: 600; color: rgba(255,255,255,0.6); }}
"""
    body = f"""
  <div class="bg"></div>
  <div class="quote-wrap">
    {eyebrow_html}
    <p class="q-text">{text}</p>
    <div class="q-attrib"><span class="name">{name}</span>
      <span class="role"> · {role}</span></div>
  </div>"""
    return _doc(css, body, swipe=swipe, credit=credit)


def slide_photo_text(foto_b64: str, eyebrow: str, title: str, bajada: str,
                     obj_pos: str = 'center 25%', text_pos: str = 'bottom',
                     credit: str = None, swipe: bool = True) -> str:
    """Layout 3a/3b: foto de fondo + texto abajo (default) o arriba.

    text_pos='top' cuando la cara del sujeto está en la mitad INFERIOR de la foto.
    """
    P = _pal()
    if text_pos == 'bottom':
        overlay, justify, padding = _overlay_bottom(), 'flex-end', '80px 80px 160px 80px'
    else:
        overlay, justify, padding = _overlay_top(), 'flex-start', '230px 80px 160px 80px'
    css = f"""
.photo {{ position: absolute; inset: 0; width: 100%; height: 100%;
    object-fit: cover; object-position: {obj_pos}; z-index: 1; }}
.overlay {{ position: absolute; inset: 0; z-index: 2; background: {overlay}; }}
.content {{ position: absolute; inset: 0; z-index: 3;
    display: flex; flex-direction: column; justify-content: {justify};
    padding: {padding}; }}
.eyebrow {{ {_EYEBROW} color: {P['LIGHT']}; margin-bottom: 24px; }}
.title {{ {_TITLE} margin-bottom: 30px; }}
.bajada {{ font-size: 30px; font-weight: 400; line-height: 1.4;
    color: rgba(255,255,255,0.9); max-width: 900px; }}
"""
    body = f"""
  <img class="photo" src="data:image/jpeg;base64,{foto_b64}">
  <div class="overlay"></div>
  <div class="content">
    <div class="eyebrow">{eyebrow}</div>
    <h1 class="title">{title}</h1>
    <p class="bajada">{bajada}</p>
  </div>"""
    return _doc(css, body, on_photo=True, swipe=swipe, credit=credit)


def slide_photo_contain(foto_b64: str, eyebrow: str, title: str, bajada: str,
                        credit: str = None, swipe: bool = True) -> str:
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
    padding: 30px 80px 130px 80px; }}
.eyebrow {{ {_EYEBROW} color: {P['LIGHT']}; margin-bottom: 22px; }}
.title {{ font-size: 54px; font-weight: 800; line-height: 1.1;
    color: white; letter-spacing: -1.5px; margin-bottom: 22px; }}
.bajada {{ font-size: 26px; font-weight: 400; line-height: 1.4;
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
    return _doc(css, body, on_photo=True, swipe=swipe, credit=credit)


def slide_number(eyebrow: str, number: str, desc: str, unit: str = None,
                 size: int = None, swipe: bool = True, credit: str = None) -> str:
    """Layout 4: dato LITERAL gigante — número o palabra clave ("Épica").

    size se calcula solo según el largo; pasalo explícito solo para ajustes.
    """
    P = _pal()
    if size is None:
        n = len(number)
        size = 300 if n <= 4 else (220 if n <= 6 else 160)
    unit_html = f'<div class="num-unit">{unit}</div>' if unit else ''
    css = _bg_glow() + f"""
.num-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 80px 150px 80px; }}
.num-eyebrow {{ {_EYEBROW} color: {P['LIGHT']}; margin-bottom: 24px; }}
/* line-height + padding vertical: previenen clipping del gradiente.
   min-width 440px: evita corte horizontal con símbolos (%, −, +). */
.big-num {{ font-size: {size}px; font-weight: 900;
    line-height: 1.08; padding: 8px 0; min-width: 440px;
    background: {P['GRADIENT']};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em; margin-bottom: 24px; }}
.num-unit {{ font-size: 48px; font-weight: 700; color: white;
    margin-bottom: 32px; letter-spacing: -1px; }}
.num-desc {{ {_BODY} }}
"""
    body = f"""
  <div class="bg"></div>
  <div class="num-wrap">
    <div class="num-eyebrow">{eyebrow}</div>
    <div class="big-num">{number}</div>
    {unit_html}
    <p class="num-desc">{desc}</p>
  </div>"""
    return _doc(css, body, swipe=swipe, credit=credit)


def slide_list(eyebrow: str, title: str, items: list, style: str = 'numbered',
               swipe: bool = True, credit: str = None) -> str:
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
    css = _bg_glow() + f"""
.list-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 80px 150px 80px; }}
.list-eyebrow {{ {_EYEBROW} color: {P['LIGHT']}; margin-bottom: 24px; }}
.list-title {{ {_TITLE} margin-bottom: 56px; }}
.item {{ display: flex; gap: 28px; margin-bottom: 40px; align-items: flex-start; }}
.num {{ flex-shrink: 0;
    font-size: 32px; font-weight: 800;
    background: {P['GRADIENT']};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    padding-top: 6px; min-width: 50px; }}
.item-body h3 {{ font-size: 38px; font-weight: 700; color: white;
    line-height: 1.15; margin-bottom: 8px; letter-spacing: -1px; }}
.item-body p {{ font-size: 26px; font-weight: 400; color: rgba(255,255,255,0.78);
    line-height: 1.4; }}
"""
    body = f"""
  <div class="bg"></div>
  <div class="list-wrap">
    <div class="list-eyebrow">{eyebrow}</div>
    <h1 class="list-title">{title}</h1>
    {items_html}
  </div>"""
    return _doc(css, body, swipe=swipe, credit=credit)


def slide_table(eyebrow: str, title: str, rows: list,
                swipe: bool = True, credit: str = None) -> str:
    """Layout 5b: filas localidad + cantidad. rows = [(loc, amt), ...]."""
    P = _pal()
    rows_html = '\n'.join(
        f'<div class="row"><span class="loc">{loc}</span><span class="amt">{amt}</span></div>'
        for loc, amt in rows
    )
    css = _bg_glow() + f"""
.list-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 80px 150px 80px; }}
.list-eyebrow {{ {_EYEBROW} color: {P['LIGHT']}; margin-bottom: 24px; }}
.list-title {{ {_TITLE} margin-bottom: 48px; }}
.row {{ display: flex; justify-content: space-between; align-items: baseline;
    padding: 22px 0; border-bottom: 1px solid rgba(255,255,255,0.12); }}
.loc {{ font-size: 30px; font-weight: 700; color: white; letter-spacing: -0.5px; }}
.amt {{ font-size: 38px; font-weight: 900;
    background: {P['GRADIENT']};
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
"""
    body = f"""
  <div class="bg"></div>
  <div class="list-wrap">
    <div class="list-eyebrow">{eyebrow}</div>
    <h1 class="list-title">{title}</h1>
    {rows_html}
  </div>"""
    return _doc(css, body, swipe=swipe, credit=credit)


def slide_close(quote: str, name: str, role: str,
                cta: str = 'Más en estacionline.com →',
                eyebrow: str = None, title: str = None,
                credit: str = None) -> str:
    """Layout 6: cierre — cita con barra + atribución + botón CTA claro.

    eyebrow/title son opcionales (para cierres con frase propia además de
    la cita). Sin "Deslizá" — es la última slide.
    """
    P = _pal()
    eyebrow_html = f'<div class="eyebrow">{eyebrow}</div>' if eyebrow else ''
    title_html = f'<h1 class="close-title">{title}</h1>' if title else ''
    css = _bg_glow() + f"""
.close-wrap {{ position: absolute; inset: 0; z-index: 2;
    display: flex; flex-direction: column; justify-content: center;
    padding: 220px 80px 150px 80px; }}
.eyebrow {{ {_EYEBROW} color: {P['LIGHT']}; margin-bottom: 36px; }}
.close-title {{ {_TITLE} margin-bottom: 44px; }}
.close-quote {{ position: relative; padding-left: 36px;
    font-size: 40px; font-weight: 600; line-height: 1.3;
    color: white; letter-spacing: -0.5px; margin-bottom: 30px; max-width: 920px; }}
.close-quote::before {{ content:''; position: absolute; left: 0; top: 8px; bottom: 8px;
    width: 6px; background: {P['GRADIENT']}; border-radius: 4px; }}
.close-attrib {{ font-size: 26px; margin-bottom: 56px; }}
.close-attrib .name {{ font-weight: 700; color: white; }}
.close-attrib .role {{ font-weight: 600; color: rgba(255,255,255,0.6); }}
/* CTA claro con texto oscuro — estética actual */
.cta {{ display: inline-block; align-self: flex-start;
    padding: 24px 44px; background: linear-gradient(135deg, {P['LIGHT']} 0%, {P['PRIMARY']} 100%);
    color: {P['BG_DARK']}; font-size: 26px; font-weight: 800;
    border-radius: 100px; letter-spacing: -0.5px; }}
"""
    body = f"""
  <div class="bg"></div>
  <div class="close-wrap">
    {eyebrow_html}
    {title_html}
    <p class="close-quote">{quote}</p>
    <div class="close-attrib"><span class="name">{name}</span>
      <span class="role"> · {role}</span></div>
    <div class="cta">{cta}</div>
  </div>"""
    return _doc(css, body, swipe=False, credit=credit)

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
