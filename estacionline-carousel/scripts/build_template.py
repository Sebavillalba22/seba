"""
build_template.py — EJEMPLO de armado de un carousel con carousel.py.

El diseño NO vive acá: vive en scripts/carousel.py (la librería). Este
archivo solo muestra cómo componer un plan de slides. Copialo, ajustá el
plan a la nota (cantidad, orden y tipos de slide) y completá el contenido.

REGLAS:
- NUNCA escribas HTML/CSS de slides a mano — solo llamadas a c.slide_*().
- Cualquier cantidad de slides vale (3, 5, 7, 10): agregá o quitá llamadas.
- <span class="accent">…</span> aplica el gradiente de la paleta en títulos.
"""
import sys
from pathlib import Path

# Ruta a los scripts de la skill (ajustar si la skill vive en otro lado)
sys.path.insert(0, str(Path(__file__).parent))
import carousel as c

WORK_DIR = '/home/claude/my_carrusel'

# Paleta: violaceo | verde | rosa | acero | atardecer | ocre
c.use_palette('violaceo')

# Fotos procesadas con process_photos.py (paths a los *_b64.txt)
FOTO_COVER = c.photo(f'{WORK_DIR}/cover_b64.txt')
FOTO_SLIDE3 = c.photo(f'{WORK_DIR}/slide3_b64.txt')
FOTO_SLIDE5 = c.photo(f'{WORK_DIR}/slide5_b64.txt')

# Plan de slides — típico de 7, pero usá las que pida la nota
slides = [
    c.slide_cover(
        FOTO_COVER,
        eyebrow='Sección de la nota',
        title='Título principal,<br><span class="accent">en dos líneas</span>.',
        sub='Subtítulo que resume la nota en una oración.',
        obj_pos='center 30%',
    ),
    c.slide_quote(
        text='"Cita textual del protagonista <span class="accent">con énfasis</span>."',
        name='Nombre Apellido',
        role='Cargo o descripción',
    ),
    c.slide_photo_text(
        FOTO_SLIDE3,
        eyebrow='El comienzo',
        title='Título <span class="accent">corto</span> y potente.',
        bajada='Bajada que da contexto sobre lo que muestra la foto.',
        obj_pos='center 25%',      # ajustar para mostrar la cara del sujeto
        text_pos='bottom',         # 'top' si la cara está en la mitad inferior
    ),
    c.slide_number(
        eyebrow='Los números',
        number='53',               # LITERAL de la nota — nunca inventado
        unit='unidades',
        desc='Descripción del número con contexto.',
    ),
    c.slide_photo_text(
        FOTO_SLIDE5,
        eyebrow='El detalle',
        title='Otro título <span class="accent">destacado</span>.',
        bajada='Bajada de la segunda foto.',
    ),
    c.slide_list(
        eyebrow='Distribución',
        title='Lista <span class="accent">por categoría</span>.',
        items=[
            ('Primer ítem', 'Descripción del primer ítem.'),
            ('Segundo ítem', 'Descripción del segundo ítem.'),
            ('Tercer ítem', 'Descripción del tercer ítem.'),
        ],
        style='numbered',          # 'check' para lista de requisitos con ✓
    ),
    c.slide_close(
        eyebrow='El compromiso',
        title='Cita o frase <span class="accent">final</span>.',
        quote='Cita que cierra la historia.',
        cta='Leé la nota completa →',
    ),
]

if __name__ == '__main__':
    c.write_slides(WORK_DIR, slides)
