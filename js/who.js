import { fmt, fmt1, seg, chips, tip, relPos, sizeOf, onResize, C, glowDefs } from "./util.js";

const CAT = {
  motorcycle:{l:"Motorcycle", c:C.vermilion}, three_wheeler:{l:"Three-wheeler (CNG, easy-bike)", c:C.ember}, local_three_wheeler:{l:"Three-wheeler", c:C.ember},
  pedestrian:{l:"Pedestrian", c:C.marigold}, drivers_helpers:{l:"Driver and helper", c:C.steel}, truck_pickup_goods:{l:"Truck, pickup, lorry", c:"#8A6E5A"},
  bus:{l:"Bus", c:C.sky}, car_microbus:{l:"Car, microbus, SUV", c:"#B9A98C"}, local_vehicle:{l:"Nosimon, korimon, vatvoti", c:"#C99BD6"}, bicycle_rickshaw:{l:"Bicycle and rickshaw", c:C.moss},
  women:{l:"Women", c:"#E58FA0"}, children:{l:"Children", c:"#F4D27A"}, students:{l:"Students", c:"#F4D27A"}, working_age_18_65:{l:"Working age 18–65", c:C.dust}, motorcycle_all:{l:"Motorcycle", c:C.vermilion}
};
const lab=k=>CAT[k]?CAT[k].l:k.replace(/_/g," ");
const col=k=>CAT[k]?CAT[k].c:"#999";

