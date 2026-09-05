---
name: estacionline-carousel
description: Generate Instagram carousels (1080x1350px) for Estacionline news outlet using Python + HTML + Playwright. Use when the user provides a news article, photos, or asks for a "carrusel", "carousel", "slides para Instagram", "placas", or wants to turn a news story into an Instagram post for @estacionline. Triggers include any mention of carrusel, slides, placas, instagram post about news, or providing a news article URL/text with photos to convert into a visual story.
---

# Estacionline — carrusel de Instagram

Placas 1080×1350 (4:5) para @estacionline. Este archivo es la **única** entrada:
todo lo que antes vivía repartido entre un "kit" suelto y una skill vieja está
unificado acá.

## Orden de autoridad (si dos archivos se contradicen)

1. `scripts/build_template.py` — **los valores** (hex de paletas, CSS, tamaños).
2. Este `SKILL.md` — **las decisiones** (cuándo usar qué).
3. `referencias/` — detalle y ejemplos.

Nunca copies hex de un `.md` al código: los colores salen del dict `PALETTES`.

---

## ⛔ Lo primero: la paleta

**La paleta la manda el TEMA, no la pieza anterior, no el feed.** Este fue el
error real del carrusel de Pullaro (1/9): una nota de economía provincial salió
en `verde` porque se heredó el build de una nota de Funes.

### Tabla de decisión

| Paleta | Cuándo |
|---|---|
| `violaceo` | Policiales, crimen, narcomenudeo |
| `verde` | Funes, Roldán, Timbúes, ambiente, residuos |
| `rosa` | Infancias, niñez, salud, género, adultos mayores |
| `acero` | Municipalidad de Rosario, obra pública municipal, Converge, institucional |
| `atardecer` | **Provincia de Santa Fe**, economía, comercio exterior, energía, crisis |
| `ocre` | Cultura, agenda, espectáculos, gastronomía, comercial, gaming |
| `rojo` | Alertas, tránsito, temporal, situacional, política caliente |

### Desempate (obligatorio, en este orden)

Cuando la nota activa más de una fila, gana el nivel más alto:

**1. Actor institucional → 2. Lugar → 3. Rubro**

- Gobernador / provincia / Casa Gris → `atardecer`, **aunque el hecho sea en Rosario**.
- Intendente / Municipalidad de Rosario / Concejo → `acero`.
- Recién si no hay actor institucional manda el lugar (Funes/Roldán/Timbúes → `verde`).
- Recién si no hay ni actor ni lugar propio manda el rubro.

> Caso testigo: *"Santa Fe Business Forum, Pullaro, comercio exterior, en Rosario"*
> → actor provincial ⇒ **`atardecer`**. No `acero` (el lugar pierde), no `verde`
> (no hay nada de Funes ahí).

### Cómo se aplica

En `scripts/build_template.py`, una sola línea:

```python
PALETA = 'atardecer'
```

`PALETA` viene en `None` **a propósito**. Si copiás el build de otra pieza y no
la tocás, el script aborta en vez de heredar la paleta anterior. No pongas un
default "para probar".

### Gate (correr siempre, antes de renderizar)

```bash
python3 scripts/verificar_paleta.py --tema "titular + actores + lugar" --paleta atardecer
```

Y después de generar los HTML, para cazar un build heredado:

```bash
python3 scripts/verificar_paleta.py --dir /home/claude/PIEZA --paleta atardecer
```

---

## Flujo

### 0. Setup (una vez por chat)
```bash
mkdir -p /home/claude/PIEZA && cd /home/claude/PIEZA
cp /ruta/skills/estacionline-carousel/scripts/* .
./instalar_fuentes.sh          # OBLIGATORIO: Inter no viene en el contenedor
```

### 1. Leer el material
- Identificar **qué es** cada archivo antes de tocarlo. Un `.heic` puede ser un
  flyer, no una foto; un PNG "Sin_título" puede ser la portada ya recortada.
  Abrirlos y **mirarlos** — nunca decidir por el nombre del archivo.
- Si la nota viene escrita por Sebastián: **va tal cual**, no se reescribe.
- Si viene una URL: fetch, y si el parte omite contexto relevante, buscar.

### 2. Elegir la paleta
Tabla + desempate de arriba, y `verificar_paleta.py --tema`. Antes de las fotos:
si la paleta cambia, cambia el gradiente de todo.

