#!/usr/bin/env python3
"""Estado de las skills para el panel de comandos del HUD.

Mantiene vault/outputs/estado-skills.md: marca una skill como corriendo o
inactiva, lleva el contador de corridas del día (se resetea solo al cambiar
de fecha) y anota la hora de la última corrida.

Uso desde una skill:
    python3 scripts/estado_skills.py metricas corriendo
    python3 scripts/estado_skills.py metricas inactiva     # suma 1 a "hoy"

Solo stdlib.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from zoneinfo import ZoneInfo

    TZ = ZoneInfo("America/Argentina/Buenos_Aires")
except Exception:  # pragma: no cover - sin tzdata, cae a la hora local
    TZ = None

REPO = Path(__file__).resolve().parent.parent
ESTADO = REPO / "vault" / "outputs" / "estado-skills.md"
SKILLS = ["metricas", "inbox", "tendencias", "plan", "vault"]

LINEA = re.compile(
    r"^-\s*(?P<nombre>\S+)\s*\|\s*(?P<estado>\S+)\s*\|\s*hoy:\s*(?P<hoy>\d+)\s*\|\s*ultima:\s*(?P<ultima>.*)$"
)


def ahora() -> datetime:
    return datetime.now(TZ) if TZ else datetime.now()


def leer() -> tuple[str, dict[str, dict]]:
    """Devuelve (fecha_de_actualizado, {skill: {estado, hoy, ultima}})."""
    filas: dict[str, dict] = {}
    fecha = ""
    if ESTADO.exists():
        texto = ESTADO.read_text(encoding="utf-8")
        m = re.search(r"^actualizado:\s*(\S+)", texto, re.M)
        if m:
            fecha = m.group(1)
        for linea in texto.splitlines():
            m = LINEA.match(linea.strip())
            if m:
                filas[m.group("nombre")] = {
                    "estado": m.group("estado"),
                    "hoy": int(m.group("hoy")),
                    "ultima": m.group("ultima").strip() or "—",
                }
    for nombre in SKILLS:
        filas.setdefault(nombre, {"estado": "inactiva", "hoy": 0, "ultima": "—"})
    return fecha, filas


def escribir(filas: dict[str, dict], momento: datetime) -> None:
    orden = SKILLS + [n for n in filas if n not in SKILLS]
    cuerpo = [
        "# Estado de skills",
        f"actualizado: {momento:%Y-%m-%d %H:%M}",
        "",
    ]
    for nombre in orden:
        f = filas[nombre]
        cuerpo.append(
            f"- {nombre} | {f['estado']} | hoy: {f['hoy']} | ultima: {f['ultima']}"
        )
    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    ESTADO.write_text("\n".join(cuerpo) + "\n", encoding="utf-8")


def marcar(skill: str, estado: str) -> dict:
    """Marca la skill como 'corriendo' o 'inactiva' (esto último cuenta una corrida)."""
    momento = ahora()
    hoy = f"{momento:%Y-%m-%d}"
    fecha_previa, filas = leer()

    if fecha_previa[:10] != hoy:  # día nuevo: se reinician los contadores
        for f in filas.values():
            f["hoy"] = 0

    fila = filas.setdefault(skill, {"estado": "inactiva", "hoy": 0, "ultima": "—"})
    if estado == "corriendo":
        fila["estado"] = "corriendo"
    else:
        fila["estado"] = "inactiva"
        fila["hoy"] += 1
        fila["ultima"] = f"{momento:%H:%M}"

    escribir(filas, momento)
    return fila


def main() -> int:
    p = argparse.ArgumentParser(description="Actualiza el estado de una skill para el HUD.")
    p.add_argument("skill", help="nombre de la skill (metricas, inbox, tendencias, plan, vault…)")
    p.add_argument("estado", choices=["corriendo", "inactiva"], help="estado nuevo")
    args = p.parse_args()

    fila = marcar(args.skill, args.estado)
    print(f"{args.skill}: {fila['estado']} | hoy: {fila['hoy']} | ultima: {fila['ultima']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
