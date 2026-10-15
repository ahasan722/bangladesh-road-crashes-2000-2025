import { fmt, C } from "./util.js";

// Night highway in one-point perspective. The road recedes to a vanishing point; lane dashes and
// headlight streaks move toward the viewer; the roadside milestones are the years, their height the death toll.
export function initHero(national, spots){
  const svg=d3.select("#heroRoad");
  const years=d3.range(2000,2026);
  const by=(src)=>Object.fromEntries(national.filter(r=>r.source===src&&r.deaths!=null).map(r=>[r.year,r.deaths]));
  const police=by("Police/BRTA"), bjks=by("BJKS"), rsf=by("RSF"), who=by("WHO estimate");
  const reduced=matchMedia("(prefers-reduced-motion: reduce)").matches;
  let raf=null;
  function draw(){
    if(raf) cancelAnimationFrame(raf);
    const el=document.querySelector(".hero"); const w=el.clientWidth, h=el.clientHeight; svg.attr("viewBox",`0 0 ${w} ${h}`).selectAll("*").remove();
    const defs=svg.append("defs");
    const sky=defs.append("linearGradient").attr("id","skyg").attr("x1",0).attr("y1",0).attr("x2",0).attr("y2",1);
    sky.append("stop").attr("offset",0).attr("stop-color","#15181C"); sky.append("stop").attr("offset",.62).attr("stop-color","#2A2F37"); sky.append("stop").attr("offset",1).attr("stop-color","#3A3630");
    const tar=defs.append("linearGradient").attr("id","targ").attr("x1",0).attr("y1",0).attr("x2",0).attr("y2",1);
    tar.append("stop").attr("offset",0).attr("stop-color","#3B3F45"); tar.append("stop").attr("offset",1).attr("stop-color","#15171A");
    const glow=defs.append("radialGradient").attr("id","hglow"); glow.append("stop").attr("offset",0).attr("stop-color","#F5B335").attr("stop-opacity",.55); glow.append("stop").attr("offset",1).attr("stop-color","#F5B335").attr("stop-opacity",0);
    const blur=defs.append("filter").attr("id","soft"); blur.append("feGaussianBlur").attr("stdDeviation",3);
    // geometry
    const vpx=w*0.58, vpy=h*0.36;           // vanishing point
    const bottomL=w*0.36, bottomR=w*0.98;   // road edges at the bottom (runs off the right edge)
    const L=t=>[vpx+(bottomL-vpx)*t, vpy+(h-vpy)*t], R=t=>[vpx+(bottomR-vpx)*t, vpy+(h-vpy)*t];
    svg.append("rect").attr("width",w).attr("height",h).attr("fill","url(#skyg)");
    // horizon glow (distant town)
    svg.append("ellipse").attr("cx",vpx).attr("cy",vpy).attr("rx",w*0.5).attr("ry",h*0.12).attr("fill","url(#hglow)").attr("opacity",.5);
    // ground
    const gnd=defs.append("linearGradient").attr("id","gndg").attr("x1",0).attr("y1",0).attr("x2",0).attr("y2",1); gnd.append("stop").attr("offset",0).attr("stop-color","#2B3038"); gnd.append("stop").attr("offset",.25).attr("stop-color","#1E2126"); gnd.append("stop").attr("offset",1).attr("stop-color","#17191D");
    svg.append("rect").attr("x",0).attr("y",vpy).attr("width",w).attr("height",h-vpy).attr("fill","url(#gndg)");
    // road
    svg.append("polygon").attr("points",`${vpx},${vpy} ${bottomL},${h} ${bottomR},${h}`).attr("fill","url(#targ)");
    // edge lines
    svg.append("line").attr("x1",vpx).attr("y1",vpy).attr("x2",bottomL).attr("y2",h).attr("stroke","#EDE7D6").attr("stroke-width",2).attr("opacity",.55);
    svg.append("line").attr("x1",vpx).attr("y1",vpy).attr("x2",bottomR).attr("y2",h).attr("stroke","#EDE7D6").attr("stroke-width",2).attr("opacity",.55);
    // lane dashes: drawn as trapezoids along the centre line, perspective-correct spacing
    const dashes=svg.append("g");
    const centre=t=>[(L(t)[0]+R(t)[0])/2, L(t)[1]];
    const nDash=14; const dashEls=[];
    for(let i=0;i<nDash;i++) dashEls.push(dashes.append("polygon").attr("fill",C.marigold).attr("opacity",.9));
    function placeDashes(phase){ // phase 0..1, t grows toward the viewer like a car driving
      dashEls.forEach((d,i)=>{ let u=((i+phase)/nDash); const t0=u*u, t1=Math.min(1,(u+0.35/nDash)*(u+0.35/nDash)); if(t1<=0.02||t0>=1){ d.attr("points",""); return; }
        const c0=centre(t0), c1=centre(t1), w0=3+30*t0, w1=3+30*t1;
        d.attr("points",`${c0[0]-w0/2},${c0[1]} ${c0[0]+w0/2},${c0[1]} ${c1[0]+w1/2},${c1[1]} ${c1[0]-w1/2},${c1[1]}`).attr("opacity",.35+.6*t0); }); }
    // headlight / tail-light streaks: three lanes, moving
    const streaks=svg.append("g").attr("filter","url(#soft)"); const strk=[];
    for(let i=0;i<7;i++){ const lane=i%3; strk.push({el:streaks.append("line").attr("stroke",lane===1?"#F6E7B1":"#FF6A4A").attr("stroke-width",lane===1?3:2.4).attr("stroke-linecap","round"), lane, off:Math.random(), speed:.12+Math.random()*.1}); }
    function placeStreaks(time){ strk.forEach(s=>{ const u=((time*s.speed+s.off)%1); const t0=u*u, t1=Math.min(1,t0+0.06*(0.3+t0)); const lx=s.lane===0?0.22:s.lane===1?0.5:0.78; const p0=[L(t0)[0]+(R(t0)[0]-L(t0)[0])*lx, L(t0)[1]-2-18*t0], p1=[L(t1)[0]+(R(t1)[0]-L(t1)[0])*lx, L(t1)[1]-2-18*t1]; s.el.attr("x1",p0[0]).attr("y1",p0[1]).attr("x2",p1[0]).attr("y2",p1[1]).attr("opacity",.15+.6*t0); }); }
    // milestones: one per year along the left verge, spaced in perspective, height = deaths
    const maxD=d3.max(years,y=>Math.max(bjks[y]||0,rsf[y]||0,police[y]||0))||1;
    const g=svg.append("g");
    years.forEach((y,i)=>{ const u=0.08+0.92*((i+1)/years.length); const t=u*u; if(t<0.03) return;
      const p=R(t); const scale=0.3+1.4*t; const base=[p[0]+10*scale, p[1]]; if(base[0]>w-8) return;
      const media=bjks[y]??rsf[y], pol=police[y];
      const hm=media? (media/maxD)*h*0.22*scale : 0, hp=pol? (pol/maxD)*h*0.22*scale : 0;
      // post
      g.append("rect").attr("x",base[0]-1.2*scale).attr("y",base[1]-Math.max(hm,hp,8*scale)).attr("width",2.4*scale).attr("height",Math.max(hm,hp,8*scale)).attr("fill","#EDE7D6").attr("opacity",.35);
      if(media) g.append("rect").attr("x",base[0]-3.5*scale).attr("y",base[1]-hm).attr("width",7*scale).attr("height",hm).attr("fill",C.vermilion).attr("opacity",.9).attr("rx",1.2*scale);
      if(pol) g.append("rect").attr("x",base[0]-1.6*scale).attr("y",base[1]-hp).attr("width",3.2*scale).attr("height",hp).attr("fill","#F6E7B1").attr("opacity",.95);
      if(scale>0.7) g.append("text").attr("x",base[0]).attr("y",base[1]+13*Math.min(1.6,scale)).attr("text-anchor","middle").attr("fill",C.chalk).attr("opacity",.8).attr("font-size",9*Math.min(1.6,scale)).attr("font-weight",700).text(y%5===0?y:"’"+String(y).slice(2));
    });
    // key
    if(w<760){ if(reduced){ placeDashes(0); placeStreaks(0); return; } const t00=performance.now(); (function tick(now){ const s=(now-t00)/1000; placeDashes((s*0.9)%1); placeStreaks(s); raf=requestAnimationFrame(tick); })(t00); return; }
    const kx=w*0.66, ky=vpy-46;
    g.append("rect").attr("x",kx).attr("y",ky-9).attr("width",10).attr("height",10).attr("fill",C.vermilion); g.append("text").attr("x",kx+16).attr("y",ky).attr("fill",C.dust).attr("font-size",12).text("deaths counted by media monitors (BJKS, RSF)");
    g.append("rect").attr("x",kx).attr("y",ky+9).attr("width",10).attr("height",10).attr("fill","#F6E7B1"); g.append("text").attr("x",kx+16).attr("y",ky+18).attr("fill",C.dust).attr("font-size",12).text("deaths in police records");
    g.append("text").attr("x",kx).attr("y",ky+38).attr("fill",C.dust).attr("font-size",11).attr("opacity",.8).text("one milestone a year: 2000 at the horizon, 2025 nearest");
    if(reduced){ placeDashes(0); placeStreaks(0); return; }
    const t0=performance.now(); (function tick(now){ const s=(now-t0)/1000; placeDashes((s*0.9)%1); placeStreaks(s); raf=requestAnimationFrame(tick); })(t0);
  }
  draw(); window.addEventListener("resize", draw);
  const lastRSF=Math.max(...Object.keys(rsf).map(Number)), lastPol=Math.max(...Object.keys(police).map(Number)), lastWHO=Math.max(...Object.keys(who).map(Number));
  document.getElementById("heroMeta").innerHTML=`
    <div><b class="num">${fmt(police[lastPol])}</b>deaths in police records, ${lastPol}</div>
    <div><b class="num red">${fmt(rsf[lastRSF])}</b>deaths counted by the Road Safety Foundation, ${lastRSF}</div>
    <div><b class="num yel">${fmt(who[lastWHO])}</b>deaths estimated by the WHO, ${lastWHO}</div>
    <div><b class="num">${fmt(spots.length)}</b>listed hazardous locations on nine highways</div>`;
}
