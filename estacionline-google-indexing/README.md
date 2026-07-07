# estacionline-google-indexing

Herramientas + plan de acción para lograr que las notas de **estacionline.com**
indexen en Google, trabajando sobre **Google Search Console**. Python **stdlib**,
sin dependencias.

## Qué hace

- **Sin API (cero setup):** `audit_urls.py` descarga el HTML de cada URL y te
  dice por qué probablemente no indexa (noindex, canónica a otra, redirect,
  404/5xx, robots.txt, contenido escaso) + `sitemap_tools.py` para sitemaps.
- **Con API (OAuth de Search Console):** `gsc_inspect.py` te da el estado
  **real** por URL (el mismo del inspector, en lote); `gsc_sitemaps.py`
  lista/envía sitemaps; `gsc_performance.py` muestra clics/impresiones.

## Empezar

```bash
# 1) Sin nada de setup — primera pasada:
python3 scripts/audit_urls.py --sitemap https://estacionline.com/sitemap.xml --limit 100

# 2) Con API (una vez): seguí SETUP-OAUTH.txt y después:
python3 scripts/gsc_auth.py
python3 scripts/gsc_inspect.py --file urls.txt
```

## Realidad sobre la indexación

- No hay API que **garantice** indexar. La **Indexing API** de Google solo
  vale para `JobPosting`/`BroadcastEvent`, no para notas — por eso no está.
- **"Solicitar indexación"** es siempre manual (Search Console → Inspección
  de URLs). Cupo ~10/día.
- Palancas reales: arreglar lo técnico, contenido con sustancia, enlazado
  interno, sitemap fresco (+ sitemap de noticias con `dateModified`).

Ver **`SKILL.md`** para el flujo completo y la tabla *motivo → arreglo* en
WordPress, y **`SETUP-OAUTH.txt`** para crear las credenciales.
