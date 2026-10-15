import { fmt, seg, chips, rampCss, C } from "./util.js";
import { makeMap } from "./basemap.js";
import { buildRoute, pointAt, sliceRoute, Ribbon } from "./ribbon.js";

export function initCorridors(corridors, spots){
  const refs=["N1","N2","N3","N4","N5","N6","N7","N8","N805"];
  const map=makeMap("corrMap", {center:[90.4,23.8], zoom:6.3, mapOpts:{dragRotate:true, pitchWithRotate:true, maxPitch:65}});
  const ribbon=new Ribbon(map, document.getElementById("corrCanvas"), {onHover:showHover, maxBarPx:170}); window.__ribbon=ribbon;
  const panel=document.getElementById("corrPanel"), badge=document.getElementById("corrBadge"), stats=document.getElementById("corrStats"), note=document.getElementById("corrNote");
  let ref="N1", binKm=10, layers=["point","upazila"], years=null, is3d=false, route=null;
  const yearsAll=[...new Set(spots.map(s=>s.year).filter(Boolean))].sort();
  const yearChips=chips(document.getElementById("corrYears"), yearsAll.map(String), {onChange:v=>{years=new Set(v.map(Number)); update();}});
  years=new Set(yearsAll);
  // relabel layer chips to what the data actually is
  const layerEl=document.getElementById("corrLayers");
  layerEl.innerHTML=`<button class="chip on" data-v="point">Point-located spots</button><button class="chip on" data-v="upazila">Upazila-level listings</button>`;
  layerEl.querySelectorAll(".chip").forEach(b=>b.addEventListener("click",()=>{ b.classList.toggle("on"); layers=[...layerEl.querySelectorAll(".chip.on")].map(x=>x.dataset.v); update(); }));
  const cl=document.getElementById("corrList");
  chips(cl, refs, {multi:false, initial:[ref], onChange:v=>{ ref=v[0]; load(); }});
  seg(document.getElementById("corrBin"), v=>{ binKm=+v; update(); });
  document.getElementById("corr3d").addEventListener("click", ()=>{ is3d=!is3d; document.getElementById("corr3d").classList.toggle("on",is3d); ribbon.set3d(is3d);
    if(is3d){ const b=screenBearing(); map.easeTo({pitch:58, bearing:b, duration:900}); } else map.easeTo({pitch:0, bearing:0, duration:900}); });
  document.getElementById("corrLegend").innerHTML=`Listed spots per bin, low to high<div class="bar" style="background:${rampCss}"></div><div class="ends"><span>fewer</span><span>more</span></div>`;

  map.on("load", ()=>{
    map.addSource("hw", {type:"geojson", data:"data/highways.geojson"});
    map.addLayer({id:"hw-r", type:"line", source:"hw", filter:["==",["get","cls"],"regional"], paint:{"line-color":"#444C55","line-width":["interpolate",["linear"],["zoom"],5,.4,9,1.4]}});
    map.addLayer({id:"hw-n-glow", type:"line", source:"hw", filter:["==",["get","cls"],"national"], paint:{"line-color":"#9FB0C0","line-width":["interpolate",["linear"],["zoom"],5,3,9,7],"line-opacity":.12,"line-blur":3}});
    map.addLayer({id:"hw-n", type:"line", source:"hw", filter:["==",["get","cls"],"national"], paint:{"line-color":"#7E8A97","line-width":["interpolate",["linear"],["zoom"],5,.9,9,2.2]}});
    map.addSource("route", {type:"geojson", data:empty()});
    map.addLayer({id:"route-glow", type:"line", source:"route", paint:{"line-color":C.marigold,"line-width":["interpolate",["linear"],["zoom"],5,14,10,26],"line-opacity":.22,"line-blur":8}});
    map.addLayer({id:"route-casing", type:"line", source:"route", paint:{"line-color":"#15171A","line-width":["interpolate",["linear"],["zoom"],5,5.5,10,11],"line-opacity":.95}});
    map.addLayer({id:"route", type:"line", source:"route", paint:{"line-color":C.marigold,"line-width":["interpolate",["linear"],["zoom"],5,2.6,10,5.5]}});
    map.addLayer({id:"route-dash", type:"line", source:"route", paint:{"line-color":"#15171A","line-width":["interpolate",["linear"],["zoom"],5,.8,10,1.6],"line-dasharray":[3,3],"line-opacity":.7}});
    map.addSource("hl", {type:"geojson", data:empty()});
    map.addLayer({id:"hl-glow", type:"line", source:"hl", paint:{"line-color":C.chalk,"line-width":["interpolate",["linear"],["zoom"],5,18,10,30],"line-opacity":.25,"line-blur":10}});
    map.addLayer({id:"hl", type:"line", source:"hl", paint:{"line-color":C.chalk,"line-width":["interpolate",["linear"],["zoom"],5,5,10,10],"line-opacity":.95}});
    map.addSource("spots", {type:"geojson", data:empty()});
    map.addLayer({id:"spots-u", type:"circle", source:"spots", filter:["==",["get","precision"],"upazila"], paint:{"circle-radius":["interpolate",["linear"],["zoom"],6,8,10,18],"circle-color":C.vermilion,"circle-opacity":.14,"circle-stroke-color":C.vermilion,"circle-stroke-width":1,"circle-stroke-opacity":.5,"circle-blur":.4}});
    map.addLayer({id:"spots-pulse", type:"circle", source:"spots", filter:["==",["get","precision"],"point"], paint:{"circle-radius":6,"circle-color":C.vermilion,"circle-opacity":.35,"circle-blur":.8}});
    map.addLayer({id:"spots-p", type:"circle", source:"spots", filter:["==",["get","precision"],"point"], paint:{"circle-radius":["interpolate",["linear"],["zoom"],6,2.8,10,5.5],"circle-color":"#FF6B55","circle-stroke-color":"#15171A","circle-stroke-width":1}});
    if(!matchMedia("(prefers-reduced-motion: reduce)").matches){ const t0=performance.now(); (function pulse(now){ const k=(Math.sin((now-t0)/600)+1)/2; try{ map.setPaintProperty("spots-pulse","circle-radius",6+k*10); map.setPaintProperty("spots-pulse","circle-opacity",.4-k*.35); }catch(e){} requestAnimationFrame(pulse); })(t0); }
    map.addSource("wp", {type:"geojson", data:empty()});
    map.addLayer({id:"wp", type:"circle", source:"wp", paint:{"circle-radius":3,"circle-color":C.chalk,"circle-stroke-color":"#1F2327","circle-stroke-width":1}});
    map.on("mousemove","spots-p", e=>{ map.getCanvas().style.cursor="pointer"; const p=e.features[0].properties; showSpot(p); });
    map.on("mouseleave","spots-p", ()=>{ map.getCanvas().style.cursor=""; showHover(ribbon.hover); });
    map.on("mousemove","spots-u", e=>{ const p=e.features[0].properties; showSpot(p); });
    load();
  });
  function empty(){ return {type:"FeatureCollection",features:[]}; }
  function screenBearing(){ const c=route.coords; const a=map.project(c[0]), b=map.project(c[c.length-1]); let deg=Math.atan2(b.x-a.x, -(b.y-a.y))*180/Math.PI; deg=((deg+360)%360); if(deg>90&&deg<270) deg-=180; return deg; }
  function load(){
    const cdat=corridors[ref]; route=buildRoute(cdat.coords); ribbon.setRoute(route);
    map.getSource("route").setData({type:"Feature",geometry:{type:"LineString",coordinates:cdat.coords}});
    map.getSource("wp").setData({type:"FeatureCollection",features:cdat.waypoints.map(w=>({type:"Feature",properties:{place:w.place,km:w.km},geometry:{type:"Point",coordinates:[w.lng,w.lat]}}))});
    badge.textContent=`${ref}  ${cdat.name}`;
    const b=new maplibregl.LngLatBounds(); cdat.coords.forEach(c=>b.extend(c));
    if(is3d){ is3d=false; document.getElementById("corr3d").classList.remove("on"); ribbon.set3d(false); }
    map.fitBounds(b, {padding:{top:60,bottom:40,left:60,right:60}, duration:1100, pitch:0, bearing:0});
    update();
  }
  function current(){ return spots.filter(s=>s.highway===ref && layers.includes(s.precision) && (!s.year || years.has(s.year))); }
  function update(){
    if(!route) return;
    const cur=current(); const bm=binKm*1000; const counts=new Map();
    cur.forEach(s=>{ const i=Math.min(Math.floor(s.route_m/bm), Math.floor((route.total-1)/bm)); const e=counts.get(i)||{index:i,count:0,spots:[]}; e.count++; e.spots.push(s); counts.set(i,e); });
    const bins=[...counts.values()];
    ribbon.setBins(bins, bm);
    map.getSource("spots").setData({type:"FeatureCollection",features:cur.map(s=>({type:"Feature",properties:s,geometry:{type:"Point",coordinates:[s.lng,s.lat]}}))});
    const peak=bins.length? d3.max(bins,b=>b.count):0, peakBin=bins.find(b=>b.count===peak);
    const c=corridors[ref];
    stats.innerHTML=`<div class="stat"><b class="num">${fmt(cur.length)}</b><span>listed spots on ${ref}</span></div><div class="stat"><b class="num">${Math.round(route.total/1000)} km</b><span>route length (OSM)</span></div><div class="stat red"><b class="num">${peak}</b><span>spots in the worst ${binKm} km</span></div><div class="stat yel"><b class="num">${peakBin? Math.round(peakBin.index*binKm)+"–"+Math.round((peakBin.index+1)*binKm):"–"}</b><span>km of that bin</span></div>`;
    const nPoint=cur.filter(s=>s.precision==="point").length, nUp=cur.length-nPoint;
    note.innerHTML=`Showing ${nPoint} point-located spots and ${nUp} upazila-level listings on ${ref} from ${[...new Set(cur.map(s=>s.year).filter(Boolean))].sort().join(", ")||"undated"} lists. Bars count how many listed hazardous locations fall in each ${binKm} km of road, not crashes. Geometry: OpenStreetMap trunk and primary roads (ODbL). Translucent circles are upazila-level listings drawn at a representative point, so their bin is approximate.`;
    showHover(null);
  }
  function showHover(bin){
    map.getSource("hl")?.setData(bin? {type:"Feature",geometry:{type:"LineString",coordinates:sliceRoute(route, bin.index*binKm*1000, Math.min(route.total,(bin.index+1)*binKm*1000))}} : empty());
    if(!bin){ panel.innerHTML=`<b class="t">${ref}: hover a bar</b><div class="muted">Each bar is a ${binKm} km stretch. Hover to list what was reported there.</div>`; return; }
    const names=bin.spots.slice(0,6).map(s=>`<div class="row"><span>${s.place}</span><b>${s.year||""}</b></div>`).join("");
    panel.innerHTML=`<b class="t">km ${Math.round(bin.index*binKm)}–${Math.round((bin.index+1)*binKm)} of ${ref}</b><div class="muted">${bin.count} listed hazardous location${bin.count>1?"s":""}</div>${names}${bin.spots.length>6?`<div class="muted">and ${bin.spots.length-6} more</div>`:""}`;
  }
  function showSpot(p){
    panel.innerHTML=`<b class="t">${p.place}</b><div class="muted">${p.upazila||""}${p.district?", "+p.district:""}</div><div class="row"><span>Listed</span><b>${p.year||"n/a"}</b></div><div class="row"><span>Km on ${p.highway}</span><b>${Math.round(p.route_m/1000)}</b></div><div style="margin-top:6px;font-size:12px">${p.rank||""}</div><div class="muted" style="margin-top:4px;font-size:11.5px">${p.precision==="upazila"?"Located to upazila only. ":""}${p.note?String(p.note).slice(0,220):""}</div>${p.source_url?`<div style="margin-top:6px"><a href="${p.source_url}" target="_blank" rel="noopener">source</a></div>`:""}`;
  }
  document.getElementById("corrTakeaway").innerHTML=`Every corridor has the same anatomy: the bars pile up where a highway passes through a bazar, a bus stand, a sharp bend or a bridge approach. <b>The N1 between Sitakunda and Mirsharai, the N2 through Sarail and Ashuganj, and the N5 around Gobindaganj and Palashbari</b> are listed year after year by police, RHD, researchers and the Road Safety Foundation alike.`;
}
