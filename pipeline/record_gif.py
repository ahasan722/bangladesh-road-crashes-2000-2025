"""Record a short teaser (corridor map first) and export it as GIF + MP4. Usage: python pipeline/record_gif.py http://localhost:8765/index.html?tour=0 out_dir"""
import sys, asyncio, math, subprocess
from pathlib import Path
from playwright.async_api import async_playwright
sys.path.insert(0, str(Path(__file__).parent))
from record_demo import Bot, CURSOR_JS, W, H  # reuse the cursor overlay and motion helpers

URL, OUT = sys.argv[1], Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
VW, VH = 1600, 900

async def hover_bars(pg, bot, n):
    # walk the cursor through the tallest bars of the ribbon so each one lights up its stretch
    bars=await pg.evaluate("""()=>{ const r=document.getElementById('corrCanvas').getBoundingClientRect(); return (window.__ribbon?window.__ribbon.bars:[]).map(b=>{ const p=b.poly; const cx=(p[0][0]+p[1][0]+p[2][0]+p[3][0])/4, cy=(p[0][1]+p[1][1]+p[2][1]+p[3][1])/4; const h=Math.hypot(p[2][0]-p[1][0],p[2][1]-p[1][1]); return {x:r.left+cx, y:r.top+cy, h, m:b.bin.index}; }); }""")
    bars=sorted(bars, key=lambda b:-b["h"])[:n]; bars.sort(key=lambda b:b["m"])
    for b in bars: await bot.move(b["x"], b["y"], 0.9); await bot.wait(0.55)

async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--no-sandbox","--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist","--enable-unsafe-swiftshader"])
        ctx=await b.new_context(viewport={"width":VW,"height":VH}, record_video_dir=str(OUT), record_video_size={"width":VW,"height":VH})
        await ctx.add_init_script(CURSOR_JS)
        pg=await ctx.new_page(); await pg.goto(URL); await pg.wait_for_timeout(2500)
        bot=Bot(pg); bot.x, bot.y = VW*0.6, VH*0.7
        # hook: corridor map first
        await bot.scroll_to("#corridors", -60, 0.6); await pg.wait_for_timeout(2600)
        await hover_bars(pg, bot, 7)
        await bot.click("#corr3d"); await bot.wait(2.0)
        await bot.to("#corrMap", 0, -30, 0.4); await pg.mouse.down(); await bot.move(bot.x+90, bot.y+30, 1.2); await pg.mouse.up(); await bot.wait(0.8)
        await bot.click("#corr3d"); await bot.wait(0.8)
        await bot.click("#corrList .chip:nth-child(2)"); await bot.wait(1.8)
        await hover_bars(pg, bot, 6)
        await bot.click("#corrList .chip:nth-child(5)"); await bot.wait(1.8)
        await hover_bars(pg, bot, 6)
        # then the rest, briefly
        await bot.scroll_to("#top", 0, 1.2); await bot.wait(1.2)
        await bot.scroll_to("#gap"); await bot.sweep("#gapChart svg", dur=2.4); await bot.click("#gapScale button[data-v=log]"); await bot.wait(0.8)
        await bot.scroll_to("#where"); await bot.click("#wherePlay"); await bot.wait(4.5); await bot.click("#wherePlay")
        await bot.scroll_to("#who"); await bot.sweep("#whoChart svg", dur=2.2, y_frac=0.45)
        await bot.scroll_to("#when"); box=await bot.to("#whenDial", 0, 0, 0.4); cx=box["x"]+box["width"]/2; cy=box["y"]+box["height"]/2; r=box["width"]*104/300
        await bot.move(cx, cy-r, 0.5); await pg.mouse.down()
        for a in range(0, 190, 8):
            ang=math.radians(a-90); await pg.mouse.move(cx+r*math.cos(ang), cy+r*math.sin(ang)); await asyncio.sleep(0.03)
        await pg.mouse.up(); await bot.wait(1.0)
        await bot.scroll_to("#roads"); await bot.sweep("#roadsMonthly svg", y_frac=0.6, dur=2.0); await bot.wait(0.6)
        await bot.scroll_to("#corridors", -60, 1.2); await bot.wait(1.5)
        await ctx.close(); await b.close()
    src=max(OUT.glob("*.webm"), key=lambda f: f.stat().st_mtime)
    mp4=OUT/"deadly-roads-bd-teaser.mp4"; gif=OUT/"deadly-roads-bd-teaser.gif"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(src),"-filter:v","setpts=PTS/1.4,fps=30,format=yuv420p","-an","-c:v","libx264","-preset","fast","-crf","21","-movflags","+faststart",str(mp4)],check=True)
    # two-pass palette GIF, 1200 px wide, 12 fps
    GIF_SECONDS, GIF_W, GIF_FPS = 32, 1000, 10   # the corridor hook; keep the GIF under ~15 MB
    subprocess.run(["ffmpeg","-y","-loglevel","error","-t",str(GIF_SECONDS),"-i",str(mp4),"-vf",f"fps={GIF_FPS},scale={GIF_W}:-1:flags=lanczos,palettegen=max_colors=160:stats_mode=diff",str(OUT/"pal.png")],check=True)
    subprocess.run(["ffmpeg","-y","-loglevel","error","-t",str(GIF_SECONDS),"-i",str(mp4),"-i",str(OUT/"pal.png"),"-lavfi",f"fps={GIF_FPS},scale={GIF_W}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle",str(gif)],check=True)
    print("wrote", mp4, mp4.stat().st_size//1024, "KB;", gif, gif.stat().st_size//1024, "KB")

asyncio.run(main())