export function initWho(who){
  const box=document.getElementById("whoChart"), T=tip(document.getElementById("whoTip"));
  const years=Object.keys(who.rsf_totals_deaths).map(Number).sort();
  // series shown over years: motorcycle deaths, pedestrians, women, children, drivers+helpers, all deaths
  const SER=["motorcycle","pedestrian","drivers_helpers","women","children"];
  const get=(y,k)=> k==="motorcycle" ? (who.veh_counts[y]||{}).motorcycle : (who.victims[y]||{})[k];
  let active=SER.slice(), mode="stack";
  chips(document.getElementById("whoCats"), SER, {initial:SER, colors:col, onChange:v=>{active=v; draw();}}).set(SER);
  document.getElementById("whoCats").querySelectorAll(".chip").forEach((b,i)=>b.innerHTML=`<span class="dot" style="background:${col(SER[i])}"></span>${lab(SER[i])}`);
  const modeEl=document.getElementById("whoMode"); modeEl.innerHTML=`<button data-v="stack" class="on">Counts</button><button data-v="share">Share of all deaths</button>`;
  seg(modeEl, v=>{mode=v; draw();});
  const srcSel=document.getElementById("whoSource"); srcSel.style.display="none";
  function draw(){
    box.innerHTML="";
    const {w}=sizeOf(box), h=380, m={t:16,r:170,b:34,l:56};
    const svg=d3.select(box).append("svg").attr("width",w).attr("height",h);
    const x=d3.scalePoint().domain(years).range([m.l,w-m.r]);
    const vals=years.flatMap(y=>active.map(k=>{ const v=get(y,k); return v==null?null:(mode==="share"? v/who.rsf_totals_deaths[y]*100 : v); })).filter(v=>v!=null);
    const y=d3.scaleLinear().domain([0,(d3.max(vals)||1)*1.1]).range([h-m.b,m.t]).nice();
    svg.append("g").attr("class","grid").selectAll("line").data(y.ticks(5)).join("line").attr("x1",m.l).attr("x2",w-m.r).attr("y1",d=>y(d)).attr("y2",d=>y(d));
    svg.append("g").attr("class","axis").attr("transform",`translate(0,${h-m.b})`).call(d3.axisBottom(x));
    svg.append("g").attr("class","axis").attr("transform",`translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickFormat(d=>mode==="share"?d+"%":d3.format("~s")(d)));
    // total deaths as a grey context line in count mode
    if(mode==="stack"){ const tot=years.map(yy=>({year:yy,v:who.rsf_totals_deaths[yy]})); const yt=d3.scaleLinear().domain([0,d3.max(tot,d=>d.v)*1.05]).range([h-m.b,m.t]);
      svg.append("path").attr("d",d3.line().x(d=>x(d.year)).y(d=>yt(d.v))(tot)).attr("fill","none").attr("stroke",C.gravel).attr("stroke-width",10).attr("stroke-linecap","round").attr("opacity",.6);
      svg.append("text").attr("x",x(years[0])+14).attr("y",yt(tot[0].v)-14).attr("fill",C.dust).attr("font-size",11).text(`grey band: all deaths counted by RSF, ${fmt(tot[0].v)} in ${years[0]} to ${fmt(tot[tot.length-1].v)} in ${years[years.length-1]} (own scale)`); }
    const line=d3.line().defined(d=>d.v!=null).x(d=>x(d.year)).y(d=>y(d.v)).curve(d3.curveMonotoneX);
    const glow=glowDefs(svg,"whoglow"); const labels=[];
    active.forEach(k=>{ const pts=years.map(yy=>{ const v=get(yy,k); return {year:yy, v: v==null?null:(mode==="share"? v/who.rsf_totals_deaths[yy]*100 : v), raw:v}; });
      svg.append("path").attr("d",line(pts)).attr("fill","none").attr("stroke",col(k)).attr("stroke-width",7).attr("stroke-opacity",.18).attr("filter",glow);
      svg.append("path").attr("d",line(pts)).attr("fill","none").attr("stroke",col(k)).attr("stroke-width",2.6);
      svg.selectAll(null).data(pts.filter(p=>p.v!=null)).join("circle").attr("cx",d=>x(d.year)).attr("cy",d=>y(d.v)).attr("r",4).attr("fill","#262B30").attr("stroke",col(k)).attr("stroke-width",2)
        .on("mousemove",(ev,d)=>{ const [px,py]=relPos(ev,box.parentElement); T.show(`<b>${lab(k)}, ${d.year}</b><div>${fmt(d.raw)} deaths</div><div>${fmt1(d.raw/who.rsf_totals_deaths[d.year]*100)}% of ${fmt(who.rsf_totals_deaths[d.year])} deaths counted by RSF</div>`,px,py); }).on("mouseleave",()=>T.hide());
      const last=[...pts].reverse().find(p=>p.v!=null); if(last) labels.push({k,y:y(last.v),x:x(last.year)}); });
    labels.sort((a,b)=>a.y-b.y); for(let i=1;i<labels.length;i++) if(labels[i].y-labels[i-1].y<14) labels[i].y=labels[i-1].y+14;
    labels.forEach(l=>svg.append("text").attr("x",l.x+8).attr("y",l.y).attr("dy","0.35em").attr("fill",col(l.k)).attr("font-size",12).attr("font-weight",700).text(lab(l.k)));
    // gaps notice
    const miss=active.flatMap(k=>years.filter(yy=>get(yy,k)==null).map(yy=>`${lab(k)} ${yy}`));
    document.getElementById("whoNote").innerHTML=`Road Safety Foundation annual figures, 2020–2025. ${miss.length?`Not published in the press for: ${miss.join(", ")}; the line breaks there instead of guessing.`:""} Motorcycle deaths from BJKS for comparison: ${Object.entries(who.bjks_moto_deaths).map(([yy,v])=>`${yy}: ${fmt(v)}`).join(", ")||"none"}.`;
  }
  draw(); onResize(draw);

  // victims 2024 bar: full 7-class vehicle breakdown
  const vy=Object.keys(who.veh_counts).map(Number).filter(yy=>Object.keys(who.veh_counts[yy]).length>=6).sort().pop();
  const vb=document.getElementById("whoVictim"); vb.previousElementSibling.textContent=`Deaths by the victim's vehicle, RSF ${vy}. One figure is 100 people.`;
  const isoRows=Object.entries(who.veh_counts[vy]).filter(([k])=>k!=="bus_truck_car_combined"); if(who.victims[vy]&&who.victims[vy].pedestrian) isoRows.push(["pedestrian",who.victims[vy].pedestrian]);
  isotype(vb, isoRows.sort((a,b)=>b[1]-a[1]).map(([k,v])=>({k,label:lab(k),v,share:v/who.rsf_totals_deaths[vy]*100,c:col(k)})), who.rsf_totals_deaths[vy]);
  // collision types pooled from RSF monthly
  const cp=who.collision_pooled_rsf, tot=Object.values(cp).reduce((a,b)=>a+b,0);
  const cb=document.getElementById("whoCollision"); cb.previousElementSibling.textContent=`Crashes by collision type, pooled from ${who.collision_months.length} months of RSF monthly reports (${who.collision_months[0]} to ${who.collision_months[who.collision_months.length-1]})`;
  const CL={lost_control:"Lost control, overturned, ran off road",head_on:"Head-on",hit_pedestrian:"Hit a pedestrian",rear_end:"Rear-end",other:"Other"};
  hbars(cb, Object.entries(cp).sort((a,b)=>b[1]-a[1]).map(([k,v])=>({k,label:CL[k]||k,v,share:v/tot*100,c:C.steel})), "crashes");
  const m24=who.veh_counts[vy].motorcycle, mshare=m24/who.rsf_totals_deaths[vy]*100;
  document.getElementById("whoTakeaway").innerHTML=`<b>Motorcycle deaths nearly doubled between 2020 and 2022</b> and have stayed above 2,400 a year since: in ${vy} they were ${fmt(m24)}, ${fmt1(mshare)}% of all deaths the Road Safety Foundation counted. Pedestrians are the second group every year. Buses, the vehicle the public blames most, account for about 5% of the dead.`;
}

function hbars(el, rows, unit){
  el.innerHTML=""; const w=el.clientWidth||400, bh=24, h=rows.length*bh+8, lw=Math.min(250,w*0.48);
  const svg=d3.select(el).append("svg").attr("width",w).attr("height",h);
  const x=d3.scaleLinear().domain([0,d3.max(rows,r=>r.v)]).range([0,w-lw-96]);
  const g=svg.selectAll("g").data(rows).join("g").attr("transform",(d,i)=>`translate(0,${i*bh+4})`);
  g.append("text").attr("x",lw-8).attr("y",bh/2).attr("dy","0.35em").attr("text-anchor","end").attr("fill",C.chalk).attr("font-size",11.5).text(d=>d.label);
  g.append("rect").attr("x",lw).attr("y",3).attr("height",bh-8).attr("width",d=>x(d.v)).attr("fill",d=>d.c).attr("rx",2);
  g.append("text").attr("x",d=>lw+x(d.v)+6).attr("y",bh/2).attr("dy","0.35em").attr("fill",C.dust).attr("font-size",11.5).text(d=>`${fmt(d.v)} (${fmt1(d.share)}%)`);
}

// original pictograms, drawn as 24x24 paths
const ICON={
  motorcycle:"M4 16a3 3 0 1 0 6 0 3 3 0 0 0-6 0Zm10 0a3 3 0 1 0 6 0 3 3 0 0 0-6 0ZM7 13l3-5h4l2 3h3l-1 2h-3l-2-2h-2l-2 2Zm6-8h4l1 2h-4Z",
  three_wheeler:"M5 17a2.5 2.5 0 1 0 5 0 2.5 2.5 0 0 0-5 0Zm9 0a2.5 2.5 0 1 0 5 0 2.5 2.5 0 0 0-5 0ZM4 15V9a3 3 0 0 1 3-3h7l4 5v4h-1.5a3.5 3.5 0 0 0-7 0h-1a3.5 3.5 0 0 0-4.5-3.3ZM8 8v3h5V8Z",
  local_three_wheeler:"M5 17a2.5 2.5 0 1 0 5 0 2.5 2.5 0 0 0-5 0Zm9 0a2.5 2.5 0 1 0 5 0 2.5 2.5 0 0 0-5 0ZM4 15V9a3 3 0 0 1 3-3h7l4 5v4h-1.5a3.5 3.5 0 0 0-7 0h-1a3.5 3.5 0 0 0-4.5-3.3ZM8 8v3h5V8Z",
  pedestrian:"M12 2.5a2 2 0 1 1 0 4 2 2 0 0 1 0-4ZM9 8h6l2 5-2 .6-1.2-2.6V15l2.5 6h-2.4l-2.4-5-1.5 2.2V21H8v-4l2-4V11l-1.5 2.6L6.5 13Z",
  drivers_helpers:"M12 2.5a2 2 0 1 1 0 4 2 2 0 0 1 0-4ZM8 8h8v5h-2v8h-4v-8H8Z",
  truck_pickup_goods:"M2 7h11v9H2Zm11 3h5l3 3v3h-8ZM5 19a2 2 0 1 0 4 0 2 2 0 0 0-4 0Zm10 0a2 2 0 1 0 4 0 2 2 0 0 0-4 0Z",
  bus:"M3 5h18v11h-1a2.5 2.5 0 0 0-5 0H9a2.5 2.5 0 0 0-5 0H3Zm2 2v4h4V7Zm6 0v4h4V7Zm6 0v4h2V7ZM4 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0Zm12 0a2 2 0 1 0 4 0 2 2 0 0 0-4 0Z",
  car_microbus:"M3 11l3-5h12l3 5v5h-2a2.5 2.5 0 0 0-5 0H9a2.5 2.5 0 0 0-5 0H3Zm4-3-1.5 3h13L17 8ZM4 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0Zm12 0a2 2 0 1 0 4 0 2 2 0 0 0-4 0Z",
  local_vehicle:"M2 9h4l2-3h6v5h7v5h-2a2.5 2.5 0 0 0-5 0H9a2.5 2.5 0 0 0-5 0H2Zm2 8a2 2 0 1 0 4 0 2 2 0 0 0-4 0Zm10 0a2 2 0 1 0 4 0 2 2 0 0 0-4 0Z",
  bicycle_rickshaw:"M3 16a3 3 0 1 0 6 0 3 3 0 0 0-6 0Zm12 0a3 3 0 1 0 6 0 3 3 0 0 0-6 0ZM6 16l4-7h5l3 7h-2l-2.3-5h-3L8 16Zm3-11h5v2h-5Z"
};
function isotype(el, rows, total){
  const per=100; el.innerHTML="";
  const wrap=document.createElement("div"); wrap.className="iso";
  rows.forEach(r=>{ const lab=document.createElement("div"); lab.className="lab"; lab.innerHTML=`${r.label}<small>${fmt(r.v)} (${fmt1(r.share)}%)</small>`;
    const row=document.createElement("div"); row.className="row"; const n=r.v/per; const full=Math.floor(n), half=(n-full)>=0.5;
    const path=ICON[r.k]||ICON.drivers_helpers;
    for(let i=0;i<full+(half?1:0);i++){ const svg=document.createElementNS("http://www.w3.org/2000/svg","svg"); svg.setAttribute("viewBox","0 0 24 24"); if(i===full&&half) svg.classList.add("half"); svg.innerHTML=`<path d="${path}" fill="${r.c}"/>`; svg.setAttribute("title",`${r.label}: ${fmt(r.v)} deaths`); row.appendChild(svg); }
    wrap.append(lab,row); });
  const key=document.createElement("div"); key.className="key"; key.textContent=`Each figure stands for ${per} deaths; a half figure for 50. ${fmt(total)} deaths in total.`; wrap.appendChild(key);
  el.appendChild(wrap);
}
