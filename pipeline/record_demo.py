"""Record a demo walkthrough of the site with a visible cursor. Usage: python pipeline/record_demo.py http://localhost:8765/index.html out_dir"""
import sys, asyncio, math, shutil, subprocess
from pathlib import Path
from playwright.async_api import async_playwright

URL, OUT = (sys.argv[1], Path(sys.argv[2])) if __name__=="__main__" else (None, None)
if OUT: OUT.mkdir(parents=True, exist_ok=True)
W, H = 1920, 1080

CURSOR_JS = """
(() => {
  const c = document.createElement('div'); c.id = '__cur';
  c.style.cssText = 'position:fixed;left:0;top:0;width:26px;height:26px;z-index:999999;pointer-events:none;transform:translate(-3px,-2px);transition:transform .08s';
  c.innerHTML = `<svg viewBox="0 0 24 24" width="26" height="26"><path d="M3 2 L3 18 L7.5 14 L10.5 21 L13.5 19.5 L10.5 12.8 L16.5 12.8 Z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>`;
  const ring = document.createElement('div'); ring.id='__ring';
  ring.style.cssText='position:fixed;left:0;top:0;width:34px;height:34px;border-radius:50%;border:3px solid #F2B035;z-index:999998;pointer-events:none;opacity:0;transform:translate(-17px,-17px)';
  document.addEventListener('DOMContentLoaded', ()=>{ document.body.appendChild(c); document.body.appendChild(ring); });
  window.addEventListener('mousemove', e => { c.style.left = e.clientX+'px'; c.style.top = e.clientY+'px'; ring.style.left=e.clientX+'px'; ring.style.top=e.clientY+'px'; });
  window.addEventListener('mousedown', ()=>{ ring.style.transition='none'; ring.style.opacity=1; ring.style.transform='translate(-17px,-17px) scale(.6)'; requestAnimationFrame(()=>{ ring.style.transition='all .35s'; ring.style.opacity=0; ring.style.transform='translate(-17px,-17px) scale(1.4)'; }); });
})();
"""

class Bot:
    def __init__(self, page): self.p=page; self.x=W/2; self.y=H/2
    async def move(self, x, y, dur=0.6):
        steps=max(6,int(dur*15)); sx,sy=self.x,self.y
        for i in range(1,steps+1):
            t=i/steps; e=t*t*(3-2*t)  # ease in-out
            await self.p.mouse.move(sx+(x-sx)*e, sy+(y-sy)*e); await asyncio.sleep(dur/steps)
        self.x,self.y=x,y
    async def to(self, sel, dx=0, dy=0, dur=0.7):
        el=self.p.locator(sel).first; await el.scroll_into_view_if_needed(); box=await el.bounding_box()
        if not box: return None
        await self.move(box["x"]+box["width"]/2+dx, box["y"]+box["height"]/2+dy, dur); return box
    async def click(self, sel, dx=0, dy=0, pause=0.9):
        await self.to(sel, dx, dy); await self.p.mouse.down(); await asyncio.sleep(0.08); await self.p.mouse.up(); await asyncio.sleep(pause)
    async def scroll_to(self, sel, offset=-70, dur=1.2):
        y=await self.p.evaluate("(s)=>document.querySelector(s).getBoundingClientRect().top+window.scrollY", sel)
        start=await self.p.evaluate("window.scrollY"); target=y+offset; steps=int(dur*20)
        for i in range(1,steps+1):
            t=i/steps; e=t*t*(3-2*t); await self.p.evaluate(f"window.scrollTo(0,{start+(target-start)*e})"); await asyncio.sleep(dur/steps)
    async def sweep(self, sel, frac_from=0.08, frac_to=0.92, y_frac=0.5, dur=2.5):
        box=await self.to(sel, 0, 0, 0.4); x0=box["x"]+box["width"]*frac_from; x1=box["x"]+box["width"]*frac_to; y=box["y"]+box["height"]*y_frac
        await self.move(x0,y,0.4); await self.move(x1,y,dur)
    async def wait(self, s): await asyncio.sleep(s)

