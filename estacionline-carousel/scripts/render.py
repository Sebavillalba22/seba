"""
render.py — Render slide HTMLs to PNG using Playwright.

Usage:

    python render.py /home/claude/my_carrusel

Looks for slide1.html, slide2.html, ... slideN.html in the given directory,
renders each at 1080x1350 (2x for sharpness), and writes slide1.png ... slideN.png.

CRITICAL: waits for all images AND fonts to load before screenshot.
- Skipping the image wait causes the img tag's alt text to render instead.
- Skipping the font wait causes screenshots with the fallback font instead
  of Inter (different letter-spacing/weights = "broken" design).
"""
import asyncio, os
import sys
from pathlib import Path
from playwright.async_api import async_playwright
from PIL import Image


async def render_dir(work_dir: str):
    work = Path(work_dir)
    # Find all slideN.html files in numeric order
    slide_files = sorted(
        [p for p in work.glob('slide*.html')],
        key=lambda p: int(p.stem.replace('slide', ''))
    )
    if not slide_files:
        print(f'No slide*.html files found in {work_dir}')
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=os.environ.get('PW_CHROMIUM') or None)
        ctx = await browser.new_context(
            viewport={'width': 1080, 'height': 1350},
            device_scale_factor=2
        )
        for html_path in slide_files:
            i = html_path.stem.replace('slide', '')
            page = await ctx.new_page()
            await page.goto(f'file://{html_path.absolute()}')

            # CRITICAL: wait for all images to load before screenshot
            await page.evaluate("""() => Promise.all(Array.from(document.images).map(img =>
                img.complete ? null : new Promise(r => { img.onload = img.onerror = r; })))""")
            # CRITICAL: wait for webfonts (Inter) — otherwise the screenshot
            # can be taken with the fallback font and the design looks off
            await page.evaluate("() => document.fonts.ready")
            await page.wait_for_timeout(400)  # extra safety margin

            png_2x = work / f'slide{i}_2x.png'
            await page.screenshot(
                path=str(png_2x),
                clip={'x': 0, 'y': 0, 'width': 1080, 'height': 1350}
            )
            await page.close()

            # Downsample 2x → 1080x1350 with LANCZOS
            img = Image.open(png_2x)
            img.thumbnail((1080, 1350), Image.LANCZOS)
            final = work / f'slide{i}.png'
            img.save(final, optimize=True)
            print(f'slide{i}: OK')

        await browser.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python render.py <work_dir>')
        sys.exit(1)
    asyncio.run(render_dir(sys.argv[1]))
