import sys, asyncio
from playwright.async_api import async_playwright
async def main(path, sel='.cover-title'):
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page(viewport={'width':1080,'height':1350})
        await pg.goto('file://'+path)
        await pg.wait_for_timeout(600)
        r = await pg.evaluate("""(sel)=>{const e=document.querySelector(sel);
            if(!e) return null;
            const cs=getComputedStyle(e);
            const fs=parseFloat(cs.fontSize);
            let lh=parseFloat(cs.lineHeight); if(isNaN(lh)) lh=fs*1.2;
            const rects=[...e.getClientRects()];
            return {alto:e.getBoundingClientRect().height, fs, lh,
                    renglones: Math.round(e.getBoundingClientRect().height/lh),
                    anchoMax: Math.max(...[...e.childNodes].map(()=>0), e.getBoundingClientRect().width)};}""", sel)
        print(r)
        await b.close()
asyncio.run(main(sys.argv[1]))