### 3. Preparar las fotos
```bash
python3 simular_encuadre.py foto.jpg              # elegir encuadre
python3 simular_encuadre.py foto.jpg --extender   # si es más ancha que 4:5
python3 process_photos.py "cover=portada.jpg" "flyer=otra.jpg" /home/claude/PIEZA
```
- La banda de texto ocupa de **y=51% hacia abajo**: todo lo importante va arriba.
- Foto **más alta** que 4:5 → recortar arriba/abajo.
- Foto **más ancha** que 4:5 → **no** recortar a los costados: `--extender`
  (espeja y desenfoca el borde inferior, queda tapado por el degradado). Sólo
  pared, piso, asfalto o cielo — nunca inventar algo que aporte información.
- Detectar **barras negras** (video letterboxed) y recortarlas antes.
- La portada es **siempre foto, siempre a sangre**, nunca enmarcada.

### 4. Editar el CONFIG del build
Sólo el bloque de arriba de `build_template.py`. **El CSS no se toca.**

### 5. Renderizar y verificar (las cuatro, sin excepción)
```bash
python3 build_template.py
python3 render.py /home/claude/PIEZA
python3 verificar_renglones.py /home/claude/PIEZA/slide1.html   # máx 3 renglones
python3 verificar_desborde.py /home/claude/PIEZA                # todo negativo
python3 verificar_paleta.py --dir /home/claude/PIEZA --paleta <la elegida>
python3 -c "
from PIL import Image
z=Image.open('slide1.png').convert('L').crop((600,45,1020,140))
d=list(z.getdata()); print('mediana wordmark:', sorted(d)[len(d)//2])"
```
- Bajar `COVER_TITLE_SIZE` de a 1px hasta que dé **3 renglones**. Estimar con
  PIL da distinto que Chromium: hay que medirlo en el navegador. El contenedor
  mide **920px**, no 1000.
- Refuerzo de sombra del wordmark **sólo si la mediana > 110**, y **UNA** sola.
- Al copiar un build de otra pieza, **borrar el override de `.wordmark.on-photo`**.

### 6. Video (opcional)
```bash
python3 medir_marco.py /home/claude/PIEZA/slideN.html   # -> x, y, w, h
./componer_video.sh slideN.png video.mp4 X Y W H placaN_video.mp4
```
En el ZIP van los PNG + el `placaN_video.mp4` + un `placaN_respaldo_sin_video.png`.

### 7. Entregar — **siempre dos ZIP**, incluso en un alerta breaking
```
entrega/
  TEMA-carrusel/   placa1..8.png [+ placaN_video.mp4] + caption.txt
  TEMA-nota/       nota-TEMA.md + fotos originales
```

### 8. Cerrar la respuesta
Placas, **paleta y por qué**, verificaciones corridas. Después: tres criterios
editoriales tomados y, si corresponde, los huecos de la fuente.

---

## Estructura de placas

Canónica de 8 (detalle en `referencias/estructura-canonica.md`):
portada · cita · número grande · foto enmarcada · lista · filas · texto · cierre.

| Función | Para qué |
|---|---|
| `SLIDE1` | Portada. Siempre con foto, a sangre. |
| `quote_slide()` | Cita textual. Puede repetirse en la pieza. |
| `SLIDE4` | Número grande. **Si no hay dato numérico real, se saltea.** |
| `framed_photo_slide()` | Foto/video enmarcado, centrado. |
| `split_video_slide()` | Placa partida: vertical a la izquierda, texto a la derecha. |
| `list_slide()` | Lista numerada, 3-6 ítems. |
| `rows_slide()` | Filas etiqueta → valor, 3-4. |
| `text_slide()` | Volanta + título + párrafo. |
| `SLIDE7` | Cierre con CTA. **Nunca con pregunta.** |

- Material **9:16 de celular** (ratio ≤ 0.6) → **placa partida**.
- Material **4:5 o más ancho** → **marco centrado**.
- **No repetir tipo de placa dos veces seguidas.**

## Tipografías