async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--no-sandbox","--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist","--enable-unsafe-swiftshader"])
        ctx=await b.new_context(viewport={"width":W,"height":H}, record_video_dir=str(OUT), record_video_size={"width":W,"height":H}, device_scale_factor=1)
        await ctx.add_init_script(CURSOR_JS)
        pg=await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(2500)
        bot=Bot(pg); await pg.mouse.move(W*0.6,H*0.7)
        await bot.wait(2.5)
        # 1 hero: drift across the km posts
        await bot.move(W*0.05, H*0.3, 0.8); await bot.move(W*0.95, H*0.3, 3.0); await bot.wait(0.6)
        # 2 gap
        await bot.scroll_to("#gap"); await bot.wait(0.8)
        await bot.sweep("#gapChart svg", dur=3.2); await bot.wait(0.5)
        await bot.click("#gapScale button[data-v=log]"); await bot.wait(1.0)
        await bot.click("#gapMeasure button[data-v=rate]"); await bot.wait(1.4)
        await bot.click("#gapMeasure button[data-v=deaths]"); await bot.click("#gapScale button[data-v=linear]"); await bot.wait(0.6)
        # 3 where
        await bot.scroll_to("#where"); await bot.wait(0.8)
        await bot.to("#whereMap", 40, -40, 0.8); await bot.move(bot.x+60, bot.y+90, 1.2); await bot.move(bot.x-160, bot.y+40, 1.2); await bot.move(bot.x+30, bot.y-150, 1.2); await bot.wait(0.4)
        await bot.click("#wherePlay"); await bot.wait(6.5); await bot.click("#wherePlay")
        await bot.click("#whereMeasure button[data-v=rate]"); await bot.wait(1.6)
        await bot.to("#whereSource"); await pg.select_option("#whereSource","district"); await bot.wait(0.8)
        await bot.to("#whereMap", -60, 60, 0.8); await bot.move(bot.x+120, bot.y-20, 1.4); await bot.wait(0.8)
        await pg.select_option("#whereSource","division"); await bot.click("#whereMeasure button[data-v=share]")
        # 4 corridors
        await bot.scroll_to("#corridors"); await bot.wait(1.2)
        await bot.to("#corrMap", 0, 0, 0.6); await bot.wait(0.5)
        # hover along the ribbon: sweep diagonally over the map
        box=await bot.to("#corrMap", -120, -200, 0.5); await bot.move(box["x"]+box["width"]*0.62, box["y"]+box["height"]*0.78, 3.5); await bot.wait(0.6)
        await bot.click("#corrBin button[data-v='5']"); await bot.wait(1.2)
        await bot.click("#corr3d"); await bot.wait(2.4)
        await bot.to("#corrMap", 0, -40, 0.5); await pg.mouse.down(); await bot.move(bot.x+80, bot.y+40, 1.4); await pg.mouse.up(); await bot.wait(1.0)
        await bot.click("#corr3d"); await bot.wait(1.2)
        await bot.click("#corrList .chip:nth-child(2)"); await bot.wait(2.2)   # N2
        box=await bot.to("#corrMap", -200, 60, 0.5); await bot.move(box["x"]+box["width"]*0.75, box["y"]+box["height"]*0.35, 3.0); await bot.wait(0.5)
        await bot.click("#corrList .chip:nth-child(5)"); await bot.wait(2.2)   # N5
        box=await bot.to("#corrMap", 0, 220, 0.5); await bot.move(box["x"]+box["width"]*0.45, box["y"]+box["height"]*0.12, 3.0); await bot.wait(0.5)
        # 5 who
        await bot.scroll_to("#who"); await bot.wait(0.8)
        await bot.sweep("#whoChart svg", dur=3.0, y_frac=0.45); await bot.wait(0.4)
        await bot.click("#whoMode button[data-v=share]"); await bot.wait(1.4)
        await bot.click("#whoCats .chip:nth-child(1)"); await bot.wait(1.2); await bot.click("#whoCats .chip:nth-child(1)")
        await bot.click("#whoMode button[data-v=stack]")
        await bot.scroll_to("#whoVictim", -260); await bot.sweep("#whoVictim svg", y_frac=0.3, dur=1.6)
        # 6 when: drag the dial handle
        await bot.scroll_to("#when"); await bot.wait(0.8)
        box=await bot.to("#whenDial", 0, 0, 0.5); cx=box["x"]+box["width"]/2; cy=box["y"]+box["height"]/2; r=box["width"]*104/300
        await bot.move(cx, cy-r, 0.6); await pg.mouse.down()
        for a in range(0, 190, 6):
            ang=math.radians(a-90); await pg.mouse.move(cx+r*math.cos(ang), cy+r*math.sin(ang)); await asyncio.sleep(0.03)
        await pg.mouse.up(); await bot.wait(1.4)
        await bot.sweep("#whenMonths svg", y_frac=0.55, dur=2.6); await bot.wait(0.4)
        await bot.scroll_to("#whenEid", -200); await bot.sweep("#whenEid svg", y_frac=0.6, dur=2.4)
        # 7 roads
        await bot.scroll_to("#roads"); await bot.wait(0.8)
        await bot.sweep("#roadsChart svg", frac_from=0.3, frac_to=0.9, y_frac=0.35, dur=2.4); await bot.wait(0.4)
        await bot.scroll_to("#roadsMonthly", -200); await bot.sweep("#roadsMonthly svg", y_frac=0.6, dur=2.6)
        # 8 method + disclaimer
        await bot.scroll_to("#method"); await bot.wait(1.2); await bot.scroll_to("#disclaimer", -120, 1.6); await bot.wait(3.0)
        await bot.scroll_to("#top", 0, 1.8); await bot.wait(2.0)
        print("page errors:", errs)
        await ctx.close(); await b.close()
    vids=list(OUT.glob("*.webm")); src=max(vids, key=lambda f: f.stat().st_mtime)
    mp4=OUT/"deadly-roads-bd-demo.mp4"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(src),"-vf","fps=30,format=yuv420p","-c:v","libx264","-preset","fast","-crf","20","-movflags","+faststart",str(mp4)], check=True)
    print("wrote", mp4, mp4.stat().st_size//1024, "KB")

if __name__=="__main__": asyncio.run(main())
