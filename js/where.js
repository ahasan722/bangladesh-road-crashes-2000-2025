import { fmt, fmt1, seg, rampCss, ramp, C } from "./util.js";
import { makeMap } from "./basemap.js";

// Division names in the boundary file vs BBS names
const DIV_FIX = {"Chittagong":"Chattogram","Barisal":"Barishal","Rajshani":"Rajshahi"};

export function initWhere(where, popAdmin, spots, national){
  const map=makeMap("whereMap", {center:[90.3,23.75], zoom:6.15});
  const panel=document.getElementById("wherePanel"), stats=document.getElementById("whereStats"), legend=document.getElementById("whereLegend"), note=document.getElementById("whereNote"), yearEl=document.getElementById("whereYear");
  const pop=Object.fromEntries(popAdmin.filter(p=>p.level==="division").map(p=>[p.name,p]));
  const popD=Object.fromEntries(popAdmin.filter(p=>p.level==="district").map(p=>[p.name,p]));
  // periods: pooled first, then each published period
  const periods=[{period:"pooled", label:`All published periods pooled (${where.pooled_n})`, shares:where.pooled, basis:"accidents", totals:{}, sources:[]}, ...where.periods];
  let pi=0, measure="share", layer="division", playing=false, timer=null;
  const slider=document.getElementById("whereSlider"); slider.min=0; slider.max=periods.length-1; slider.value=0;
  const srcSel=document.getElementById("whereSource");
  srcSel.innerHTML=`<option value="division">Division share of crashes (RSF)</option><option value="district">Listed hazardous spots per district</option>`;
  srcSel.addEventListener("change", ()=>{ layer=srcSel.value; render(); });
  // measure segment: reuse buttons for share / per 100k / per period count
  const segEl=document.getElementById("whereMeasure"); segEl.innerHTML=`<button data-v="share" class="on">Share %</button><button data-v="rate">Per million people</button>`;
  seg(segEl, v=>{ measure=v; render(); });
  slider.addEventListener("input", ()=>{ pi=+slider.value; render(); });
  document.getElementById("wherePlay").addEventListener("click", ()=>{ playing=!playing; document.getElementById("wherePlay").textContent=playing?"Pause":"Play"; document.getElementById("wherePlay").classList.toggle("on",playing);
    if(playing){ timer=setInterval(()=>{ pi=(pi+1)%periods.length; slider.value=pi; render(); }, 1600); } else clearInterval(timer); });

  // district spot counts
  const spotByDistrict={}; spots.forEach(s=>{ if(s.district) spotByDistrict[s.district]=(spotByDistrict[s.district]||0)+1; });
  const DIST_FIX={"Chittagong":"Chattogram","Barisal":"Barishal","Comilla":"Cumilla","Jessore":"Jashore","Bogra":"Bogura","Nawabganj":"Chapainawabganj","Brahamanbaria":"Brahmanbaria","Maulvibazar":"Moulvibazar","Cox's Bazar":"Cox's Bazar"};

  map.on("load", ()=>{
    map.addLayer({id:"div-fill", type:"fill", source:"divisions", paint:{"fill-color":"#2C3238","fill-opacity":.9}}, "lakes");
    map.addLayer({id:"dist-fill2", type:"fill", source:"districts", paint:{"fill-color":"#2C3238","fill-opacity":0}}, "lakes");
    map.addLayer({id:"div-hover", type:"line", source:"divisions", paint:{"line-color":C.chalk,"line-width":2.2}, filter:["==",["get","division"],""]});
    map.addLayer({id:"dist-hover", type:"line", source:"districts", paint:{"line-color":C.chalk,"line-width":2}, filter:["==",["get","district"],""]});
    // division name markers
    const centers={Dhaka:[90.3,23.9],Chattogram:[91.6,22.6],Rajshahi:[88.9,24.4],Khulna:[89.3,22.7],Barishal:[90.35,22.5],Sylhet:[91.6,24.7],Rangpur:[89.2,25.7],Mymensingh:[90.5,24.9]};
    Object.entries(centers).forEach(([n,c])=>{ const el=document.createElement("div"); el.className="divlabel"; el.textContent=n; el.style.cssText="font:700 11px Open Sans;color:#ECE8DF;text-shadow:0 1px 2px #000;pointer-events:none;opacity:.85"; new maplibregl.Marker({element:el}).setLngLat(c).addTo(map); });
    map.on("mousemove","div-fill", e=>{ const d=DIV_FIX[e.features[0].properties.division]||e.features[0].properties.division; map.setFilter("div-hover",["==",["get","division"],e.features[0].properties.division]); showDiv(d); });
    map.on("mouseleave","div-fill", ()=>{ map.setFilter("div-hover",["==",["get","division"],""]); defaultPanel(); });
    map.on("mousemove","dist-fill2", e=>{ if(layer!=="district") return; const raw=e.features[0].properties.district, d=DIST_FIX[raw]||raw; map.setFilter("dist-hover",["==",["get","district"],raw]); showDist(d); });
    map.on("mouseleave","dist-fill2", ()=>{ map.setFilter("dist-hover",["==",["get","district"],""]); if(layer==="district") defaultPanel(); });
    render();
  });
  function valueFor(div){ const p=periods[pi]; const sh=p.shares[div]; if(sh==null) return null;
    if(measure==="share") return sh;
    // per million: share × period count ÷ population(2022) ... only when the period total is known; pooled uses RSF 2024 annual deaths as a scale
    const tot = p.period==="pooled" ? (national.find(r=>r.source==="RSF"&&r.year===2024)||{}).accidents : p.totals.accidents;
    if(!tot||!pop[div]) return null; return sh/100*tot/pop[div].pop_2022*1e6; }
  function render(){
    if(!map.getLayer("div-fill")) return;
    const p=periods[pi]; yearEl.textContent=p.period==="pooled"?"Pooled":p.label; slider.value=pi;
    if(layer==="division"){
      map.setLayoutProperty("div-fill","visibility","visible"); map.setPaintProperty("dist-fill2","fill-opacity",0);
      const vals=where.divisions.map(d=>valueFor(d)).filter(v=>v!=null); const max=d3.max(vals)||1, min=0;
      const expr=["match",["get","division"]]; where.divisions.forEach(d=>{ const key=Object.keys(DIV_FIX).find(k=>DIV_FIX[k]===d)||d; const v=valueFor(d); expr.push(key, v==null?"#3C434B":ramp((v-min)/(max-min))); }); expr.push("#3C434B");
      map.setPaintProperty("div-fill","fill-color",expr);
      legend.innerHTML=`${measure==="share"?"Share of reported crashes":"Crashes per million residents in the period"}<div class="bar" style="background:${rampCss}"></div><div class="ends"><span>0</span><span>${measure==="share"?fmt1(max)+"%":fmt1(max)}</span></div>`;
      const top=where.divisions.map(d=>({d,v:valueFor(d)})).filter(x=>x.v!=null).sort((a,b)=>b.v-a.v);
      stats.innerHTML=`<div class="stat red"><b class="num">${top[0]?top[0].d:"–"}</b><span>highest: ${top[0]?fmt1(top[0].v)+(measure==="share"?"%":""):""}</span></div><div class="stat"><b class="num">${top[top.length-1]?top[top.length-1].d:"–"}</b><span>lowest: ${top.length?fmt1(top[top.length-1].v)+(measure==="share"?"%":""):""}</span></div><div class="stat yel"><b class="num">${p.totals.accidents?fmt(p.totals.accidents):"–"}</b><span>crashes in period</span></div><div class="stat"><b class="num">${p.totals.deaths?fmt(p.totals.deaths):"–"}</b><span>deaths in period</span></div>`;
      note.innerHTML = p.period==="pooled" ? `Pooled from the ${where.pooled_n} periods for which the Road Safety Foundation published an 8-division table in the press (${where.periods.map(x=>x.label).join(", ")}), weighted by each period's crash count. RSF annual reports give only the highest and lowest division; no full division table for a calendar year was found online.` : `Division shares as published for ${p.label}${p.basis==="deaths"?" (share of deaths)":" (share of crashes)"}. ${p.sources.length?`<a href="${p.sources[0]}" target="_blank" rel="noopener">source</a>`:""}`;
    } else {
      map.setLayoutProperty("div-fill","visibility","none");
      const max=d3.max(Object.values(spotByDistrict))||1; const expr=["match",["get","district"]];
      Object.keys(DIST_FIX).concat(Object.keys(popD)).forEach(k=>{}); // no-op, names handled below
      const names=new Set(); map.getSource("districts"); // districts geojson names (BBS old spellings)
      const old=["Bagerhat","Bandarban","Barguna","Barisal","Bhola","Bogra","Brahamanbaria","Chandpur","Chittagong","Chuadanga","Comilla","Cox's Bazar","Dhaka","Dinajpur","Faridpur","Feni","Gaibandha","Gazipur","Gopalganj","Habiganj","Jamalpur","Jessore","Jhalokati","Jhenaidah","Joypurhat","Khagrachhari","Khulna","Kishoreganj","Kurigram","Kushtia","Lakshmipur","Lalmonirhat","Madaripur","Magura","Manikganj","Maulvibazar","Meherpur","Munshiganj","Mymensingh","Naogaon","Narail","Narayanganj","Narsingdi","Natore","Nawabganj","Netrakona","Nilphamari","Noakhali","Pabna","Panchagarh","Patuakhali","Pirojpur","Rajbari","Rajshahi","Rangamati","Rangpur","Satkhira","Shariatpur","Sherpur","Sirajganj","Sunamganj","Sylhet","Tangail","Thakurgaon"];
      old.forEach(o=>{ const n=DIST_FIX[o]||o; const v=spotByDistrict[n]||0; expr.push(o, v?ramp(v/max):"#2C3238"); }); expr.push("#2C3238");
      map.setPaintProperty("dist-fill2","fill-color",expr); map.setPaintProperty("dist-fill2","fill-opacity",.9);
      legend.innerHTML=`Listed hazardous locations per district (all lists, all years)<div class="bar" style="background:${rampCss}"></div><div class="ends"><span>0</span><span>${max}</span></div>`;
      const top=Object.entries(spotByDistrict).sort((a,b)=>b[1]-a[1]);
      stats.innerHTML=`<div class="stat red"><b class="num">${top[0][0]}</b><span>most listed spots: ${top[0][1]}</span></div><div class="stat"><b class="num">${Object.keys(spotByDistrict).length}</b><span>districts with a listed spot</span></div><div class="stat yel"><b class="num">${fmt(spots.length)}</b><span>spots on nine highways</span></div><div class="stat"><b class="num">${top[1][0]}</b><span>second: ${top[1][1]}</span></div>`;
      note.innerHTML=`Counts the blackspots and accident-prone locations compiled for the corridor chapter (press, RHD, ARI-BUET and RSF lists). It reflects which highways pass through a district and which lists were published, not a crash rate.`;
    }
    defaultPanel();
  }
  function defaultPanel(){ panel.innerHTML=`<b class="t">${layer==="division"?"Hover a division":"Hover a district"}</b><div class="muted">${layer==="division"?periods[pi].label:"Listed hazardous locations"}</div>`; }
  function showDiv(d){ const p=periods[pi]; const sh=p.shares[d]; const pp=pop[d];
    panel.innerHTML=`<b class="t">${d}</b><div class="muted">${p.label}</div><div class="row"><span>Share of ${p.basis}</span><b>${sh!=null?fmt1(sh)+"%":"n/a"}</b></div>${p.totals.accidents?`<div class="row"><span>Implied crashes</span><b>${fmt(Math.round(sh/100*p.totals.accidents))}</b></div>`:""}${pp?`<div class="row"><span>Population 2022</span><b>${fmt(pp.pop_2022)}</b></div><div class="row"><span>Share of population</span><b>${fmt1(pp.pop_2022/165158616*100)}%</b></div>`:""}${valueFor(d)!=null&&measure==="rate"?`<div class="row"><span>Per million</span><b>${fmt1(valueFor(d))}</b></div>`:""}`; }
  function showDist(d){ const n=spotByDistrict[d]||0; const pp=popD[d]; const sp=spots.filter(s=>s.district===d);
    panel.innerHTML=`<b class="t">${d}</b><div class="muted">${pp?pp.division+" division":""}</div><div class="row"><span>Listed hazardous spots</span><b>${n}</b></div>${pp?`<div class="row"><span>Population 2022</span><b>${fmt(pp.pop_2022)}</b></div>`:""}${sp.length?`<div class="muted" style="margin-top:6px">${[...new Set(sp.map(s=>s.highway))].join(", ")}: ${sp.slice(0,4).map(s=>s.place.split("(")[0].trim()).join("; ")}${sp.length>4?" and more":""}</div>`:""}`; }
  const dh=where.annual_extremes.filter(r=>r.measure==="deaths");
  document.getElementById("whereTakeaway").innerHTML=`<b>Dhaka division carries roughly a quarter of the country's reported crashes</b> in every period the Road Safety Foundation has tabulated, with Chattogram and Rajshahi next. Sylhet is consistently lowest. ${dh.length?`In the annual reports, ${dh.map(r=>`${r.division} ${r.year} (${fmt(r.value)} deaths)`).slice(0,3).join(", ")} mark the extremes.`:""}`;
}
