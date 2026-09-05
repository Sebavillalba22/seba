import sys, asyncio, glob, os
from playwright.async_api import async_playwright
async def main(carpeta):
    archivos = sorted(glob.glob(os.path.join(carpeta,'slide*.html')),
                      key=lambda f: int(''.join(c for c in os.path.basename(f) if c.isdigit())))
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page(viewport={'width':1080,'height':1350})
        for f in archivos:
            await pg.goto('file://'+f); await pg.wait_for_timeout(400)
            r = await pg.evaluate("""()=>{
                const sel=['.list-wrap','.cover-content','.quote-wrap','.num-wrap','.close-wrap','.content'];
                for (const s of sel){ const e=document.querySelector(s); if(!e) continue;
                    const cs=getComputedStyle(e);
                    const padT=parseFloat(cs.paddingTop), padB=parseFloat(cs.paddingBottom);
                    let alto=0; for(const c of e.children) alto+=c.getBoundingClientRect().height
                        + parseFloat(getComputedStyle(c).marginTop) + parseFloat(getComputedStyle(c).marginBottom);
                    return {sel:s, contenido:Math.round(alto), disponible:Math.round(1350-padT-padB),
                            desborde: Math.round(alto-(1350-padT-padB))};
                }
                return null;}""")
            print(os.path.basename(f), r)
        await b.close()
asyncio.run(main(sys.argv[1]))
