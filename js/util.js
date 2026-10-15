export const fmt = d3.format(",");
export const fmt1 = d3.format(",.1f");
export const pct = d3.format(".1%");

export const C = {
  asphalt:"#262B30", tarmac:"#30363D", gravel:"#3C434B", chalk:"#ECE8DF", dust:"#A9A496",
  marigold:"#F2B035", vermilion:"#D9442F", ember:"#F07A3C", steel:"#6F93AE", sky:"#A8C4D8", moss:"#7FA37A"
};
// severity ramp: steel -> marigold -> ember -> vermilion
export const ramp = d3.scaleLinear().domain([0,.35,.7,1]).range([C.steel,C.marigold,C.ember,C.vermilion]).interpolate(d3.interpolateLab);
export const rampCss = `linear-gradient(90deg, ${C.steel}, ${C.marigold}, ${C.ember}, ${C.vermilion})`;

export const SOURCE_COLORS = {
  "Police/BRTA": C.steel,
  "BJKS": C.marigold,
  "RSF": C.vermilion,
  "WHO estimate": C.sky,
  "WHO reported": "#8FA6B8",
  "BHIS": C.moss,
  "Nirapad Sarak Chai": "#C99BD6"
};
export function sourceColor(s){ return SOURCE_COLORS[s] || "#BBB"; }

export function seg(el, onChange, initial){
  const btns = [...el.querySelectorAll("button")];
  let v = initial ?? (btns.find(b=>b.classList.contains("on"))||btns[0]).dataset.v;
  const set = (nv, fire=true)=>{ v=nv; btns.forEach(b=>b.classList.toggle("on", b.dataset.v===v)); if(fire) onChange(v); };
  btns.forEach(b=>b.addEventListener("click", ()=>set(b.dataset.v)));
  set(v,false);
  return { get:()=>v, set };
}

export function chips(el, items, {multi=true, initial, onChange, colors}={}){
  el.innerHTML="";
  const sel = new Set(initial ?? (multi? items : [items[0]]));
  const btns = items.map(it=>{
    const b=document.createElement("button"); b.className="chip"+(colors?" sw":""); b.type="button";
    b.innerHTML = (colors? `<span class="dot" style="background:${colors(it)}"></span>`:"") + it;
    b.classList.toggle("on", sel.has(it));
    b.addEventListener("click", ()=>{
      if(multi){ if(sel.has(it) && sel.size>1) sel.delete(it); else sel.add(it); }
      else { sel.clear(); sel.add(it); }
      btns.forEach((bb,i)=>bb.classList.toggle("on", sel.has(items[i])));
      onChange([...sel]);
    });
    el.appendChild(b); return b;
  });
  return { get:()=>[...sel], set:(arr)=>{ sel.clear(); arr.forEach(a=>sel.add(a)); btns.forEach((bb,i)=>bb.classList.toggle("on", sel.has(items[i]))); } };
}

export function tip(el){
  return {
    show(html, x, y){ el.innerHTML=html; el.classList.add("show");
      const p=el.parentElement.getBoundingClientRect(); const w=el.offsetWidth, h=el.offsetHeight;
      let lx=x+14, ly=y-10; if(lx+w>p.width-8) lx=x-w-14; if(ly+h>p.height-8) ly=p.height-h-8; if(ly<4) ly=4;
      el.style.left=lx+"px"; el.style.top=ly+"px"; },
    hide(){ el.classList.remove("show"); }
  };
}

export function relPos(ev, container){ const r=container.getBoundingClientRect(); return [ev.clientX-r.left, ev.clientY-r.top]; }

export function sizeOf(el, h){ let w=el.clientWidth, p=el; while((!w||w<40) && p.parentElement){ p=p.parentElement; w=p.clientWidth; } w=Math.max(280, w||Math.min(900, window.innerWidth-48)); return {w, h: h ?? Math.max(300, Math.round(w*0.46))}; }

export function onResize(fn){ let t; window.addEventListener("resize", ()=>{ clearTimeout(t); t=setTimeout(fn,120); }); }

export function sourceList(rows, key="source"){ return [...new Set(rows.map(r=>r[key]))]; }

export function haversine(a,b){ const R=6371000, toR=Math.PI/180; const dLat=(b[1]-a[1])*toR, dLng=(b[0]-a[0])*toR; const s=Math.sin(dLat/2)**2+Math.cos(a[1]*toR)*Math.cos(b[1]*toR)*Math.sin(dLng/2)**2; return 2*R*Math.asin(Math.sqrt(s)); }

export function niceStep(v){ const p=Math.pow(10,Math.floor(Math.log10(v))); const r=v/p; return (r<1.5?1:r<3?2:r<7?5:10)*p; }
