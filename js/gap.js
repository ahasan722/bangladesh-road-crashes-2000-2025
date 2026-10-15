import { fmt, fmt1, seg, chips, tip, relPos, sizeOf, onResize, sourceColor, glowDefs } from "./util.js";

// rows: {year, source, accidents, deaths, injuries, deaths_per_100k, note, citation_url}
export function initGap(rows, population){
  const box=document.getElementById("gapChart"), T=tip(document.getElementById("gapTip"));
  const sources=[...new Set(rows.map(r=>r.source))];
  let measure="deaths", scale="linear", active=sources.slice();
  const key={deaths:"deaths",accidents:"accidents",injuries:"injuries",rate:"deaths_per_100k"};
  const title={deaths:"Deaths",accidents:"Crashes",injuries:"Injuries",rate:"Deaths per 100,000 people"};
  chips(document.getElementById("gapSources"), sources, {colors:sourceColor, onChange:v=>{active=v; draw();}});
  seg(document.getElementById("gapMeasure"), v=>{measure=v; draw();});
  seg(document.getElementById("gapScale"), v=>{scale=v; draw();});
  function draw(){
    box.innerHTML="";
    const {w}=sizeOf(box), h=Math.max(360, Math.min(520, w*0.5)), m={t:18,r:150,b:34,l:62};
    const k=key[measure];
    const series=active.map(s=>({source:s, pts:rows.filter(r=>r.source===s && r[k]!=null && !isNaN(r[k])).map(r=>({year:+r.year, v:+r[k], r})).sort((a,b)=>a.year-b.year)})).filter(s=>s.pts.length);
    const all=series.flatMap(s=>s.pts);
    const svg=d3.select(box).append("svg").attr("width",w).attr("height",h).attr("role","img").attr("aria-label",title[measure]+" by year and source");
    if(!all.length){ svg.append("text").attr("x",w/2).attr("y",h/2).attr("fill","#A9A496").attr("text-anchor","middle").text("No source publishes this measure"); return; }
    const x=d3.scaleLinear().domain([2000,2025]).range([m.l,w-m.r]);
    const ymax=d3.max(all,d=>d.v), ymin=d3.min(all,d=>d.v);
    const y=(scale==="log"? d3.scaleLog().domain([Math.max(1,ymin*0.8), ymax*1.08]) : d3.scaleLinear().domain([0, ymax*1.08])).range([h-m.b,m.t]).nice();
    svg.append("g").attr("class","grid").selectAll("line").data(y.ticks(scale==="log"?4:6)).join("line").attr("x1",m.l).attr("x2",w-m.r).attr("y1",d=>y(d)).attr("y2",d=>y(d));
    svg.append("g").attr("class","axis").attr("transform",`translate(0,${h-m.b})`).call(d3.axisBottom(x).ticks(13).tickFormat(d3.format("d")));
    svg.append("g").attr("class","axis").attr("transform",`translate(${m.l},0)`).call(d3.axisLeft(y).ticks(scale==="log"?4:6).tickFormat(d=>measure==="rate"?fmt1(d):d3.format("~s")(d)));
    const line=d3.line().x(d=>x(d.year)).y(d=>y(d.v)).curve(d3.curveMonotoneX);
    const glow=glowDefs(svg,"gapglow"); const g=svg.append("g");
    // the gap itself: shaded band between the police line and the highest media-monitored count, where both exist
    const pol=series.find(s0=>s0.source==="Police/BRTA"), media=series.filter(s0=>["BJKS","RSF"].includes(s0.source));
    if(pol && media.length && measure!=="rate"){ const band=[]; for(let yr=2000;yr<=2025;yr++){ const p0=pol.pts.find(d=>d.year===yr); const ms=media.map(s0=>s0.pts.find(d=>d.year===yr)).filter(Boolean); if(p0&&ms.length){ const top=d3.max(ms,d=>d.v); if(top>p0.v) band.push({year:yr,lo:p0.v,hi:top}); } }
      if(band.length>1){ const runs=[]; let cur=[band[0]]; for(let i=1;i<band.length;i++){ if(band[i].year-band[i-1].year>1){ runs.push(cur); cur=[]; } cur.push(band[i]); } runs.push(cur);
        runs.forEach(run=>{ if(run.length<2) return; g.append("path").attr("d",d3.area().x(d=>x(d.year)).y0(d=>y(d.lo)).y1(d=>y(d.hi)).curve(d3.curveMonotoneX)(run)).attr("fill",sourceColor("BJKS")).attr("opacity",.13); });
        const mid=band[Math.floor(band.length/2)]; g.append("text").attr("x",x(mid.year)).attr("y",y((mid.lo+mid.hi)/2)).attr("text-anchor","middle").attr("dy","0.35em").attr("fill",sourceColor("BJKS")).attr("font-size",11.5).attr("font-weight",700).attr("opacity",.85).text("deaths the media counted but the police did not"); } }
    series.forEach(s=>{
      const col=sourceColor(s.source);
      // draw gaps as broken segments: split where consecutive years differ by >1
      const runs=[]; let cur=[];
      s.pts.forEach((p,i)=>{ if(i&&p.year-s.pts[i-1].year>1){ runs.push(cur); cur=[]; } cur.push(p); }); runs.push(cur);
      runs.forEach(run=>{ if(run.length>1){ g.append("path").attr("d",line(run)).attr("fill","none").attr("stroke",col).attr("stroke-width",6).attr("stroke-opacity",.18).attr("filter",glow); g.append("path").attr("d",line(run)).attr("fill","none").attr("stroke",col).attr("stroke-width",2.4).attr("stroke-linejoin","round"); } });
      // dotted bridge across gaps
      for(let i=1;i<s.pts.length;i++){ if(s.pts[i].year-s.pts[i-1].year>1){ g.append("line").attr("x1",x(s.pts[i-1].year)).attr("y1",y(s.pts[i-1].v)).attr("x2",x(s.pts[i].year)).attr("y2",y(s.pts[i].v)).attr("stroke",col).attr("stroke-width",1.2).attr("stroke-dasharray","2 5").attr("opacity",.7); } }
      g.selectAll(null).data(s.pts).join("circle").attr("cx",d=>x(d.year)).attr("cy",d=>y(d.v)).attr("r",3.2).attr("fill","#262B30").attr("stroke",col).attr("stroke-width",2);
      const last=s.pts[s.pts.length-1];
      g.append("text").attr("x",x(last.year)+8).attr("y",y(last.v)).attr("dy","0.35em").attr("fill",col).attr("font-size",12).attr("font-weight",700).text(s.source);
    });
    // label collision avoidance (simple): push labels apart
    const labels=g.selectAll("text").nodes().sort((a,b)=>+a.getAttribute("y")-+b.getAttribute("y"));
    for(let i=1;i<labels.length;i++){ const prev=+labels[i-1].getAttribute("y"), cur=+labels[i].getAttribute("y"); if(cur-prev<14) labels[i].setAttribute("y",prev+14); }
    // hover
    const bis=d3.bisector(d=>d.year).center;
    svg.append("rect").attr("x",m.l).attr("y",m.t).attr("width",w-m.l-m.r).attr("height",h-m.t-m.b).attr("fill","transparent")
      .on("mousemove",ev=>{ const [px,py]=relPos(ev,box.parentElement); const yr=Math.round(x.invert(px));
        const items=series.map(s=>{ const p=s.pts.find(d=>d.year===yr); return p?`<div><span style="color:${sourceColor(s.source)}">●</span> ${s.source}: <b>${measure==="rate"?fmt1(p.v):fmt(p.v)}</b>${p.r.note?` <span class="muted">(${p.r.note})</span>`:""}</div>`:""; }).join("");
        if(items.trim()) T.show(`<b>${yr}</b><div>${title[measure]}</div>${items}`, px, py); else T.hide();
        svg.selectAll(".cursor").remove(); svg.append("line").attr("class","cursor").attr("x1",x(yr)).attr("x2",x(yr)).attr("y1",m.t).attr("y2",h-m.b).attr("stroke","#ECE8DF").attr("stroke-opacity",.35).attr("pointer-events","none"); })
      .on("mouseleave",()=>{ T.hide(); svg.selectAll(".cursor").remove(); });
  }
  draw(); onResize(draw);
}
