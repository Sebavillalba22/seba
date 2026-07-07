---
name: estacionline-google-indexing
description: Diagnóstico y aceleración de la indexación en Google (Search Console) para Estacionline. Triggers cuando el usuario pide "que estas páginas indexen", pasa un drilldown de Search Console, o pregunta por qué una nota no aparece en Google. Audita la indexabilidad real de cada URL (sin API, descargando el HTML), y si hay credenciales OAuth consulta el estado exacto por URL (URL Inspection), reenvía/monitorea sitemaps y mide rendimiento — todo con Python stdlib. Incluye el mapeo motivo→arreglo para WordPress. La Indexing API NO se usa (Google la ignora para notas). El botón "Solicitar indexación" no tiene API: es a mano.
---

# estacionline-google-indexing — Indexación en Google

Herramientas + plan de acción para lograr que las notas de **estacionline.com**
(WordPress) indexen en Google. Todo en **Python stdlib**, sin dependencias.

## ⚠️ Expectativa realista (leer primero)

- **No existe ningún botón/API que garantice indexación.** Google decide.
- La **Indexing API** de Google solo funciona para `JobPosting` y
  `BroadcastEvent`; para notas/artículos **Google ignora esos pings**
  (reconfirmado 2025). Por eso **no** está en esta skill.
- El botón **"Solicitar indexación"** del inspector de URLs **no tiene API**:
  siempre es manual, y tiene cupo (~10-12 URLs/día útiles).
- Lo que **sí** mueve la aguja: arreglar causas técnicas (noindex, canónica,
  robots, redirects), **contenido con sustancia**, **enlazado interno**,
  **sitemap fresco** (y sitemap de noticias con `dateModified` en el schema),
  y pedir indexación a mano para las prioritarias.

## Dos modos

### A) Sin API (cero setup) — `audit_urls.py`
Descarga el HTML de cada URL y detecta el motivo probable por el que no
indexa (noindex, canónica a otra, redirect, 404/5xx, robots, contenido
escaso). No necesita credenciales. Es la **primera pasada**.

```bash
# auditar una lista (una URL por línea)
python3 scripts/audit_urls.py --file urls.txt

# auditar el sitemap entero y cruzar descubribilidad
python3 scripts/audit_urls.py --sitemap https://estacionline.com/sitemap.xml --limit 200
```
Herramienta de apoyo (sin API): `sitemap_tools.py` — expande sitemaps,
lista URLs, y encuentra las que faltan en el sitemap.

### B) Con API de Search Console (OAuth) — el diagnóstico autoritativo
Consulta a Google el estado real de cada URL. Reemplaza adivinar el
`item_key` del drilldown: te dice, URL por URL, el `coverageState` exacto
("Rastreada: actualmente sin indexar", etc.), la canónica que **eligió
Google**, la última fecha de rastreo y más.

Setup una vez (ver `SETUP-OAUTH.txt`, ~10-15 min):
```bash
python3 scripts/gsc_auth.py            # OAuth con tu cuenta (loopback)
```
Después:
```bash
python3 scripts/gsc_inspect.py --file urls.txt              # estado real por URL
python3 scripts/gsc_sitemaps.py --list                      # sitemaps + estado
python3 scripts/gsc_sitemaps.py --submit https://estacionline.com/sitemap.xml
python3 scripts/gsc_performance.py --by query --days 28     # qué trae tráfico
python3 scripts/gsc_performance.py --by page  --days 28     # qué páginas rinden
```

## Flujo recomendado (paso a paso)

1. **Conseguir la lista de URLs afectadas.** En el drilldown de Search
   Console → botón **Exportar** (o copiar). Guardala en `urls.txt` (una por
   línea). Si no la tenés, arrancá del sitemap con `sitemap_tools.py --list`.
2. **Primera pasada sin API:** `audit_urls.py --file urls.txt`. Resuelve al
   toque lo técnico evidente (noindex, canónica, redirect, 404, robots).
