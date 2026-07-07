#!/usr/bin/env python3
"""Auditar la INDEXABILIDAD real de una lista de URLs (sin API de Google).

Descarga el HTML de cada URL (como lo vería Googlebot) y detecta el motivo
más probable por el que NO se indexa, replicando los estados del informe
"Indexación de páginas" de Search Console:

  - Error de red / servidor (5xx)         -> revisar hosting
  - No encontrada (4xx / 404 / 410)       -> URL rota o borrada
  - Página con redirección (3xx)          -> "Página con redirección"
  - Bloqueada por robots.txt              -> "Bloqueada por robots.txt"
  - Excluida por noindex                  -> meta robots / X-Robots-Tag
  - Canónica apunta a OTRA URL            -> "Alternativa / Duplicada"
  - Contenido escaso                      -> probable "Rastreada: sin indexar"
  - Indexable ✔                           -> pedir indexación / esperar rastreo

Además chequea title, meta description, H1, lang, datos estructurados
(JSON-LD Article/NewsArticle) y, si se pasa un sitemap, si la URL figura
en él (descubribilidad).

Solo usa la librería estándar de Python 3. No necesita credenciales.

Uso:
  # auditar URLs de un archivo (una por línea, admite comentarios con #)
  audit_urls.py --file urls.txt

  # auditar directamente un sitemap (expande sitemaps anidados)
  audit_urls.py --sitemap https://estacionline.com/sitemap.xml --limit 200

  # auditar URLs sueltas y cruzarlas contra el sitemap
  audit_urls.py https://estacionline.com/nota-1/ https://estacionline.com/nota-2/ \
      --sitemap https://estacionline.com/sitemap.xml

  # guardar el detalle en JSON
  audit_urls.py --file urls.txt --json reporte.json

Opciones útiles:
  --limit N          máximo de URLs a auditar (por defecto 100)
  --min-words N      umbral de "contenido escaso" (por defecto 250)
  --ua "..."         User-Agent a usar (por defecto uno de Chrome)
  --header "K: V"    cabecera extra (repetible; p. ej. para pasar un WAF)
  --timeout S        timeout por request (por defecto 25s)
  --delay S          pausa entre requests para no golpear el server (0.5s)
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
REDIRECT_CODES = {301, 302, 303, 307, 308}


def _die(msg: str):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


# --------------------------------------------------------------------------- #
#  Descarga con seguimiento manual de redirecciones                           #
# --------------------------------------------------------------------------- #
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """No seguir redirecciones automáticamente: las manejamos a mano para
    poder registrar la cadena completa y el status de cada salto."""

    def redirect_request(self, *args, **kwargs):  # noqa: D401
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def fetch(url: str, headers: dict, timeout: float, max_redirects: int = 10) -> dict:
    """Devuelve dict con status final, url final, headers, body y cadena de
    redirecciones. Nunca lanza: los errores quedan en result['error']."""
    chain: list[tuple[str, int, str | None]] = []
    current = url
    for _ in range(max_redirects + 1):
        req = urllib.request.Request(current, headers=headers, method="GET")
        try:
            resp = _OPENER.open(req, timeout=timeout)
            status = resp.getcode()
            hdrs = resp.headers
            body = resp.read()
            if (hdrs.get("Content-Encoding") or "").lower() == "gzip":
                try:
                    body = gzip.decompress(body)
                except OSError:
                    pass
            return {
                "status": status,
                "final_url": current,
                "headers": hdrs,
                "body": body,
                "chain": chain,
                "error": None,
            }
        except urllib.error.HTTPError as e:
            status = e.code
            hdrs = e.headers
            if status in REDIRECT_CODES:
                loc = hdrs.get("Location")
                chain.append((current, status, loc))
                if not loc:
                    return {"status": status, "final_url": current, "headers": hdrs,
                            "body": b"", "chain": chain, "error": "redirect sin Location"}
                current = urllib.parse.urljoin(current, loc)
                continue
            return {"status": status, "final_url": current, "headers": hdrs,
                    "body": b"", "chain": chain, "error": None}
        except (urllib.error.URLError, TimeoutError) as e:
            return {"status": None, "final_url": current, "headers": None,
                    "body": b"", "chain": chain, "error": str(getattr(e, "reason", e))}
        except Exception as e:  # noqa: BLE001 — no romper la corrida por una URL
            return {"status": None, "final_url": current, "headers": None,
                    "body": b"", "chain": chain, "error": str(e)}
    return {"status": None, "final_url": current, "headers": None, "body": b"",
            "chain": chain, "error": f"demasiadas redirecciones (>{max_redirects})"}


# --------------------------------------------------------------------------- #
#  Parser de HTML (solo <head> + conteo de texto)                             #
# --------------------------------------------------------------------------- #
class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title: str | None = None
        self.metas: list[dict] = []
        self.links: list[dict] = []
        self.lang: str | None = None
        self.h1 = 0
        self.jsonld: list[str] = []
        self.words = 0
        self._in_title = False
        self._in_ld = False
        self._ld_buf: list[str] = []
        self._skip = False  # dentro de <script>/<style> no-LD

    def handle_starttag(self, tag, attrs):
        d = {k.lower(): (v or "") for k, v in attrs}
        if tag == "title":
            self._in_title = True
            if self.title is None:
                self.title = ""
        elif tag == "meta":
            self.metas.append(d)
        elif tag == "link":
            self.links.append(d)
        elif tag == "html":
            self.lang = d.get("lang")
        elif tag == "h1":
            self.h1 += 1
        elif tag == "script":
            if d.get("type", "").lower() == "application/ld+json":
                self._in_ld = True
                self._ld_buf = []
            else:
                self._skip = True
        elif tag == "style":
            self._skip = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "script":
            if self._in_ld:
                self.jsonld.append("".join(self._ld_buf))
                self._in_ld = False
            self._skip = False
        elif tag == "style":
            self._skip = False

    def handle_data(self, data):
        if self._in_title:
            self.title = (self.title or "") + data
        elif self._in_ld:
            self._ld_buf.append(data)
        elif not self._skip:
            self.words += len(data.split())


# --------------------------------------------------------------------------- #
#  robots.txt (matcher mínimo estilo Google)                                  #
# --------------------------------------------------------------------------- #
class RobotsRules:
    def __init__(self):
        self.rules: list[tuple[bool, str]] = []  # (allow?, path_pattern)
        self.sitemaps: list[str] = []
        self.ok = False

    @staticmethod
    def _to_regex(pattern: str) -> re.Pattern:
        # convierte comodines de robots (* y $) a regex
        out = ["^"]
        for ch in pattern:
            if ch == "*":
                out.append(".*")
            elif ch == "$":
                out.append("$")
            else:
                out.append(re.escape(ch))
        return re.compile("".join(out))

    def allows(self, path: str) -> bool:
        if not self.ok or not self.rules:
            return True
        best_len = -1
        best_allow = True
        for allow, pat in self.rules:
            if pat == "":
                continue
            m = self._to_regex(pat).match(path)
            if m:
                length = len(pat)
                if length > best_len:
                    best_len = length
                    best_allow = allow
        return best_allow


def load_robots(base: str, headers: dict, timeout: float) -> RobotsRules:
    rr = RobotsRules()
    url = urllib.parse.urljoin(base, "/robots.txt")
    r = fetch(url, headers, timeout)
    if r["status"] != 200 or not r["body"]:
        return rr
    rr.ok = True
    text = r["body"].decode("utf-8", "replace")
    applies = False  # ¿el grupo actual aplica a * o googlebot?
    current_agents: list[str] = []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field, _, value = line.partition(":")
        field = field.strip().lower()
        value = value.strip()
        if field == "user-agent":
            current_agents = [value.lower()]
            applies = value == "*" or "googlebot" in value.lower()
        elif field == "sitemap":
            rr.sitemaps.append(value)
        elif field in ("disallow", "allow") and applies:
            rr.rules.append((field == "allow", value))
    return rr


# --------------------------------------------------------------------------- #
#  Normalización de URLs y análisis de una página                             #
# --------------------------------------------------------------------------- #
def norm_url(u: str) -> str:
    if not u:
        return ""
    p = urllib.parse.urlsplit(u.strip())
    scheme = (p.scheme or "https").lower()
    host = p.netloc.lower()
    if host.endswith(":80"):
        host = host[:-3]
    if host.endswith(":443"):
        host = host[:-4]
    path = p.path or "/"
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    return urllib.parse.urlunsplit((scheme, host, path, p.query, ""))


def analyze(url: str, sitemap_set: set[str], robots: RobotsRules,
            headers: dict, timeout: float, min_words: int) -> dict:
    r = fetch(url, headers, timeout)
    out: dict = {
        "url": url,
        "final_url": r["final_url"],
        "status": r["status"],
        "verdict": "",
        "reason": "",
        "action": "",
        "signals": {},
        "redirect_chain": [f"{s} → {loc}" for (_, s, loc) in r["chain"]],
    }
    sig = out["signals"]

    # X-Robots-Tag de las cabeceras
    xrobots = ""
    if r["headers"] is not None:
        xrobots = (r["headers"].get("X-Robots-Tag") or "").lower()
    sig["x_robots_tag"] = xrobots or None

    # errores de red / status
    if r["error"] and r["status"] is None:
        out["verdict"] = "ERROR_RED"
        out["reason"] = f"No se pudo descargar: {r['error']}"
        out["action"] = "Revisar DNS/hosting/firewall del sitio."
        return out
    if r["status"] and r["status"] >= 500:
        out["verdict"] = "ERROR_SERVIDOR"
        out["reason"] = f"El servidor respondió {r['status']} (5xx)."
        out["action"] = "Error del servidor: revisar el hosting/WordPress."
        return out
    if r["status"] in (404, 410):
        out["verdict"] = "NO_ENCONTRADA"
        out["reason"] = f"La URL devuelve {r['status']}."
        out["action"] = "URL rota o eliminada: restaurar el contenido o redirigir 301."
        return out
    if r["status"] and 400 <= r["status"] < 500:
        out["verdict"] = "ERROR_CLIENTE"
        out["reason"] = f"La URL devuelve {r['status']} (posible bloqueo/WAF)."
        out["action"] = "Revisar permisos/WAF; Googlebot debe poder acceder."
        return out
    if r["chain"]:
        out["verdict"] = "REDIRIGE"
        out["reason"] = "La URL redirige a otra (Search Console: 'Página con redirección')."
        out["action"] = ("Indexá la URL de destino, no esta. Si no debería "
                          "redirigir, corregí el redirect.")
        return out

    # robots.txt
    path = urllib.parse.urlsplit(r["final_url"]).path or "/"
    if not robots.allows(path):
        out["verdict"] = "BLOQUEADA_ROBOTS"
        out["reason"] = "robots.txt no permite rastrear esta ruta."
        out["action"] = "Quitar la regla Disallow que la bloquea en robots.txt."
        return out

    # parsear HTML
    ctype = ""
    if r["headers"] is not None:
        ctype = (r["headers"].get("Content-Type") or "").lower()
    if "html" not in ctype and r["body"][:200].lower().find(b"<html") == -1:
        out["verdict"] = "NO_HTML"
        out["reason"] = f"Content-Type '{ctype or '?'}' no es HTML."
        out["action"] = "Verificar que la URL sirva una página HTML."
        return out

    parser = PageParser()
    try:
        parser.feed(r["body"].decode("utf-8", "replace"))
    except Exception:  # noqa: BLE001
        pass

    # meta robots (todos los meta name=robots|googlebot)
    robots_meta = ""
    for m in parser.metas:
        name = (m.get("name") or "").lower()
        if name in ("robots", "googlebot"):
            robots_meta += " " + (m.get("content") or "").lower()
    sig["meta_robots"] = robots_meta.strip() or None

    # canonical
    canonical = None
    for lk in parser.links:
        if (lk.get("rel") or "").lower() == "canonical":
            canonical = lk.get("href")
            break
    sig["canonical"] = canonical
    sig["title"] = (parser.title or "").strip() or None
    sig["title_len"] = len((parser.title or "").strip())
    desc = None
    for m in parser.metas:
        if (m.get("name") or "").lower() == "description":
            desc = m.get("content")
            break
    sig["meta_description"] = bool(desc)
    sig["h1_count"] = parser.h1
    sig["lang"] = parser.lang
    sig["words"] = parser.words
    sig["in_sitemap"] = (norm_url(url) in sitemap_set) if sitemap_set else None
    # datos estructurados Article/NewsArticle
    has_article = False
    for blob in parser.jsonld:
        low = blob.lower()
        if "article" in low and "@type" in low:
            has_article = True
            break
    sig["structured_article"] = has_article

    # noindex (meta o cabecera)
    if "noindex" in robots_meta or "noindex" in xrobots:
        out["verdict"] = "NOINDEX"
        out["reason"] = "La página declara noindex (meta robots o X-Robots-Tag)."
        out["action"] = ("Quitar el noindex. En Yoast/RankMath: activar "
                         "'Mostrar en resultados de búsqueda' para esa entrada/tipo.")
        return out

    # canónica hacia otra URL
    if canonical:
        if norm_url(canonical) != norm_url(url):
            out["verdict"] = "CANONICAL_OTRA"
            out["reason"] = (f"La canónica apunta a otra URL: {canonical} "
                             "(Search Console: 'Alternativa con canónica' / 'Duplicada').")
            out["action"] = ("Si esta URL debería indexarse, corregí la canónica "
                             "para que apunte a sí misma. Si es un duplicado real, "
                             "está bien: indexá la canónica.")
            return out
    else:
        sig["canonical"] = "(falta)"

    # contenido escaso -> probable "Rastreada/Detectada: actualmente sin indexar"
    if parser.words < min_words:
        out["verdict"] = "CONTENIDO_ESCASO"
        out["reason"] = (f"Solo ~{parser.words} palabras (< {min_words}). "
                         "Causa típica de 'Rastreada: actualmente sin indexar'.")
        out["action"] = ("Ampliar/enriquecer el contenido, sumar enlaces internos "
                         "desde notas relevantes y pedir indexación.")
        return out

    # indexable
    out["verdict"] = "INDEXABLE"
    reason = "Técnicamente indexable."
    if sig["in_sitemap"] is False:
        reason += " OJO: no está en el sitemap."
    out["reason"] = reason
    out["action"] = ("Reforzar enlazado interno + pedir indexación (URL Inspection "
                     "→ Solicitar indexación). Si ya se pidió, esperar el recrawl.")
    return out


# --------------------------------------------------------------------------- #
#  Sitemap (para el cruce de descubribilidad)                                 #
# --------------------------------------------------------------------------- #
def expand_sitemap(url: str, headers: dict, timeout: float, seen=None) -> list[str]:
    if seen is None:
        seen = set()
    if url in seen:
        return []
    seen.add(url)
    r = fetch(url, headers, timeout)
    if r["status"] != 200 or not r["body"]:
        return []
    body = r["body"]
    if url.endswith(".gz") or body[:2] == b"\x1f\x8b":
        try:
            body = gzip.decompress(body)
        except OSError:
            pass
    text = body.decode("utf-8", "replace")
    locs = re.findall(r"<loc>\s*(.*?)\s*</loc>", text, re.I | re.S)
    if "<sitemapindex" in text.lower():
        urls: list[str] = []
        for sm in locs:
            urls.extend(expand_sitemap(sm.strip(), headers, timeout, seen))
        return urls
    return [u.strip() for u in locs]


# --------------------------------------------------------------------------- #
#  Reporte                                                                     #
# --------------------------------------------------------------------------- #
VERDICT_LABEL = {
    "ERROR_RED": "❌ Error de red",
    "ERROR_SERVIDOR": "❌ Error de servidor (5xx)",
    "ERROR_CLIENTE": "❌ Error de cliente (4xx)",
    "NO_ENCONTRADA": "❌ No encontrada (404/410)",
    "NO_HTML": "❌ No es HTML",
    "REDIRIGE": "↪️  Página con redirección",
    "BLOQUEADA_ROBOTS": "🚫 Bloqueada por robots.txt",
    "NOINDEX": "🚫 Excluida por noindex",
    "CANONICAL_OTRA": "🔁 Canónica a otra URL (alternativa/duplicada)",
    "CONTENIDO_ESCASO": "⚠️  Contenido escaso (probable 'sin indexar')",
    "INDEXABLE": "✅ Indexable",
}
PRIORITY = ["NOINDEX", "BLOQUEADA_ROBOTS", "CANONICAL_OTRA", "REDIRIGE",
            "NO_ENCONTRADA", "ERROR_SERVIDOR", "ERROR_CLIENTE", "ERROR_RED",
            "NO_HTML", "CONTENIDO_ESCASO", "INDEXABLE"]


def print_report(results: list[dict], min_words: int):
    groups: dict[str, list[dict]] = {}
    for res in results:
        groups.setdefault(res["verdict"], []).append(res)

    print("\n" + "=" * 68)
    print(f"  AUDITORÍA DE INDEXABILIDAD — {len(results)} URL(s)")
    print("=" * 68)
    for v in PRIORITY:
        if v not in groups:
            continue
        items = groups[v]
        print(f"\n{VERDICT_LABEL.get(v, v)}  —  {len(items)} URL(s)")
        print("-" * 68)
        for res in items:
            print(f"  {res['url']}")
            print(f"     · {res['reason']}")
            if res["action"]:
                print(f"     → {res['action']}")
            sig = res.get("signals", {})
            extra = []
            if sig.get("title_len") is not None and sig.get("title_len", 0) == 0:
                extra.append("sin <title>")
            if sig.get("meta_description") is False:
                extra.append("sin meta description")
            if sig.get("h1_count") == 0:
                extra.append("sin H1")
            if sig.get("in_sitemap") is False:
                extra.append("NO en sitemap")
            if sig.get("structured_article") is False and v == "INDEXABLE":
                extra.append("sin datos estructurados Article")
            if extra:
                print(f"     ⚑ {', '.join(extra)}")

    # resumen final
    print("\n" + "=" * 68)
    print("  RESUMEN")
    print("=" * 68)
    for v in PRIORITY:
        if v in groups:
            print(f"  {len(groups[v]):>3}  {VERDICT_LABEL.get(v, v)}")
    indexables = [r["url"] for r in results if r["verdict"] == "INDEXABLE"]
    if indexables:
        print("\n  ✅ LISTAS PARA PEDIR INDEXACIÓN (URL Inspection → Solicitar):")
        for u in indexables:
            print(f"     {u}")
    tofix = [r for r in results if r["verdict"] not in ("INDEXABLE",)]
    if tofix:
        print("\n  🔧 REQUIEREN ARREGLO ANTES DE INDEXAR:")
        for r in tofix:
            print(f"     [{VERDICT_LABEL.get(r['verdict'], r['verdict'])}] {r['url']}")
    print()


def read_url_file(path: str) -> list[str]:
    urls = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.split("#", 1)[0].strip()
                if line:
                    urls.append(line)
    except OSError as e:
        _die(f"no se pudo leer {path}: {e}")
    return urls


def main():
    ap = argparse.ArgumentParser(description="Auditar indexabilidad de URLs (sin API de Google).")
    ap.add_argument("urls", nargs="*", help="URLs sueltas a auditar")
    ap.add_argument("--file", help="archivo con una URL por línea")
    ap.add_argument("--sitemap", help="sitemap a auditar y/o cruzar")
    ap.add_argument("--limit", type=int, default=100, help="máximo de URLs (def. 100)")
    ap.add_argument("--min-words", type=int, default=250, help="umbral contenido escaso (def. 250)")
    ap.add_argument("--ua", default=DEFAULT_UA, help="User-Agent")
    ap.add_argument("--header", action="append", default=[], help="cabecera extra 'K: V' (repetible)")
    ap.add_argument("--timeout", type=float, default=25.0)
    ap.add_argument("--delay", type=float, default=0.5, help="pausa entre requests (def. 0.5s)")
    ap.add_argument("--json", dest="json_out", help="guardar detalle en JSON")
    ap.add_argument("--no-robots", action="store_true", help="no chequear robots.txt")
    args = ap.parse_args()

    headers = {"User-Agent": args.ua, "Accept": "text/html,application/xhtml+xml"}
    for h in args.header:
        if ":" in h:
            k, _, v = h.partition(":")
            headers[k.strip()] = v.strip()

    urls: list[str] = list(args.urls)
    if args.file:
        urls += read_url_file(args.file)

    sitemap_urls: list[str] = []
    if args.sitemap:
        print(f"Leyendo sitemap: {args.sitemap} ...", file=sys.stderr)
        sitemap_urls = expand_sitemap(args.sitemap, headers, args.timeout)
        print(f"  → {len(sitemap_urls)} URLs en el sitemap.", file=sys.stderr)
        if not urls:  # sin lista propia: auditar el sitemap
            urls = sitemap_urls

    # dedup preservando orden
    seen = set()
    urls = [u for u in urls if not (u in seen or seen.add(u))]
    if not urls:
        _die("no hay URLs para auditar (usá --file, --sitemap o pasá URLs).")
    if len(urls) > args.limit:
        print(f"Limitando a {args.limit} de {len(urls)} URLs (subí --limit para más).",
              file=sys.stderr)
        urls = urls[: args.limit]

    sitemap_set = {norm_url(u) for u in sitemap_urls}

    robots = RobotsRules()
    if not args.no_robots and urls:
        base = "{0.scheme}://{0.netloc}".format(urllib.parse.urlsplit(urls[0]))
        robots = load_robots(base, headers, args.timeout)

    results = []
    for i, u in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {u}", file=sys.stderr)
        results.append(analyze(u, sitemap_set, robots, headers, args.timeout, args.min_words))
        if args.delay and i < len(urls):
            time.sleep(args.delay)

    print_report(results, args.min_words)

    if args.json_out:
        # los headers de urllib no serializan: quitarlos
        clean = []
        for r in results:
            r2 = {k: v for k, v in r.items()}
            clean.append(r2)
        try:
            with open(args.json_out, "w", encoding="utf-8") as f:
                json.dump(clean, f, ensure_ascii=False, indent=2)
            print(f"Detalle guardado en {args.json_out}", file=sys.stderr)
        except OSError as e:
            _die(f"no se pudo escribir {args.json_out}: {e}")


if __name__ == "__main__":
    main()