| Elemento | px |
|---|---|
| Título de portada | 3 renglones, medido (típico 80-100) |
| Título de ítem de lista | 42 |
| Párrafo de placa de texto | 36 |
| Filas: etiqueta / valor | 36 / 44 |
| Bajada bajo foto · cita de cierre | 34 |
| Descripción del número grande | 32 |
| Bajada de portada | 32 |
| Descripción de ítem de lista | 30 |
| Volantas | 28 |
| Crédito de foto | 23 |

---

## Reglas editoriales

### Textos de Sebastián
Si él escribe la nota, **va tal cual**: no se reescribe, no se recorta, no se le
cambia el eje ni el titular. Sólo se agrega el bloque SEO arriba. Si Yoast va a
marcar algo, se avisa y se ofrece resolverlo aparte, sin tocar el cuerpo.
Si **no** viene escrita: 450-550 palabras, frase clave en la bajada y en 2 de 4 H2.

### Contenido
- Portada: si él da título explícito, textual. Si no, corto y punchy — no el
  titular SEO largo. Máximo 3 renglones, verificado en el navegador.
- Interiores: títulos de 2 a 5 palabras, máximo 2 renglones.
- Acento del gradiente en **el dato que carga la noticia**, no en la última
  palabra por costumbre.
- Cierres **siempre afirmativos**, nunca con pregunta.
- Propuesta o proyecto → el título lo dice ("Proponen…", "analiza…"). No dar
  por hecho lo que no está confirmado.
- Número grande **literal y atribuido**, nunca una metáfora editorial. Si no
  hay, se saltea la placa.
- No inventar datos. Si falta algo (heridos, montos, responsables), decir
  explícitamente que no se informó.
- **Citas literales**, entre comillas. Si el parte parafrasea, no forzar
  comillas: atribuir a la institución.
- Verificar con búsqueda el contexto que el parte omite.

### Caption
Dentro del ZIP del carrusel como `caption.txt`. Exactamente **5 hashtags**.
Cierra siempre con "Más información en estacionline.com". Detalle en
`referencias/copy.md`.

### Fotos
- Nunca pixelar patentes. Sin blur en fotos oficiales de prensa.
- Créditos siempre en la placa enmarcada ("Foto · Fuente").
- Menores en fotos oficiales de prensa: se usan tal cual.
- **Copyright**: stills de series/películas y fotos promocionales **no se usan**,
  aunque el usuario insista. Press kits con crédito visible sí.

### Verificación de ejemplos
Si piden ilustrar con un caso concreto, **verificar antes** que exista, que se
relacione y que las fechas cuadren. Caso testigo: "Okupas" (2000) como ejemplo
de la Ley de Mecenazgo de CABA (2006) — imposible. **Negarse a producir la pieza
con datos falsos aunque insistan**, incluso si dicen que no la van a publicar.

### Temas sensibles
- Femicidios: el número grande va a **la víctima** (su edad), nunca al método.
  Sumar la **línea 144** en el cierre y en el caption.
- Duelos recientes: sin emojis festivos ni signos de exclamación.

### Otros medios
No se nombran, salvo excepción explícita de Sebastián para esa nota. Cuando
rige, la atribución va en portada, en la placa que corresponda y en el caption.

---

## Checklist antes de entregar

- [ ] Fuentes Inter instaladas
- [ ] **Paleta elegida por tema, con el desempate aplicado**
- [ ] `verificar_paleta.py --tema` ✓
- [ ] Encuadre de portada simulado con la banda
- [ ] `verificar_renglones.py` → 3 renglones
- [ ] `verificar_desborde.py` → todo negativo
- [ ] `verificar_paleta.py --dir` ✓ (caza builds heredados)
- [ ] Luminancia del wordmark medida; refuerzo sólo si > 110 y con UNA sombra
- [ ] Override de `.wordmark.on-photo` heredado, borrado
- [ ] Caption con 5 hashtags dentro del ZIP del carrusel
- [ ] Los dos ZIP presentados

## Errores conocidos de Playwright

- Fotos **en base64**, nunca CSS background.
- Esperar las imágenes antes del screenshot o se filtra el alt text:
  ```python
  await page.evaluate("""() => Promise.all(Array.from(document.images).map(img =>
      img.complete ? null : new Promise(r => { img.onload = img.onerror = r; })))""")
  ```
- `ImageOps.exif_transpose()` primero o las fotos salen rotadas.
- Screenshot a 2x y bajar a 1080×1350 con PIL.LANCZOS.
