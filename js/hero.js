import { fmt, C } from "./util.js";

export function initHero(national, spots){
  const svg=d3.select("#heroRoad");
  const years=d3.range(2000,2026);
  const by=(src)=>Object.fromEntries(national.filter(r=>r.source===src&&r.deaths!=null).map(r=>[r.year,r.deaths]));
  const police=by("Police/BRTA"), bjks=by("BJKS"), rsf=by("RSF"), who=by("WHO estimate");
  function draw(){
    const el=document.querySelector(".hero .road"); const w=el.clientWidth, h=el.clientHeight; svg.attr("viewBox",`0 0 ${w} ${h}`).selectAll("*").remove();
    const roadY=h*0.62, rh=Math.max(70,h*0.22);
    // perspective-less flat road band
    svg.append("rect").attr("class","tar").attr("x",0).attr("y",roadY-rh/2).attr("width",w).attr("height",rh);
    svg.append("line").attr("class","edge").attr("x1",0).attr("x2",w).attr("y1",roadY-rh/2+6).attr("y2",roadY-rh/2+6);
    svg.append("line").attr("class","edge").attr("x1",0).attr("x2",w).attr("y1",roadY+rh/2-6).attr("y2",roadY+rh/2-6);
    const dash=svg.append("line").attr("class","dash").attr("x1",-80).attr("x2",w+80).attr("y1",roadY).attr("y2",roadY);
    // km posts: one per year, height = media-monitored deaths (BJKS/RSF) on top, police as inner post
    const x=d3.scaleLinear().domain([2000,2025]).range([w*0.04,w*0.96]);
    const maxD=d3.max(years,y=>Math.max(bjks[y]||0,rsf[y]||0,police[y]||0))||1;
    const hs=d3.scaleLinear().domain([0,maxD]).range([0,h*0.3]);
    const g=svg.append("g");
    years.forEach(y=>{
      const media=bjks[y]??rsf[y]; const pol=police[y];
      const bx=x(y), base=roadY-rh/2-10;
      if(media) g.append("rect").attr("class","kmpost red").attr("x",bx-5).attr("y",base-hs(media)).attr("width",10).attr("height",hs(media)).attr("opacity",.85);
      if(pol) g.append("rect").attr("class","kmpost").attr("x",bx-2).attr("y",base-hs(pol)).attr("width",4).attr("height",hs(pol));
      g.append("text").attr("x",bx).attr("y",roadY+rh/2+18).attr("text-anchor","middle").attr("opacity",.75).text(y%5===0?y:"’"+String(y).slice(2)).attr("font-size",y%5===0?12:10);
    });
    g.append("text").attr("x",x(2000)).attr("y",roadY-rh/2-hs(maxD)-16).attr("fill",C.vermilion).attr("font-size",12).text("deaths counted by media monitoring (BJKS / RSF)");
    g.append("text").attr("x",x(2000)).attr("y",roadY-rh/2-hs(maxD)-2).attr("fill",C.chalk).attr("opacity",.8).attr("font-size",12).text("deaths in police records");
    // animate the centre line like driving
    if(!matchMedia("(prefers-reduced-motion: reduce)").matches){ let off=0; (function tick(){ off-=1.2; dash.attr("stroke-dashoffset",off); requestAnimationFrame(tick); })(); }
  }
  draw(); window.addEventListener("resize", draw);
  const lastRSF=Math.max(...Object.keys(rsf).map(Number)), lastPol=Math.max(...Object.keys(police).map(Number)), lastWHO=Math.max(...Object.keys(who).map(Number));
  document.getElementById("heroMeta").innerHTML=`
    <div><b class="num">${fmt(police[lastPol])}</b>deaths in police records, ${lastPol}</div>
    <div><b class="num">${fmt(rsf[lastRSF])}</b>deaths counted by the Road Safety Foundation, ${lastRSF}</div>
    <div><b class="num">${fmt(who[lastWHO])}</b>deaths estimated by the WHO, ${lastWHO}</div>
    <div><b class="num">${fmt(spots.length)}</b>listed hazardous locations on nine highways</div>`;
}
