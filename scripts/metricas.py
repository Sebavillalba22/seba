#!/usr/bin/env python3
"""Trae los números reales de Instagram y escribe la memoria de métricas.

Escribe vault/outputs/metricas.md (lo que lee el panel Vitales del HUD),
manteniendo la serie de los últimos 7 valores, y agrega una línea al
histórico en vault/raw/metricas-historial.md.

    python3 scripts/metricas.py --check          # ¿el token sirve?
    python3 scripts/metricas.py                  # jala y escribe
    python3 scripts/metricas.py --manual seguidores=12480 vistas=45200

Credenciales: jarvis-haz-lo-tuyo/instagram.json
    {"username": "...", "ig_user_id": "...", "page_id": "...", "access_token": "..."}
o las variables de entorno IG_USER_ID / IG_ACCESS_TOKEN.

Nunca inventa números: si una fuente falla, conserva el último valor conocido
y deja escrito qué falló. Solo stdlib.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from estado_skills import TZ, ahora, marcar  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
DESTINO = REPO / "vault" / "outputs" / "metricas.md"
HISTORIAL = REPO / "vault" / "raw" / "metricas-historial.md"
CONFIG = REPO / "jarvis-haz-lo-tuyo" / "instagram.json"
API_BASE = "https://graph.facebook.com/v21.0"

# nombre en el .md  ->  clave corta del histórico
METRICAS = [("Seguidores IG", "seguidores"), ("Vistas 7d", "vistas"), ("Interacciones 7d", "interacciones")]


# ── Config y API ────────────────────────────────────────────────────────────
def cargar_config(ruta: Path) -> dict:
    import os

    cfg = {}
    if ruta.exists():
        cfg = json.loads(ruta.read_text(encoding="utf-8"))
    cfg.setdefault("ig_user_id", os.environ.get("IG_USER_ID", ""))
    cfg.setdefault("access_token", os.environ.get("IG_ACCESS_TOKEN", ""))
    if not cfg.get("ig_user_id") or not cfg.get("access_token"):
        raise SystemExit(
            f"Faltan credenciales de Instagram.\n"
            f"  Creá {ruta} con ig_user_id y access_token (mirá instagram.example.json),\n"
            f"  o exportá IG_USER_ID e IG_ACCESS_TOKEN,\n"
            f"  o corré con --manual seguidores=… vistas=… interacciones=…"
        )
    return cfg


def get(api_base: str, path: str, token: str, **params) -> dict:
    params["access_token"] = token
    url = f"{api_base}/{path}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"HTTP {e.code}: {detalle}") from e
    except Exception as e:
        raise RuntimeError(str(e)) from e


def traer(api_base: str, cfg: dict) -> tuple[dict[str, int], dict[str, str]]:
    """Devuelve (valores, notas). Una métrica que falla no aparece en valores."""
    uid, token = cfg["ig_user_id"], cfg["access_token"]
    valores: dict[str, int] = {}
    notas: dict[str, str] = {}
    hoy = ahora()

    try:
        perfil = get(api_base, uid, token, fields="followers_count,media_count")
        valores["seguidores"] = int(perfil["followers_count"])
    except Exception as e:
        notas["seguidores"] = f"no se pudo leer followers_count ({e})"

    # Interacciones: likes + comentarios de los posts de los últimos 7 días.
    try:
        desde = hoy - timedelta(days=7)
        media = get(api_base, f"{uid}/media", token,
                    fields="like_count,comments_count,timestamp", limit=50)
        total = 0
        for post in media.get("data", []):
            ts = post.get("timestamp", "")
            try:
                fecha = datetime.fromisoformat(ts.replace("+0000", "+00:00"))
                if TZ:
                    fecha = fecha.astimezone(TZ)
                else:
                    fecha = fecha.replace(tzinfo=None)
            except ValueError:
                continue
            if fecha >= desde:
                total += int(post.get("like_count", 0)) + int(post.get("comments_count", 0))
        valores["interacciones"] = total
    except Exception as e:
        notas["interacciones"] = f"no se pudieron sumar las interacciones ({e})"

    # Vistas: insights day-by-day de los últimos 7 días. Si la cuenta no
    # habilita "views", se intenta "reach" y se deja constancia de cuál se usó.
    for metrica in ("views", "reach"):
        try:
            ins = get(api_base, f"{uid}/insights", token, metric=metrica, period="day",
                      since=int((hoy - timedelta(days=7)).timestamp()),
                      until=int(hoy.timestamp()))
            datos = ins.get("data", [])
            if not datos:
                raise RuntimeError("respuesta sin datos")
            valores["vistas"] = sum(int(v.get("value", 0)) for v in datos[0].get("values", []))
            if metrica == "reach":
                notas["vistas"] = "medido con reach (la cuenta no habilita views)"
            break
        except Exception as e:
            notas["vistas"] = f"no se pudieron leer las vistas ({e})"

    return valores, notas


# ── Lectura y escritura del .md ─────────────────────────────────────────────
def leer_previo() -> tuple[str, dict[str, list[int]]]:
    """Devuelve (fecha de la última corrida, {nombre: serie7})."""
    if not DESTINO.exists():
        return "", {}
    texto = DESTINO.read_text(encoding="utf-8")
    m = re.search(r"^actualizado:\s*(\S+)", texto, re.M)
    fecha = m.group(1) if m else ""
    series: dict[str, list[int]] = {}
    for bloque in texto.split("\n## ")[1:]:
        nombre = bloque.splitlines()[0].strip()
        s = re.search(r"^serie7:\s*(.+)$", bloque, re.M)
        if s:
            series[nombre] = [int(float(x)) for x in s.group(1).split() if x.strip("-").replace(".", "").isdigit()]
    return fecha, series


def actualizar_serie(previa: list[int], valor: int, mismo_dia: bool) -> list[int]:
    """Corre la serie una posición. Si ya corrió hoy, reemplaza el último valor."""
    serie = list(previa)
    if mismo_dia and serie:
        serie[-1] = valor
    else:
        serie.append(valor)
    return serie[-7:]


def escribir(series: dict[str, list[int]], notas: dict[str, str], momento: datetime) -> None:
    lineas = ["# Métricas Estacionline", f"actualizado: {momento:%Y-%m-%d %H:%M}", ""]
    for nombre, clave in METRICAS:
        serie = series.get(nombre, [])
        if not serie:
            continue
        lineas += [f"## {nombre}", f"actual: {serie[-1]}", f"serie7: {' '.join(str(v) for v in serie)}"]
        if clave in notas:
            lineas.append(f"nota: {notas[clave]}")
        lineas.append("")
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text("\n".join(lineas).rstrip() + "\n", encoding="utf-8")


def anotar_historial(series: dict[str, list[int]], momento: datetime) -> None:
    partes = [f"{momento:%Y-%m-%d %H:%M}"]
    for nombre, clave in METRICAS:
        serie = series.get(nombre, [])
        partes.append(f"{clave} {serie[-1] if serie else 's/d'}")
    HISTORIAL.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORIAL.exists():
        HISTORIAL.write_text("# Histórico de métricas\n\n", encoding="utf-8")
    with HISTORIAL.open("a", encoding="utf-8") as f:
        f.write(" | ".join(partes) + "\n")


def resumir(series: dict[str, list[int]], notas: dict[str, str]) -> str:
    """Resumen de 3 líneas, el número que más cambió primero."""
    filas = []
    for nombre, clave in METRICAS:
        serie = series.get(nombre, [])
        if not serie:
            filas.append((0.0, f"{nombre}: s/d — {notas.get(clave, 'sin datos')}"))
            continue
        actual = serie[-1]
        if len(serie) < 2:
            filas.append((0.0, f"{nombre}: {actual:,}".replace(",", ".") + " (primera medición)"))
            continue
        d = actual - serie[0]
        pct = (d / serie[0] * 100) if serie[0] else 0.0
        signo = "+" if d >= 0 else ""
        texto = f"{nombre}: {actual:,}".replace(",", ".") + f" ({signo}{d:,}".replace(",", ".") + f" / {signo}{pct:.1f}% en 7d)"
        if clave in notas:
            texto += f" — {notas[clave]}"
        filas.append((abs(pct), texto))
    filas.sort(key=lambda x: -x[0])
    return "\n".join(t for _, t in filas)


# ── CLI ─────────────────────────────────────────────────────────────────────
def main() -> int:
    p = argparse.ArgumentParser(description="Jala las métricas de Instagram al vault.")
    p.add_argument("--check", action="store_true", help="solo verifica que el token funcione")
    p.add_argument("--manual", nargs="*", metavar="clave=valor",
                   help="números a mano: seguidores=… vistas=… interacciones=…")
    p.add_argument("--config", default=str(CONFIG), help="ruta a instagram.json")
    p.add_argument("--api-base", default=API_BASE, help="base de la API (para pruebas)")
    args = p.parse_args()

    if args.check:
        cfg = cargar_config(Path(args.config))
        try:
            perfil = get(args.api_base, cfg["ig_user_id"], cfg["access_token"],
                         fields="username,followers_count")
            print(f"OK · @{perfil.get('username', '?')} · {perfil.get('followers_count', '?')} seguidores")
            return 0
        except Exception as e:
            print(f"FALLA · {e}", file=sys.stderr)
            return 1

    marcar("metricas", "corriendo")
    try:
        notas: dict[str, str] = {}
        if args.manual:
            valores = {}
            for par in args.manual:
                clave, _, valor = par.partition("=")
                if clave in {c for _, c in METRICAS}:
                    valores[clave] = int(valor)
            if not valores:
                raise SystemExit("--manual espera seguidores=… vistas=… interacciones=…")
            faltan = {c for _, c in METRICAS} - set(valores)
            for clave in faltan:
                notas[clave] = "no se cargó a mano en esta corrida"
        else:
            valores, notas = traer(args.api_base, cargar_config(Path(args.config)))

        momento = ahora()
        fecha_previa, series_previas = leer_previo()
        mismo_dia = fecha_previa[:10] == f"{momento:%Y-%m-%d}"

        series: dict[str, list[int]] = {}
        for nombre, clave in METRICAS:
            previa = series_previas.get(nombre, [])
            if clave in valores:
                series[nombre] = actualizar_serie(previa, valores[clave], mismo_dia)
            elif previa:
                series[nombre] = previa  # se conserva el último valor conocido
                notas.setdefault(clave, "sin dato nuevo en esta corrida")

        if not series:
            raise SystemExit("No se obtuvo ninguna métrica y no había historial previo. "
                             "Revisá el token con --check o cargá los números con --manual.")

        escribir(series, notas, momento)
        anotar_historial(series, momento)
        print(resumir(series, notas))
        print(f"\n→ {DESTINO.relative_to(REPO)} actualizado ({momento:%H:%M})")
        return 0
    finally:
        marcar("metricas", "inactiva")


if __name__ == "__main__":
    sys.exit(main())
