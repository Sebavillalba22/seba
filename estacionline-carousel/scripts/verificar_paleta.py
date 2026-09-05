#!/usr/bin/env python3
"""verificar_paleta.py — gate de paleta.

Existe porque la paleta era la única regla del kit sin verificación
automática, y por eso se arrastraba de la pieza anterior. Hace dos cosas:

  1. Deduce la paleta que corresponde al TEMA, con desempate explícito
     (actor institucional > lugar > rubro), y la contrasta con la elegida.
  2. Lee los slide*.html ya generados y detecta qué paleta quedó realmente
     pintada, para cazar un build heredado de otra pieza.

Uso:
    python3 verificar_paleta.py --tema "Pullaro, Santa Fe Business Forum, comercio exterior en Rosario"
    python3 verificar_paleta.py --tema "..." --paleta atardecer
    python3 verificar_paleta.py --dir /home/claude/PIEZA --paleta atardecer
    python3 verificar_paleta.py --tema "..." --dir /home/claude/PIEZA

Sale con código 1 si algo no cierra.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys
import unicodedata

# Hex de cada paleta — deben coincidir con PALETTES de build_template.py.
# La detección en el HTML usa BG_DARK, no PRIMARY: el gradiente de 5 stops de
# `atardecer` contiene los PRIMARY de rojo, rosa y violáceo, y por PRIMARY
# daba falso positivo. BG_DARK es único por paleta y va en `.slide`.
PRIMARIES = {
    'violaceo':  '#A855F7',
    'verde':     '#A3C616',
    'rosa':      '#EC4899',
    'acero':     '#5B8FB9',
    'atardecer': '#F97316',
    'ocre':      '#D4A53A',
    'rojo':      '#EF4444',
}
BG_DARKS = {
    'violaceo':  '#0F0817',
    'verde':     '#0F1008',
    'rosa':      '#1A0814',
    'acero':     '#0A1220',
    'atardecer': '#1A0510',
    'ocre':      '#14100A',
    'rojo':      '#170707',
}

# Reglas por nivel. El primer nivel que matchea gana: un actor institucional
# provincial manda sobre el lugar donde pasó el hecho, y el lugar sobre el rubro.
NIVELES = [
    ('actor institucional', [
        ('atardecer', ['provincia', 'provincial', 'gobernador', 'gobernadora', 'pullaro',
                       'casa gris', 'gobierno de santa fe', 'ministerio de la provincia',
                       'senado provincial', 'diputados provincial', 'legislatura']),
        ('acero',     ['municipalidad de rosario', 'muni rosario', 'intendente de rosario',
                       'javkin', 'concejo de rosario', 'concejo municipal', 'converge']),
    ]),
    ('lugar', [
        ('verde', ['funes', 'roldan', 'timbues', 'puerto timbues']),
        ('acero', ['rosario']),
    ]),
    ('rubro', [
        ('violaceo',  ['policial', 'policiales', 'crimen', 'narcomenudeo', 'homicidio',
                       'balacera', 'robo', 'asesinato', 'droga']),
        ('rosa',      ['infancia', 'infancias', 'ninez', 'salud', 'genero', 'mujer',
                       'mujeres', 'adultos mayores', 'femicidio', 'violencia de genero']),
        ('atardecer', ['economia', 'economico', 'comercio exterior', 'exportacion',
                       'exportaciones', 'inversion', 'dolar', 'inflacion', 'energia',
                       'crisis', 'paritaria']),
        ('rojo',      ['alerta', 'transito', 'temporal', 'evacuados', 'incendio',
                       'situacional', 'urgente']),
        ('ocre',      ['cultura', 'agenda', 'espectaculo', 'espectaculos', 'musica',
                       'gaming', 'premium', 'gastronomia', 'comercial']),
        ('verde',     ['ambiente', 'residuos', 'reciclado', 'arbolado', 'sustentable']),
    ]),
]


def _norm(s: str) -> str:
    """Minúsculas sin tildes, para que 'Roldán' matchee 'roldan'."""
    s = unicodedata.normalize('NFD', s.lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


def deducir(tema: str, titular: str | None = None) -> tuple[str | None, str, list[str]]:
    """Devuelve (paleta, nivel_que_decidio, motivos).

    Si en un nivel empatan paletas distintas (Pullaro + Javkin en el mismo
    acto, muy común), se desempata por quién es el SUJETO del titular:
    se vuelven a aplicar las reglas de ese nivel sólo sobre `titular`.
    """
    t = _norm(tema)
    tit = _norm(titular) if titular else None
    for nivel, reglas in NIVELES:
        hits = [(pal, kw) for pal, kws in reglas for kw in kws if kw in t]
        if not hits:
            continue
        motivos = [f'"{kw}" → {p}' for p, kw in hits]
        if len({p for p, _ in hits}) == 1:
            return hits[0][0], nivel, motivos
        # Empate en el nivel: el titular decide, si lo hay y no empata también.
        if tit:
            en_titular = [(pal, kw) for pal, kws in reglas for kw in kws if kw in tit]
            if en_titular and len({p for p, _ in en_titular}) == 1:
                motivos.append(f'empate → desempata el titular: "{en_titular[0][1]}"')
                return en_titular[0][0], f'{nivel} (titular)', motivos
        return None, nivel, motivos
    return None, 'ninguno', []


def paleta_en_html(carpeta: str) -> tuple[dict[str, str], list[str]]:
    """Mapea slide -> paleta detectada leyendo el BG_DARK que quedó en el HTML."""
    por_hex = {v.lower(): k for k, v in BG_DARKS.items()}
    detectado, sin_pista = {}, []
    archivos = sorted(glob.glob(os.path.join(carpeta, 'slide*.html')),
                      key=lambda f: int(''.join(c for c in os.path.basename(f) if c.isdigit()) or 0))
    for f in archivos:
        txt = open(f, encoding='utf-8').read()
        encontrados = {por_hex[h.lower()] for h in re.findall(r'#[0-9A-Fa-f]{6}', txt)
                       if h.lower() in por_hex}
        nombre = os.path.basename(f)
        if len(encontrados) == 1:
            detectado[nombre] = encontrados.pop()
        elif encontrados:
            detectado[nombre] = '+'.join(sorted(encontrados))
        else:
            sin_pista.append(nombre)
    return detectado, sin_pista


def main() -> int:
    ap = argparse.ArgumentParser(description='Verifica que la paleta corresponda al tema y al build.')
    ap.add_argument('--tema', help='Titular / resumen / actores de la nota.')
    ap.add_argument('--titular', help='Sólo el título. Desempata cuando dos actores '
                                       'institucionales comparten el acto (Pullaro + Javkin).')
    ap.add_argument('--paleta', help='La paleta elegida para la pieza.')
    ap.add_argument('--dir', help='Carpeta con los slide*.html ya generados.')
    a = ap.parse_args()

    if not (a.tema or a.dir):
        ap.error('pasá al menos --tema o --dir')
    if a.paleta and a.paleta not in PRIMARIES:
        print(f"✗ paleta '{a.paleta}' no existe. Opciones: {' | '.join(PRIMARIES)}")
        return 1

    fallas = []
    sugerida = None

    if a.tema:
        sugerida, nivel, motivos = deducir(a.tema, a.titular)
        print('── tema ' + '─' * 52)
        for m in motivos:
            print(f'   {m}')
        if sugerida:
            print(f'   → decide el nivel "{nivel}": \033[1m{sugerida}\033[0m')
        elif motivos:
            print(f'   ✗ empate dentro del nivel "{nivel}": pasá --titular "..." '
                  f'para desempatar por el sujeto del título, o elegila a mano y justificala')
            fallas.append('tema ambiguo')
        else:
            print('   ? ninguna keyword conocida; elegila a mano')

        if a.paleta and sugerida and a.paleta != sugerida:
            print(f'   ✗ elegiste "{a.paleta}" pero el tema pide "{sugerida}"')
            fallas.append('paleta no coincide con el tema')

    if a.dir:
        detectado, sin_pista = paleta_en_html(a.dir)
        print('── build ' + '─' * 51)
        if not detectado and not sin_pista:
            print(f'   ✗ no hay slide*.html en {a.dir}')
            return 1
        esperada = a.paleta or sugerida
        for slide, pal in detectado.items():
            marca = '✓' if (not esperada or pal == esperada) else '✗'
            print(f'   {marca} {slide}: {pal}')
            if esperada and pal != esperada:
                fallas.append(f'{slide} pintado en {pal}')
        for slide in sin_pista:
            print(f'   ? {slide}: sin BG_DARK reconocible')
        distintas = {p for p in detectado.values()}
        if len(distintas) > 1:
            print(f'   ✗ los slides no comparten paleta: {", ".join(sorted(distintas))}')
            fallas.append('slides con paletas mezcladas')

    print('─' * 60)
    if fallas:
        print('✗ ' + '; '.join(dict.fromkeys(fallas)))
        print('  Recordá: la paleta la manda el TEMA, no la pieza anterior.')
        return 1
    print('✓ paleta consistente')
    return 0


if __name__ == '__main__':
    sys.exit(main())
