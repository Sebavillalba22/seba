#!/usr/bin/env python3
"""Devuelve el bounding box exacto del marco (.frame img) de una placa ya
renderizada. Se usa para componer un video adentro con componer_video.sh.

  python3 medir_marco.py /ruta/slideN.html
"""
import sys, asyncio
from playwright.async_api import async_playwright

async def main(html):
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page(viewport={'width': 1080, 'height': 1350}, device_scale_factor=1)
        await pg.goto('file://' + html); await pg.wait_for_timeout(500)
        r = await pg.evaluate("""()=>{const e=document.querySelector('.frame img');
            const b=e.getBoundingClientRect();
            return {x:Math.round(b.x), y:Math.round(b.y), w:Math.round(b.width), h:Math.round(b.height)};}""")
        print(r); await b.close()

asyncio.run(main(sys.argv[1]))
