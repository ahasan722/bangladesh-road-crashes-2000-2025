// Self-running tour: the page operates itself with a visible cursor until the visitor touches anything.
// Starts automatically after a short idle on first load (unless ?tour=0), or from the "Watch tour" button, or with ?tour=1.
export function initTour(){
  const btn=document.getElementById("tourBtn"); const cur=document.createElement("div"); cur.id="tourCursor"; cur.innerHTML=`<svg viewBox="0 0 24 24" width="26" height="26"><path d="M3 2 L3 18 L7.5 14 L10.5 21 L13.5 19.5 L10.5 12.8 L16.5 12.8 Z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>`;
  const ring=document.createElement("div"); ring.id="tourRing"; const cap=document.createElement("div"); cap.id="tourCaption";
  document.body.append(cur, ring, cap);
  let running=false, stop=false, px=innerWidth*0.6, py=innerHeight*0.7, token=0;
  const q=new URLSearchParams(location.search); const auto=q.get("tour")!=="0" && !matchMedia("(prefers-reduced-motion: reduce)").matches && innerWidth>900;
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const ease=t=>t*t*(3-2*t);
  function setCursor(x,y){ px=x; py=y; cur.style.transform=`translate(${x-3}px,${y-2}px)`; ring.style.left=x+"px"; ring.style.top=y+"px"; }
  function fire(type,x,y,extra={}){ const el=document.elementFromPoint(x,y); if(!el) return null;
    const init={bubbles:true,cancelable:true,clientX:x,clientY:y,view:window,pointerId:1,pointerType:"mouse",isPrimary:true,...extra};
    el.dispatchEvent(new PointerEvent(type.replace("mouse","pointer"),init)); el.dispatchEvent(new MouseEvent(type,init)); return el; }
  async function move(x,y,ms=600){ const sx=px,sy=py,t0=performance.now(); let last=null;
    while(!stop){ const t=Math.min(1,(performance.now()-t0)/ms), e=ease(t); const nx=sx+(x-sx)*e, ny=sy+(y-sy)*e; setCursor(nx,ny);
      const el=fire("mousemove",nx,ny); if(last&&last!==el){ last.dispatchEvent(new MouseEvent("mouseleave",{bubbles:false,clientX:nx,clientY:ny})); last.dispatchEvent(new MouseEvent("mouseout",{bubbles:true,clientX:nx,clientY:ny})); if(el){ el.dispatchEvent(new MouseEvent("mouseenter",{bubbles:false,clientX:nx,clientY:ny})); el.dispatchEvent(new MouseEvent("mouseover",{bubbles:true,clientX:nx,clientY:ny})); } } last=el;
      if(t>=1) break; await sleep(16); } }
  function rect(sel){ const el=document.querySelector(sel); return el? el.getBoundingClientRect(): null; }
  async function scrollTo(sel,offset=-64,ms=1100){ const r=rect(sel); if(!r) return; const start=scrollY, target=start+r.top+offset, t0=performance.now();
    while(!stop){ const t=Math.min(1,(performance.now()-t0)/ms); window.scrollTo(0,start+(target-start)*ease(t)); if(t>=1) break; await sleep(16); } }
  async function to(sel,fx=.5,fy=.5,ms=700){ const r=rect(sel); if(!r) return null; await move(r.left+r.width*fx, r.top+r.height*fy, ms); return r; }
  async function click(sel,fx=.5,fy=.5){ await to(sel,fx,fy); if(stop) return; ring.classList.remove("pop"); void ring.offsetWidth; ring.classList.add("pop"); fire("mousedown",px,py); fire("mouseup",px,py); const el=document.elementFromPoint(px,py); el&&el.click(); await sleep(700); }
  async function sweep(sel,x0=.08,x1=.92,fy=.5,ms=2600){ const r=rect(sel); if(!r) return; await move(r.left+r.width*x0, r.top+r.height*fy, 400); await move(r.left+r.width*x1, r.top+r.height*fy, ms); }
  async function say(text,ms=0){ cap.textContent=text; cap.classList.toggle("show",!!text); if(ms) await sleep(ms); }
  async function select(sel,value){ await to(sel); const el=document.querySelector(sel); if(!el) return; el.value=value; el.dispatchEvent(new Event("change",{bubbles:true})); await sleep(600); }

  const script=[
    async()=>{ await say("A self-running tour. Move your mouse or press any key to take over.",2200); await move(innerWidth*0.05,innerHeight*0.28,700); await move(innerWidth*0.95,innerHeight*0.28,2600); },
    async()=>{ await scrollTo("#gap"); await say("Chapter 1: nine sources, one axis. Hover a year to read every figure."); await sweep("#gapChart svg",.08,.92,.5,3000); await click("#gapScale button[data-v=log]"); await sleep(900); await click("#gapMeasure button[data-v=rate]"); await sleep(1300); await click("#gapMeasure button[data-v=deaths]"); await click("#gapScale button[data-v=linear]"); },
    async()=>{ await scrollTo("#where"); await say("Chapter 2: which division's roads produce the crashes. Play runs every published period."); const r=await to("#whereMap",.55,.42,800); if(!r) return; await move(r.left+r.width*.62,r.top+r.height*.6,1200); await move(r.left+r.width*.42,r.top+r.height*.72,1200); await move(r.left+r.width*.5,r.top+r.height*.3,1200);
      await click("#wherePlay"); await sleep(6200); await click("#wherePlay"); await click("#whereMeasure button[data-v=rate]"); await sleep(1400); await select("#whereSource","district"); await to("#whereMap",.45,.6,700); await move(px+140,py-30,1300); await sleep(600); await select("#whereSource","division"); await click("#whereMeasure button[data-v=share]"); },
    async()=>{ await scrollTo("#corridors"); await say("Chapter 3: a hazard ribbon along the real road. Hover a bar to light up the stretch."); await sleep(900); let r=await to("#corrMap",.45,.2,600); if(!r) return; await move(r.left+r.width*.62,r.top+r.height*.78,3400); await click("#corrBin button[data-v='5']"); await sleep(900);
      await click("#corr3d"); await say("3D turns the ribbon into a wall."); await sleep(2200); await click("#corr3d"); await sleep(900);
      await click("#corrList .chip:nth-child(2)"); await say("N2, Dhaka to Sylhet."); await sleep(1800); r=await to("#corrMap",.25,.55,500); await move(r.left+r.width*.78,r.top+r.height*.32,3000);
      await click("#corrList .chip:nth-child(5)"); await say("N5, Dhaka to Banglabandha."); await sleep(1800); r=await to("#corrMap",.5,.88,500); await move(r.left+r.width*.45,r.top+r.height*.12,3000); await click("#corrList .chip:nth-child(1)"); },
    async()=>{ await scrollTo("#who"); await say("Chapter 4: who dies. The motorcycle line doubled in two years."); await sweep("#whoChart svg",.08,.92,.45,3000); await click("#whoMode button[data-v=share]"); await sleep(1300); await click("#whoMode button[data-v=stack]"); await scrollTo("#whoVictim",-240); await sweep("#whoVictim svg",.45,.9,.3,1600); },
    async()=>{ await scrollTo("#when",-40); await say("Chapter 5: drag the dial to pick a window of the day."); const r=rect("#whenDial"); if(r){ const cx=r.left+r.width/2, cy=r.top+r.height/2, rad=r.width*104/300; await move(cx,cy-rad,700); fire("mousedown",px,py); for(let a=0;a<=180&&!stop;a+=5){ const an=(a-90)*Math.PI/180; const x=cx+rad*Math.cos(an), y=cy+rad*Math.sin(an); setCursor(x,y); const svg=document.getElementById("whenDial"); svg.dispatchEvent(new PointerEvent("pointermove",{bubbles:true,clientX:x,clientY:y,pointerId:1,pointerType:"mouse"})); await sleep(28); } const svg=document.getElementById("whenDial"); svg.dispatchEvent(new PointerEvent("pointerup",{bubbles:true,clientX:px,clientY:py,pointerId:1,pointerType:"mouse"})); await sleep(1200); }
      await sweep("#whenMonths svg",.1,.95,.55,2600); await scrollTo("#whenEid",-200); await sweep("#whenEid svg",.1,.9,.6,2400); },
    async()=>{ await scrollTo("#roads"); await say("Chapter 6: three percent of the network, two thirds of the crashes."); await sweep("#roadsChart svg",.32,.9,.35,2400); await scrollTo("#roadsMonthly",-200); await sweep("#roadsMonthly svg",.1,.95,.6,2600); },
    async()=>{ await scrollTo("#method"); await say("Chapter 7: every number links to its source. Read the disclaimer before quoting."); await sleep(1200); await scrollTo("#disclaimer",-110,1500); await sleep(3200); await say(""); await scrollTo("#top",0,1600); }
  ];
  async function run(){ if(running) return; running=true; stop=false; const my=++token; btn.textContent="Stop tour"; document.body.classList.add("touring"); document.documentElement.style.scrollBehavior="auto"; setCursor(innerWidth*0.6,innerHeight*0.7);
    for(const step of script){ if(stop||my!==token) break; try{ await step(); }catch(e){ console.warn("tour step",e); } }
    end(); }
  function end(){ if(!running) return; running=false; stop=true; btn.textContent="Watch tour"; document.body.classList.remove("touring"); document.documentElement.style.scrollBehavior=""; cap.classList.remove("show"); }
  btn.addEventListener("click", e=>{ e.stopPropagation(); if(running) end(); else run(); });
  // any real input hands control back
  ["wheel","keydown","mousedown","touchstart","pointerdown"].forEach(t=>window.addEventListener(t, e=>{ if(running && e.isTrusted && !(e.target&&e.target.id==="tourBtn")) end(); }, {capture:true,passive:true}));
  window.addEventListener("mousemove", e=>{ if(running && e.isTrusted && (Math.abs(e.clientX-px)>40||Math.abs(e.clientY-py)>40)) end(); }, {capture:true,passive:true});
  if(q.get("tour")==="1") setTimeout(run, 1500);
  else if(auto){ let idle=true; const cancel=()=>{ idle=false; }; ["wheel","keydown","mousedown","touchstart","mousemove"].forEach(t=>window.addEventListener(t,cancel,{once:true,passive:true})); setTimeout(()=>{ if(idle && scrollY<40) run(); }, 3500); }
}
