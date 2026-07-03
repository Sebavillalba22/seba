#!/usr/bin/env python3
"""Programador RECURRENTE de Historias de Instagram. Stdlib only.

Lee recurring.json (al lado de SKILL.md): reglas por sponsor con día(s) de la
semana + hora, que se repiten INDEFINIDAMENTE (no por mes). Cada vez que corre,
publica las historias cuyo día/hora ya llegó hoy y que todavía no se postearon.
Pensado para correr periódicamente (cron) en una compu prendida, o con --daemon.

recurring.json = lista de reglas:
[
  {
    "label": "Embody Fitness",
    "days": ["thu", "sat"],          // lun=mon mar=tue mié=wed jue=thu vie=fri sáb=sat dom=sun
    "time": "05:00",                  // hora LOCAL de la máquina
    "media_type": "video",            // "video" | "image"
    "media": ["https://.../a.mp4", "https://.../b.mp4"]   // rota entre estas
  }
]

Estado en schedule_state.json (lo maneja el script): por label guarda la última
fecha posteada y un contador para rotar la media.

Uso:
  story_scheduler.py            # corre una vez (cron)
  story_scheduler.py --daemon   # bucle infinito, revisa cada 60s
  story_scheduler.py --dry-run  # no publica, muestra qué haría
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / "recurring.json"
STATE = ROOT / "schedule_state.json"
IG_STORY = Path(__file__).resolve().parent / "ig_story.py"

DAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6,
        "lun": 0, "mar": 1, "mie": 2, "mié": 2, "jue": 3, "vie": 4, "sab": 5, "sáb": 5, "dom": 6}


def log(m):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {m}", flush=True)


def load_rules():
    if not RULES.exists():
        log(f"no existe {RULES}")
        return []
    return json.loads(RULES.read_text(encoding="utf-8"))


def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_state(s):
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")


def run_once(dry_run=False):
    rules = load_rules()
    state = load_state()
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    wd = now.weekday()
    changed = False
    posted_any = False

    for r in rules:
        label = r["label"]
        days = [DAYS.get(d.strip().lower()) for d in r.get("days", [])]
        if wd not in days:
            continue
        try:
            hh, mm = (int(x) for x in r["time"].split(":"))
        except (ValueError, KeyError):
            log(f"hora inválida en regla {label!r}"); continue
        if (now.hour, now.minute) < (hh, mm):
            continue  # todavía no es la hora de hoy
        st = state.get(label, {"last": None, "count": 0})
        if st.get("last") == today:
            continue  # ya se posteó hoy para este sponsor
        media = r.get("media", [])
        if not media:
            log(f"regla {label!r} sin media"); continue
        url = media[st.get("count", 0) % len(media)]
        flag = "--video-url" if r.get("media_type", "video") == "video" else "--image-url"
        cmd = [sys.executable, str(IG_STORY), flag, url]
        if dry_run:
            cmd.append("--dry-run")
        log(f"historia: {label} ({r['time']}) -> {url.rsplit('/', 1)[-1]}")
        res = subprocess.run(cmd, capture_output=True, text=True)
        posted_any = True
        if res.returncode == 0:
            log(f"  OK -> {res.stdout.strip()}")
            if not dry_run:
                state[label] = {"last": today, "count": st.get("count", 0) + 1}
                changed = True
        else:
            log(f"  FALLO -> {res.stderr.strip() or res.stdout.strip()}")
    if changed:
        save_state(state)
    if not posted_any:
        log("nada pendiente")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--daemon", action="store_true", help="bucle infinito (revisa cada 60s).")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.daemon:
        log("daemon iniciado (Ctrl+C para salir)")
        while True:
            try:
                run_once(dry_run=args.dry_run)
            except Exception as ex:  # noqa: BLE001
                log(f"error: {ex}")
            time.sleep(60)
    else:
        run_once(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