3. **Diagnóstico autoritativo (si hay OAuth):** `gsc_inspect.py --file
   urls.txt`. Confirma el motivo real de Google por URL.
4. **Arreglar según el motivo** (tabla de abajo) en WordPress.
5. **Sitemap:** confirmá que las URLs están en el sitemap
   (`sitemap_tools.py --diff`) y **reenvialo** (`gsc_sitemaps.py --submit`).
6. **Pedir indexación a mano** para las prioritarias: Search Console →
   Inspección de URLs → pegar URL → **Solicitar indexación** (máx ~10/día).
7. **Esperar y re-inspeccionar** a los días con `gsc_inspect.py`. La
   indexación de contenido "flojo" puede tardar semanas o no ocurrir.

## Motivo de Search Console → causa → arreglo (WordPress)

| Motivo (coverageState)                                   | Causa típica                                   | Arreglo |
|----------------------------------------------------------|------------------------------------------------|---------|
| **Excluida por 'noindex'**                               | meta robots / X-Robots-Tag noindex             | Quitar noindex. Yoast/RankMath → "Mostrar en resultados de búsqueda: Sí" para esa entrada y su tipo. |
| **Bloqueada por robots.txt**                             | regla Disallow que tapa la ruta                | Editar robots.txt (Yoast → Herramientas → editor de archivos) y quitar el Disallow. |
| **Página con redirección**                               | la URL hace 301/302 a otra                      | Indexar la URL destino; corregir el redirect si no debía existir. |
| **Alternativa con canónica adecuada / Duplicada**        | la canónica apunta a otra URL                   | Si debe indexar, apuntar la canónica a sí misma. Si es duplicado real (categoría/tag/paginado), está bien: indexá la canónica. |
| **Duplicada: Google eligió otra canónica**               | contenido casi igual a otra URL                 | Diferenciar el contenido o consolidar con 301; alinear canónica + enlaces internos. |
| **Rastreada: actualmente sin indexar**                   | contenido escaso/duplicado, poca autoridad      | Enriquecer la nota, sumar **enlaces internos** desde notas fuertes, mejorar título/entradilla, pedir indexación. |
| **Detectada: actualmente sin indexar**                   | no rastreada aún (crawl budget/descubribilidad) | Meterla en el sitemap, reenviar sitemap, enlazarla desde home/categorías, pedir indexación. |
| **Soft 404**                                             | página "vacía" o sin contenido útil             | Dar contenido real o devolver 404/410 de verdad y redirigir. |
| **No encontrada (404)**                                  | URL rota/borrada                                | Restaurar o 301 a la nota equivalente. |
| **Error de servidor (5xx)**                              | hosting/WordPress caído al rastrear             | Revisar hosting, plugins de caché/seguridad, límites de PHP. |

> Para un medio, sumá el **sitemap de noticias** y el schema `NewsArticle`
> con `datePublished`/`dateModified`. Enviá ese sitemap con
> `gsc_sitemaps.py --submit https://estacionline.com/news-sitemap.xml`.

## Archivos

```
estacionline-google-indexing/
├── SKILL.md                 (este archivo)
├── SETUP-OAUTH.txt          cómo crear el proyecto + OAuth client
├── INSTALL.txt              instalar como skill / usar a mano
├── oauth_client.example.json  formato del JSON de Google Cloud
├── urls.example.txt         formato de la lista de URLs
└── scripts/
    ├── audit_urls.py        (sin API) auditoría de indexabilidad
    ├── sitemap_tools.py     (sin API) expandir/diferenciar sitemaps
    ├── gsc_common.py        OAuth + HTTP compartido (stdlib)
    ├── gsc_auth.py          autorización OAuth (una vez)
    ├── gsc_inspect.py       estado real por URL (URL Inspection API)
    ├── gsc_sitemaps.py      listar/enviar/monitorear sitemaps
    └── gsc_performance.py   clics/impresiones por consulta/página/fecha
```

## Secretos

`oauth_client.json` y `.gsc_token.json` están en `.gitignore`. **Nunca**
commitear credenciales; los `.example` muestran el formato.
