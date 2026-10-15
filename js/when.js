import { fmt, fmt1, tip, relPos, sizeOf, onResize, ramp, C } from "./util.js";
import { initDial } from "./dial.js";

const BAND_LABEL={dawn:"Dawn (04–06)",morning:"Morning (06–12)",noon:"Midday (12–15)",afternoon:"Afternoon (15–18)",evening:"Evening (18–20)",night:"Night (20–04)"};
const ORDER=["dawn","morning","noon","afternoon","evening","night"];
const BANDS={dawn:[4,6],morning:[6,12],noon:[12,15],afternoon:[15,18],evening:[18,20],night:[20,28]};
const MON=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

export function initWhen(when){
  const T=tip(document.getElementById("whenTip"));
  const periods=[{period:"pooled",label:`Mean of ${when.tod_pooled_n} published periods`,shares:when.tod_pooled},...when.tod_periods.map(p=>({...p, shares:canon(p.shares)}))];
  let pi=0, range=[0,24];
  const sel=document.getElementById("whenYear"); sel.innerHTML=periods.map((p,i)=>`<option value="${i}">${p.label}</option>`).join(""); sel.addEventListener("change",()=>{pi=+sel.value; draw();});
  document.querySelector("#when .rail .ctl .lbl").textContent="Period";
  initDial(document.getElementById("whenDial"), (s,e)=>{ range=[s,e]; draw(); });
  function canon(sh){ const o={}; Object.entries(sh).forEach(([k,v])=>{ const ck={early_morning:"dawn",dusk:"evening",late_afternoon:"afternoon"}[k]||k; o[ck]=(o[ck]||0)+v; }); return o; }
  function overlapHours(band,[s,e]){ // hours of band inside selection, both on 0..48 wrap
    const [b0,b1]=BANDS[band]; let total=0; const sels= s<e? [[s,e]] : (s===e? [[0,24]] : [[s,24],[0,e]]);
    for(const [a0,a1] of sels){ for(const [c0,c1] of [[b0,b1],[b0-24,b1-24]]){ total+=Math.max(0,Math.min(a1,c1)-Math.max(a0,c0)); } }
    return total; }
  function selectedShare(){ const p=periods[pi]; let s=0; ORDER.forEach(b=>{ const sh=p.shares[b]; if(sh==null) return; const hrs=BANDS[b][1]-BANDS[b][0]; s+=sh*overlapHours(b,range)/hrs; }); return s; }
  function draw(){
    const p=periods[pi]; const box=document.getElementById("whenHours"); box.innerHTML="";
    const {w}=sizeOf(box), h=210, m={t:26,r:16,b:30,l:44};
    const svg=d3.select(box).append("svg").attr("width",w).attr("height",h);
    svg.append("text").attr("x",m.l).attr("y",14).attr("fill",C.chalk).attr("font-size",13).attr("font-weight",700).text(`Share of crashes by time of day, ${p.label}`);
    const x=d3.scaleBand().domain(ORDER).range([m.l,w-m.r]).padding(.18);
    const y=d3.scaleLinear().domain([0,d3.max(ORDER,b=>p.shares[b]||0)*1.15]).range([h-m.b,m.t]).nice();
    svg.append("g").attr("class","axis").attr("transform",`translate(0,${h-m.b})`).call(d3.axisBottom(x).tickFormat(b=>BAND_LABEL[b].replace(/ \(.*/,"")));
    svg.append("g").attr("class","axis").attr("transform",`translate(${m.l},0)`).call(d3.axisLeft(y).ticks(4).tickFormat(d=>d+"%"));
    svg.selectAll("rect").data(ORDER).join("rect").attr("x",b=>x(b)).attr("width",x.bandwidth()).attr("y",b=>y(p.shares[b]||0)).attr("height",b=>y(0)-y(p.shares[b]||0))
      .attr("fill",b=>{ const f=overlapHours(b,range)/(BANDS[b][1]-BANDS[b][0]); return f>0? ramp(.45+.55*f) : C.gravel; }).attr("rx",2)
      .on("mousemove",(ev,b)=>{ const [px,py]=relPos(ev,box.parentElement); T.show(`<b>${BAND_LABEL[b]}</b><div>${p.shares[b]!=null?fmt1(p.shares[b])+"% of crashes":"not published"}</div>`,px,py); }).on("mouseleave",()=>T.hide());
    svg.selectAll("text.v").data(ORDER).join("text").attr("class","v").attr("x",b=>x(b)+x.bandwidth()/2).attr("y",b=>y(p.shares[b]||0)-5).attr("text-anchor","middle").attr("fill",C.chalk).attr("font-size",11.5).text(b=>p.shares[b]!=null?fmt1(p.shares[b])+"%":"");
    const [s,e]=range, full=(s%24===e%24)||e-s>=24;
    document.getElementById("whenStats").innerHTML=`<div class="stat yel"><b class="num">${fmt1(selectedShare())}%</b><span>of crashes ${full?"all day":`between ${String(s).padStart(2,"0")}:00 and ${String(e%24).padStart(2,"0")}:00`}</span></div><div class="stat"><b class="num">${fmt1(p.shares.morning||0)}%</b><span>in the morning (06–12)</span></div>`;
    drawMonths();
  }
  function drawMonths(){
    const box=document.getElementById("whenMonths"); box.innerHTML="";
    const rows=when.monthly.filter(r=>r.deaths!=null); const yrs=[...new Set(rows.map(r=>r.year))].sort();
    const {w}=sizeOf(box), cell=Math.min(44,(w-70)/12), h=yrs.length*cell+40;
    const svg=d3.select(box).append("svg").attr("width",w).attr("height",h);
    svg.append("text").attr("x",0).attr("y",14).attr("fill",C.chalk).attr("font-size",13).attr("font-weight",700).text("Deaths per month, RSF monthly reports (grey = month not found in the press)");
    const max=d3.max(rows,r=>r.deaths); const byKey=Object.fromEntries(rows.map(r=>[r.year+"-"+r.month,r]));
    yrs.forEach((yy,i)=>{ svg.append("text").attr("x",0).attr("y",28+i*cell+cell/2).attr("dy","0.35em").attr("fill",C.dust).attr("font-size",11.5).text(yy);
      MON.forEach((mn,j)=>{ const r=byKey[yy+"-"+(j+1)]; const g=svg.append("g");
        g.append("rect").attr("x",40+j*cell).attr("y",28+i*cell).attr("width",cell-3).attr("height",cell-3).attr("rx",3).attr("fill",r?ramp(r.deaths/max):C.gravel).attr("opacity",r?1:.5)
          .on("mousemove",ev=>{ const [px,py]=relPos(ev,box.parentElement); T.show(r?`<b>${mn} ${yy}</b><div>${fmt(r.deaths)} deaths${r.accidents?`, ${fmt(r.accidents)} crashes`:""}${r.injuries?`, ${fmt(r.injuries)} injured`:""}</div>`:`<b>${mn} ${yy}</b><div>no monthly figure found</div>`,px,py); }).on("mouseleave",()=>T.hide());
        if(r && cell>=36) g.append("text").attr("x",40+j*cell+(cell-3)/2).attr("y",28+i*cell+(cell-3)/2).attr("dy","0.35em").attr("text-anchor","middle").attr("fill","#1F2327").attr("font-size",10.5).attr("font-weight",700).text(r.deaths); }); });
    MON.forEach((mn,j)=>svg.append("text").attr("x",40+j*cell+(cell-3)/2).attr("y",h-6).attr("text-anchor","middle").attr("fill",C.dust).attr("font-size",11).text(mn));
  }
  // Eid
  const eb=document.getElementById("whenEid"); const ev=Object.values(when.eid).sort((a,b)=>a.year-b.year||a.kind.localeCompare(b.kind));
  (function(){ const {w}=sizeOf(eb), h=290, m={t:26,r:16,b:72,l:48}; const svg=d3.select(eb).append("svg").attr("width",w).attr("height",h);
    const x=d3.scaleBand().domain(ev.map(e=>e.label)).range([m.l,w-m.r]).padding(.25);
    const y=d3.scaleLinear().domain([0,d3.max(ev,e=>e.deaths_per_day||e.deaths/(e.days||13))*1.2]).range([h-m.b,m.t]).nice();
    svg.append("g").attr("class","grid").selectAll("line").data(y.ticks(4)).join("line").attr("x1",m.l).attr("x2",w-m.r).attr("y1",d=>y(d)).attr("y2",d=>y(d));
    svg.append("g").attr("class","axis").attr("transform",`translate(0,${h-m.b})`).call(d3.axisBottom(x).tickFormat(s=>s.replace("Eid-ul-",""))).selectAll("text").attr("transform","rotate(-20)").attr("text-anchor","end");
    svg.append("g").attr("class","axis").attr("transform",`translate(${m.l},0)`).call(d3.axisLeft(y).ticks(4));
    const base=20; svg.append("line").attr("x1",m.l).attr("x2",w-m.r).attr("y1",y(base)).attr("y2",y(base)).attr("stroke",C.marigold).attr("stroke-dasharray","4 4"); svg.append("text").attr("x",m.l+4).attr("y",m.t-10).attr("fill",C.marigold).attr("font-size",11).text("dashed line: about 20 deaths a day in an ordinary year (7,294 ÷ 365, RSF 2024)");
    svg.selectAll("rect").data(ev).join("rect").attr("x",e=>x(e.label)).attr("width",x.bandwidth()).attr("y",e=>y(e.deaths_per_day||e.deaths/(e.days||13))).attr("height",e=>y(0)-y(e.deaths_per_day||e.deaths/(e.days||13))).attr("fill",e=>e.days?C.vermilion:C.ember).attr("opacity",e=>e.days?1:.6).attr("rx",2)
      .on("mousemove",(e2,e)=>{ const [px,py]=relPos(e2,eb); T.show(`<b>${e.label}</b><div>${fmt(e.deaths)} deaths${e.accidents?` in ${fmt(e.accidents)} crashes`:""}</div><div>${e.days?`${e.days}-day window, ${fmt1(e.deaths/e.days)} a day`:"window length not published; drawn as 13 days"}</div>`,px,py); }).on("mouseleave",()=>T.hide());
    svg.append("text").attr("x",m.l).attr("y",h-6).attr("fill",C.dust).attr("font-size",11).text("Bars: deaths per day of the Eid travel window. Lighter bars: window length not published, drawn as 13 days."); })();
  document.getElementById("whenNote").innerHTML=`Time-of-day bands follow the Road Safety Foundation's own categories (dawn, morning, noon, afternoon, evening, night) and are only published for a few months; the dial converts a selected hour window into a share by assuming crashes are spread evenly inside each band. Dhaka city cumulative deaths 2020–mid 2026 by band: ${ORDER.map(b=>`${b} ${fmt(when.cumulative_deaths_2020_2026[b]||0)}`).join(", ")}.`;
  document.getElementById("whenTakeaway").innerHTML=`<b>Mornings, not nights, are when most crashes are reported</b>: the 06–12 band alone holds about ${fmt1(when.tod_pooled.morning)}% of crashes in the months RSF has tabulated. Eid windows run at ${fmt1(d3.mean(ev.filter(e=>e.days),e=>e.deaths/e.days))} deaths a day, above the roughly 20 a day of an ordinary week.`;
  draw(); onResize(draw);
}
