"""Functional verification of the site in headless Chromium. Usage: python pipeline/verify_site.py http://localhost:8765/index.html"""
import sys, asyncio, math
from playwright.async_api import async_playwright
URL=sys.argv[1]
async def main():
    fails=[]
    def check(cond, msg):
        print(("PASS " if cond else "FAIL ")+msg);
        if not cond: fails.append(msg)
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--no-sandbox","--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist","--enable-unsafe-swiftshader"])
        pg=await b.new_page(viewport={"width":1440,"height":900})
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        con=[]; pg.on("console", lambda m: con.append(m.text) if m.type=="error" and "WebGL" not in m.text and "GL Driver" not in m.text and "swiftshader" not in m.text.lower() else None)
        resp_fail=[]; pg.on("response", lambda r: resp_fail.append(r.url) if r.status>=400 else None)
        await pg.goto(URL); await pg.wait_for_timeout(4000)
        check(not errs, f"no page errors {errs[:2]}"); check(not con, f"no console errors {con[:2]}"); check(not resp_fail, f"all requests ok {resp_fail[:3]}")
        # hero meta filled
        check("deaths" in (await pg.inner_text("#heroMeta")), "hero stats rendered")
        # gap chart has paths for several sources
        n=await pg.locator("#gapChart path").count(); check(n>=5, f"gap chart paths {n}")
        await pg.click("#gapScale button[data-v=log]"); await pg.click("#gapMeasure button[data-v=rate]"); await pg.wait_for_timeout(300)
        t=await pg.inner_text("#gapChart"); check("%" not in t and len(t)>10, "gap rate/log redraw")
        # where
        await pg.locator("#where").scroll_into_view_if_needed(); await pg.wait_for_timeout(1500)
        s0=await pg.inner_text("#whereStats"); await pg.click("#wherePlay"); await pg.wait_for_timeout(2000); await pg.click("#wherePlay"); s1=await pg.inner_text("#whereStats")
        check("highest" in s0 and s0!=s1, "where play advances period")
        await pg.select_option("#whereSource","district"); await pg.wait_for_timeout(500); check("most listed" in (await pg.inner_text("#whereStats")), "district layer stats")
        # corridors
        await pg.locator("#corridors").scroll_into_view_if_needed(); await pg.wait_for_timeout(2500)
        st=await pg.inner_text("#corrStats"); check("listed spots on N1" in st, "N1 loaded")
        bars=await pg.evaluate("document.getElementById('corrCanvas').getContext('2d').getImageData(0,0,document.getElementById('corrCanvas').width,document.getElementById('corrCanvas').height).data.some((v,i)=>i%4===3&&v>0)")
        check(bars, "ribbon drew bars on the canvas")
        await pg.click("#corrList .chip:nth-child(5)"); await pg.wait_for_timeout(2500); st5=await pg.inner_text("#corrStats"); check("listed spots on N5" in st5 and st5!=st, "switch to N5 changes stats")
        await pg.click("#corr3d"); await pg.wait_for_timeout(1500); pitch=await pg.evaluate("window.__data && 1"); check((await pg.get_attribute("#corr3d","class") or "").find("on")>=0, "3D toggle on")
        await pg.click("#corr3d"); await pg.wait_for_timeout(800)
        await pg.click("#corrBin button[data-v='5']"); await pg.wait_for_timeout(600); check("worst 5 km" in (await pg.inner_text("#corrStats")), "bin size 5 km applied")
        # hover a bar: move across the stage until the panel changes
        await pg.evaluate("document.getElementById('corrMap').scrollIntoView({block:'center'})"); await pg.wait_for_timeout(1500)
        pt=await pg.evaluate("(()=>{const r=document.getElementById('corrCanvas').getBoundingClientRect(); const bs=window.__ribbon.bars; if(!bs.length) return null; const p=bs[0].poly; return [r.left+(p[0][0]+p[2][0])/2, r.top+(p[0][1]+p[2][1])/2]})()")
        found=False
        if pt: await pg.mouse.move(pt[0],pt[1]); await pg.wait_for_timeout(400); found="listed hazardous location" in (await pg.inner_text("#corrPanel"))
        check(found, "hovering a bar fills the panel")
        # who
        await pg.locator("#who").scroll_into_view_if_needed(); await pg.wait_for_timeout(500)
        n=await pg.locator("#whoChart circle").count(); check(n>=20, f"who chart points {n}")
        await pg.click("#whoMode button[data-v=share]"); await pg.wait_for_timeout(300); check("%" in (await pg.inner_text("#whoChart")), "who share mode")
        # when: drag dial
        await pg.evaluate("document.getElementById('whenDial').scrollIntoView({block:'center'})"); await pg.wait_for_timeout(900)
        s0=await pg.inner_text("#whenStats"); d=await pg.locator("#whenDial").bounding_box(); cx=d["x"]+d["width"]/2; cy=d["y"]+d["height"]/2; r=d["width"]*104/300
        await pg.mouse.move(cx,cy-r); await pg.mouse.down(); await pg.mouse.move(cx+r,cy, steps=10); await pg.mouse.up(); await pg.wait_for_timeout(300)
        s1=await pg.inner_text("#whenStats"); check(s0!=s1 and "between" in s1, "dial drag updates share")
        check((await pg.locator("#whenMonths rect").count())>=60, "month heat strip rendered")
        check((await pg.locator("#whenEid rect").count())>=8, "Eid bars rendered")
        # roads
        await pg.locator("#roads").scroll_into_view_if_needed(); await pg.wait_for_timeout(500)
        check((await pg.locator("#roadsChart rect").count())>=30, "road share bars"); check((await pg.locator("#roadsMonthly rect").count())>=50, "monthly road class bars")
        # method
        check("Read this before you quote" in (await pg.inner_text("#method")), "disclaimer present")
        check((await pg.locator("#downloads a").count())>=7, "download links")
        check(not errs, f"no page errors at end {errs[:2]}")
        await b.close()
    print("\n%d failures" % len(fails)); sys.exit(1 if fails else 0)
asyncio.run(main())
