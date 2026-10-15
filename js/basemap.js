// Self-hosted vector basemap: no tile server, works offline, loads in under a second.
export function baseStyle(){
  return {
    version: 8,
    sources: {
      countries: { type:"geojson", data:"assets/basemap/countries.geojson" },
      rivers:    { type:"geojson", data:"assets/basemap/rivers.geojson" },
      lakes:     { type:"geojson", data:"assets/basemap/lakes.geojson" },
      districts: { type:"geojson", data:"assets/basemap/districts.geojson", promoteId:"district" },
      divisions: { type:"geojson", data:"assets/basemap/divisions.geojson", promoteId:"division" }
    },
    layers: [
      { id:"bg", type:"background", paint:{ "background-color":"#1D2125" } },
      { id:"neighbours", type:"fill", source:"countries", filter:["!=",["get","iso"],"BGD"], paint:{ "fill-color":"#24292E" } },
      { id:"bd", type:"fill", source:"countries", filter:["==",["get","iso"],"BGD"], paint:{ "fill-color":"#2C3238" } },
      { id:"district-fill", type:"fill", source:"districts", paint:{ "fill-color":"#2C3238", "fill-opacity":0 } },
      { id:"lakes", type:"fill", source:"lakes", paint:{ "fill-color":"#1A2A36" } },
      { id:"rivers", type:"line", source:"rivers", paint:{ "line-color":"#3C5A6E", "line-width":["interpolate",["linear"],["zoom"],5,1,8,3,11,6], "line-opacity":.9 } },
      { id:"district-line", type:"line", source:"districts", paint:{ "line-color":"#3E454D", "line-width":.6 } },
      { id:"division-line", type:"line", source:"divisions", paint:{ "line-color":"#5A6370", "line-width":1.2 } },
      { id:"border", type:"line", source:"countries", filter:["==",["get","iso"],"BGD"], paint:{ "line-color":"#7E8893", "line-width":1.4 } }
    ]
  };
}

export function makeMap(container, opts={}){
  const map = new maplibregl.Map({
    container, style: baseStyle(), center: opts.center||[90.3,23.7], zoom: opts.zoom||6.1,
    minZoom:5, maxZoom:12, attributionControl:false, dragRotate:false, pitchWithRotate:false, ...opts.mapOpts
  });
  map.addControl(new maplibregl.NavigationControl({showCompass:false}), "bottom-right");
  map.addControl(new maplibregl.AttributionControl({compact:true, customAttribution:"Boundaries: geoBoundaries (CC BY 4.0). Rivers: Natural Earth."}), "bottom-left");
  // the section may be laid out after the map is created; resize when it scrolls into view and after fonts settle
  const el=document.getElementById(container);
  new IntersectionObserver(es=>{ if(es.some(e=>e.isIntersecting)) map.resize(); }, {threshold:0.05}).observe(el);
  if(window.ResizeObserver) new ResizeObserver(()=>map.resize()).observe(el);
  setTimeout(()=>map.resize(), 600); setTimeout(()=>map.resize(), 2500);
  return map;
}
