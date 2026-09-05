#!/usr/bin/env python3
"""Simula la banda de texto sobre los encuadres 4:5 posibles de una foto.
PASO OBLIGATORIO antes de renderizar cualquier portada.

  python3 simular_encuadre.py foto.jpg            -> prueba varios object-position
  python3 simular_encuadre.py foto.jpg --extender -> extiende el lienzo hacia abajo
"""
import sys
from PIL import Image, ImageDraw, ImageFilter

def simular(ruta, salida='/tmp/encuadres.png'):
    im = Image.open(ruta).convert('RGB'); W, H = im.size
    if W / H <= 0.8:                      # más alta que 4:5 -> se recorta alto
        th = int(round(W / 0.8)); y0 = max(0, (H - th) // 2)
        c = im.crop((0, y0, W, y0 + th)).resize((432, 540))
        d = ImageDraw.Draw(c, 'RGBA'); d.rectangle([0, 276, 432, 540], fill=(0, 0, 0, 150))
        c.save(salida); print('foto más alta que 4:5, recorte vertical ->', salida); return
    win = int(round(H * 0.8)); out = []
    for pct in [0, 25, 50, 75, 100]:
        x = int((W - win) * pct / 100)
        c = im.crop((x, 0, x + win, H)).resize((432, 540))
        d = ImageDraw.Draw(c, 'RGBA')
        d.rectangle([0, 276, 432, 540], fill=(0, 0, 0, 150))   # banda de texto: y>=51%
        d.text((8, 8), f'{pct}%', fill=(255, 255, 0)); out.append(c)
    s = Image.new('RGB', (432 * 5, 540), 'black')
    for i, c in enumerate(out): s.paste(c, (i * 432, 0))
    s.save(salida); print('object-position 0/25/50/75/100% ->', salida)

def extender(ruta, x0=0, ancho=None, salida='portada_extendida.jpg'):
    """Extiende el lienzo hacia abajo espejando y desenfocando el borde inferior.
    Se usa cuando la foto es más ANCHA que 4:5 y el sujeto queda sobre la banda."""
    im = Image.open(ruta).convert('RGB'); W, H = im.size
    ancho = ancho or W
    base = im.crop((x0, 0, x0 + ancho, H))
    bw, bh = base.size; th = int(round(bw / 0.8)); ext = th - bh
    if ext <= 0: base.save(salida); print('no hace falta extender'); return
    tail = base.crop((0, bh - ext, bw, bh)).transpose(Image.FLIP_TOP_BOTTOM)
    tail = tail.filter(ImageFilter.GaussianBlur(18))
    tail = Image.blend(tail, Image.new('RGB', tail.size, (0, 0, 0)), 0.5)
    c = Image.new('RGB', (bw, th)); c.paste(base, (0, 0)); c.paste(tail, (0, bh))
    blend = 110
    st = base.crop((0, bh - blend, bw, bh)); sb = c.crop((0, bh, bw, bh + blend))
    m = Image.new('L', (bw, blend)); dm = ImageDraw.Draw(m)
    for y in range(blend): dm.line([(0, y), (bw, y)], fill=int(255 * y / blend))
    c.paste(Image.composite(sb, st, m), (0, bh - blend // 2))
    c.save(salida, quality=93); print(f'{c.size}, extendido {ext}px ->', salida)

if __name__ == '__main__':
    if '--extender' in sys.argv: extender(sys.argv[1])
    else: simular(sys.argv[1])
