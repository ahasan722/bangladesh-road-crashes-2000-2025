import { fmt, fmt1, chips, tip, relPos, sizeOf, onResize, C } from "./util.js";

const CLASSES=["National highway","Regional highway","Feeder / rural road","City road","Other"];
const CCOL={"National highway":C.vermilion,"Regional highway":C.ember,"Feeder / rural road":C.marigold,"City road":C.steel,"Other":C.gravel};

export function initRoads(roads){
  const T=tip(document.getElementById("roadsTip"));
  // keep annual + multi-year + Eid shares for the comparison chart, drop unknown periods
  const shares=roads.shares.filter(s=>!/unknown/.test(s.period) && !/^\d{4}-\d{2}$/.test(s.period));
  const srcs=[...new Set(shares.map(s=>s.source))]; let active=srcs.slice();
  chips(document.getElementById("roadsSources"), srcs, {onChange:v=>{active=v; drawShares();}});
  document.getElementById("roadsSub").textContent="Each bar is one published table (annual, multi-year or Eid window). Monthly tables are in the lower chart.";
  function drawShares(){
    const box=document.getElementById("roadsChart"); box.innerHTML="";
    const rows=shares.filter(s=>active.includes(s.source)).sort((a,b)=>a.period.localeCompare(b.period));
    const {w}=sizeOf(box), bh=26, m={t:8,r:16,b:52,l:190}, h=rows.length*bh+m.t+m.b;
    const svg=d3.select(box).append("svg").attr("width",w).attr("height",h);
    const x=d3.scaleLinear().domain([0,100]).range([m.l,w-m.r]);
    rows.forEach((r,i)=>{ let acc=0; const g=svg.append("g").attr("transform",`translate(0,${m.t+i*bh})`);
      g.append("text").attr("x",m.l-8).attr("y",bh/2).attr("dy","0.35em").attr("text-anchor","end").attr("fill",C.chalk).attr("font-size",11.5).text(`${r.source} ${r.label}`);
      CLASSES.forEach(c=>{ const v=r.shares[c]||0; if(!v) return; g.append("rect").attr("x",x(acc)).attr("y",3).attr("height",bh-8).attr("width",x(acc+v)-x(acc)).attr("fill",CCOL[c])
        .on("mousemove",ev=>{ const [px,py]=relPos(ev,box.parentElement); T.show(`<b>${c}</b><div>${fmt1(v)}% of crashes</div><div class="muted">${r.source}, ${r.label}</div>${r.sources[0]?`<div><a href="${r.sources[0]}" target="_blank">source</a></div>`:""}`,px,py); }).on("mouseleave",()=>T.hide());
        if(x(acc+v)-x(acc)>34) g.append("text").attr("x",x(acc+(v/2))).attr("y",bh/2).attr("dy","0.35em").attr("text-anchor","middle").attr("fill","#1F2327").attr("font-size",10.5).attr("font-weight",700).text(Math.round(v)+"%"); acc+=v; }); });
    svg.append("g").attr("class","axis").attr("transform",`translate(0,${h-m.b+4})`).call(d3.axisBottom(x).ticks(5).tickFormat(d=>d+"%"));
    // legend
    const lg=svg.append("g").attr("transform",`translate(${m.l},${h-6})`); let lx=0; CLASSES.forEach(c=>{ lg.append("rect").attr("x",lx).attr("y",-8).attr("width",10).attr("height",10).attr("fill",CCOL[c]); lg.append("text").attr("x",lx+14).attr("y",0).attr("fill",C.dust).attr("font-size",11).text(c); lx+=c.length*6.4+30; });
  }
  drawShares(); onResize(drawShares);

  // network km: RHD 2021 + LGED latest
  const net=roads.network; const rhd=net.filter(n=>n.agency==="RHD"&&String(n.year)==="2021"); const lged=net.filter(n=>n.agency==="LGED").sort((a,b)=>String(b.year).localeCompare(String(a.year)));
  const lgedLatestYear=lged[0]?.year; const lg2=lged.filter(n=>n.year===lgedLatestYear);
  const nb=document.getElementById("roadsNetwork"); nb.innerHTML="";
  const km=[{c:"National highway",v:rhd.find(n=>n.road_class==="national")?.length_km,src:"RHD 2021 (ADB)"},{c:"Regional highway",v:rhd.find(n=>n.road_class==="regional")?.length_km,src:"RHD 2021 (ADB)"},{c:"Zilla road (RHD)",v:rhd.find(n=>n.road_class==="zilla")?.length_km,src:"RHD 2021 (ADB)"},
    {c:"Upazila road (LGED)",v:lg2.find(n=>n.road_class==="upazila")?.length_km,src:`LGED ${lgedLatestYear}`},{c:"Union road (LGED)",v:lg2.find(n=>n.road_class==="union")?.length_km,src:`LGED ${lgedLatestYear}`},{c:"Village road (LGED)",v:lg2.find(n=>n.road_class==="village")?.length_km,src:`LGED ${lgedLatestYear}`}].filter(d=>d.v);
  (function(){ const {w}=sizeOf(nb), bh=30, h=km.length*bh+30, lw=170; const svg=d3.select(nb).append("svg").attr("width",w).attr("height",h);
    const x=d3.scaleLog().domain([1000,d3.max(km,d=>d.v)*1.3]).range([lw,w-100]);
    km.forEach((d,i)=>{ const g=svg.append("g").attr("transform",`translate(0,${i*bh})`); g.append("text").attr("x",lw-8).attr("y",bh/2).attr("dy","0.35em").attr("text-anchor","end").attr("fill",C.chalk).attr("font-size",12).text(d.c);
      g.append("rect").attr("x",x(1000)).attr("y",5).attr("height",bh-11).attr("width",x(d.v)-x(1000)).attr("fill",CCOL[d.c]||(d.c.includes("LGED")?C.moss:C.sky)).attr("rx",2); g.append("text").attr("x",x(d.v)+6).attr("y",bh/2).attr("dy","0.35em").attr("fill",C.dust).attr("font-size",11.5).text(`${fmt(Math.round(d.v))} km`); });
    svg.append("text").attr("x",lw).attr("y",h-6).attr("fill",C.dust).attr("font-size",11).text("Log scale. RHD 2021 via ADB; LGED latest published."); })();

  // intensity: share of crashes ÷ share of km (RHD classes only, 2024 RSF + 2014-24 BJKS)
  const ib=document.getElementById("roadsIntensity"); ib.innerHTML="";
  const kmN=rhd.find(n=>n.road_class==="national")?.length_km, kmR=rhd.find(n=>n.road_class==="regional")?.length_km, kmZ=rhd.find(n=>n.road_class==="zilla")?.length_km, kmL=lg2.reduce((a,n)=>a+(n.length_km||0),0);
  const totKm=kmN+kmR+kmZ+kmL;
  const cmp=shares.filter(s=>/^(20\d\d|2014 to)/.test(s.label)||/^\d{4}$/.test(s.label)).slice(-6);
  const rowsI=cmp.map(s=>({label:`${s.source} ${s.label}`, vals:[{c:"National highway",r:(s.shares["National highway"]||0)/(kmN/totKm*100)},{c:"Regional highway",r:(s.shares["Regional highway"]||0)/(kmR/totKm*100)},{c:"Feeder / rural road",r:(s.shares["Feeder / rural road"]||0)/((kmZ+kmL)/totKm*100)}]}));
  (function(){ const {w}=sizeOf(ib), h=rowsI.length*54+40, lw=180; const svg=d3.select(ib).append("svg").attr("width",w).attr("height",h);
    const x=d3.scaleLog().domain([0.05,200]).range([lw,w-20]);
    svg.append("line").attr("x1",x(1)).attr("x2",x(1)).attr("y1",0).attr("y2",h-30).attr("stroke",C.chalk).attr("stroke-dasharray","3 4");
    svg.append("text").attr("x",x(1)+4).attr("y",10).attr("fill",C.dust).attr("font-size",11).text("1 = crashes in proportion to length");
    rowsI.forEach((r,i)=>{ const g=svg.append("g").attr("transform",`translate(0,${16+i*54})`); g.append("text").attr("x",lw-8).attr("y",22).attr("text-anchor","end").attr("fill",C.chalk).attr("font-size",11.5).text(r.label);
      r.vals.forEach((v,j)=>{ g.append("rect").attr("x",x(Math.min(0.05,v.r))).attr("y",j*14).attr("height",11).attr("width",Math.max(0,x(Math.max(0.05,v.r))-x(0.05))).attr("fill",CCOL[v.c]); g.append("text").attr("x",x(Math.max(0.05,v.r))+5).attr("y",j*14+9).attr("fill",C.dust).attr("font-size",10.5).text(`${v.c.split(" ")[0]} ×${fmt1(v.r)}`); }); });
    svg.append("text").attr("x",lw).attr("y",h-8).attr("fill",C.dust).attr("font-size",11).text(`Network: RHD national ${fmt(kmN)} km, regional ${fmt(kmR)} km, zilla ${fmt(kmZ)} km, LGED ${fmt(Math.round(kmL))} km. Log scale.`); })();

  // monthly stacked counts
  const mb=document.createElement("div"); mb.className="chartbox"; mb.style.marginTop="18px"; mb.innerHTML=`<h3>Crashes per month by road class</h3><div class="sub">RSF monthly reports where the road-class table was reproduced in the press (${roads.monthly_counts.length} months)</div><div id="roadsMonthly"></div>`;
  document.getElementById("roadsIntensity").parentElement.after(mb);
  (function(){ const box=document.getElementById("roadsMonthly"); const rows=roads.monthly_counts; const {w}=sizeOf(box), h=300, m={t:12,r:16,b:50,l:44};
    const svg=d3.select(box).append("svg").attr("width",w).attr("height",h); const x=d3.scaleBand().domain(rows.map(r=>r.period)).range([m.l,w-m.r]).padding(.15);
    const y=d3.scaleLinear().domain([0,d3.max(rows,r=>d3.sum(Object.values(r.counts)))*1.08]).range([h-m.b,m.t]).nice();
    svg.append("g").attr("class","grid").selectAll("line").data(y.ticks(5)).join("line").attr("x1",m.l).attr("x2",w-m.r).attr("y1",d=>y(d)).attr("y2",d=>y(d));
    svg.append("g").attr("class","axis").attr("transform",`translate(0,${h-m.b})`).call(d3.axisBottom(x).tickFormat(p=>rows.find(r=>r.period===p).label)).selectAll("text").attr("transform","rotate(-45)").attr("text-anchor","end").attr("font-size",10);
    svg.append("g").attr("class","axis").attr("transform",`translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5));
    let lx=m.l; CLASSES.forEach(c=>{ svg.append("rect").attr("x",lx).attr("y",2).attr("width",10).attr("height",10).attr("fill",CCOL[c]); svg.append("text").attr("x",lx+14).attr("y",11).attr("fill",C.dust).attr("font-size",11).text(c); lx+=c.length*6.4+30; });
    rows.forEach(r=>{ let acc=0; CLASSES.forEach(c=>{ const v=r.counts[c]||0; if(!v) return; svg.append("rect").attr("x",x(r.period)).attr("width",x.bandwidth()).attr("y",y(acc+v)).attr("height",y(acc)-y(acc+v)).attr("fill",CCOL[c])
      .on("mousemove",ev=>{ const [px,py]=relPos(ev,box.parentElement); T.show(`<b>${r.label}</b><div>${c}: ${fmt(v)} crashes</div><div class="muted">month total ${fmt(d3.sum(Object.values(r.counts)))}</div>`,px,py); }).on("mouseleave",()=>T.hide()); acc+=v; }); }); })();

  document.getElementById("roadsNote").innerHTML=`BJKS reports national, regional and feeder shares; RSF reports national, regional, rural and city. "Feeder / rural road" merges BJKS feeder and RSF rural; "City road" merges Dhaka and Chattogram city rows. The intensity chart divides a source's crash share by the class's share of the combined RHD + LGED network length, so it is a rough length-normalised comparison, not a risk rate: traffic volumes differ by orders of magnitude between a national highway and a village road.`;
  document.getElementById("roadsTakeaway").innerHTML=`<b>National highways are about 1.2% of the road network and carry about a third of reported crashes.</b> Regional highways, 1.5% of the network, carry another third. The remaining 97% of kilometres, the zilla, upazila, union and village roads that most Bangladeshis live on, produce the last third, which is where the motorcycles and three-wheelers die.`;
}
