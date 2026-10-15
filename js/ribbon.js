// Hazard ribbon: bars drawn on a canvas beside a MapLibre polyline, one bar per distance bin.
// Own implementation. Geometry in lng/lat; distances in metres along the route.
import { haversine, ramp, C } from "./util.js";

export function buildRoute(coords){ // coords: [[lng,lat],...]
  const seg=[]; let m=0;
  for(let i=1;i<coords.length;i++){ const d=haversine(coords[i-1],coords[i]); if(d<=0) continue; seg.push({a:coords[i-1], b:coords[i], start:m, end:m+d}); m+=d; }
  return { coords, segments:seg, total:m };
}
export function pointAt(route, m){
  const s=route.segments; let lo=0, hi=s.length-1;
  while(lo<hi){ const mid=(lo+hi)>>1; if(s[mid].end<m) lo=mid+1; else hi=mid; }
  const g=s[lo]; const t=Math.max(0,Math.min(1,(m-g.start)/(g.end-g.start)));
  return [g.a[0]+(g.b[0]-g.a[0])*t, g.a[1]+(g.b[1]-g.a[1])*t];
}
export function projectToRoute(route, p){ // nearest point on polyline, returns {m, dist}
  let best={m:0,dist:Infinity};
  const toR=Math.PI/180, kx=111320*Math.cos(p[1]*toR), ky=111320;
  for(const g of route.segments){
    const ax=(g.a[0]-p[0])*kx, ay=(g.a[1]-p[1])*ky, bx=(g.b[0]-p[0])*kx, by=(g.b[1]-p[1])*ky;
    const dx=bx-ax, dy=by-ay, L=dx*dx+dy*dy; let t=L>0? -(ax*dx+ay*dy)/L : 0; t=Math.max(0,Math.min(1,t));
    const px=ax+dx*t, py=ay+dy*t, d=Math.hypot(px,py);
    if(d<best.dist) best={m:g.start+(g.end-g.start)*t, dist:d};
  }
  return best;
}
export function sliceRoute(route, from, to){ // coords between two metre marks
  const out=[pointAt(route,from)];
  for(const g of route.segments){ if(g.end>from && g.start<to && g.start>from) out.push(g.a); }
  out.push(pointAt(route,to)); return out;
}

export class Ribbon {
  constructor(map, canvas, opts={}){
    this.map=map; this.canvas=canvas; this.ctx=canvas.getContext("2d");
    this.route=null; this.bins=[]; this.binMeters=10000; this.hover=null; this.is3d=false;
    this.onHover=opts.onHover||(()=>{}); this.maxBarPx=opts.maxBarPx||150; this.side=1;
    this.bars=[];
    const redraw=()=>this.draw();
    map.on("render", redraw); map.on("resize", ()=>{ this.resize(); redraw(); });
    this.resize();
    const cont=map.getContainer();
    cont.addEventListener("mousemove", e=>{ const r=canvas.getBoundingClientRect(); this.hit(e.clientX-r.left, e.clientY-r.top); });
    cont.addEventListener("mouseleave", ()=>this.setHover(null));
  }
  resize(){ const r=this.map.getContainer().getBoundingClientRect(); const dpr=window.devicePixelRatio||1; this.canvas.width=r.width*dpr; this.canvas.height=r.height*dpr; this.canvas.style.width=r.width+"px"; this.canvas.style.height=r.height+"px"; this.dpr=dpr; this.w=r.width; this.h=r.height; }
  setRoute(route){ this.route=route; this.side=this.curveSide(route); this.draw(); }
  setBins(bins, binMeters){ this.bins=bins; this.binMeters=binMeters; this.peak=d3.max(bins,b=>b.count)||1; this.draw(); }
  set3d(v){ this.is3d=v; this.draw(); }
  curveSide(route){ // which side of the overall curve to put bars: outside of the dominant bend
    const pts=[]; const n=24; for(let i=0;i<=n;i++) pts.push(pointAt(route, route.total*i/n));
    let s=0; for(let i=1;i<pts.length-1;i++){ const a=pts[i-1],b=pts[i],c=pts[i+1]; s+=(b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]); }
    return s>0? -1 : 1;
  }
  setHover(bin){ if((this.hover&&this.hover.index)===(bin&&bin.index)) return; this.hover=bin; this.onHover(bin); this.draw(); }
  hit(x,y){ for(const b of this.bars){ if(pip(b.poly,[x,y])){ this.setHover(b.bin); return; } } this.setHover(null); }
  draw(){
    const ctx=this.ctx, map=this.map; ctx.setTransform(this.dpr,0,0,this.dpr,0,0); ctx.clearRect(0,0,this.w,this.h); this.bars=[];
    if(!this.route||!this.bins.length) return;
    const bm=this.binMeters, route=this.route;
    const pr=ll=>{ const p=map.project(ll); return [p.x,p.y]; };
    const maxBar=Math.min(this.maxBarPx, this.h*0.3);
    const hPx=c=>Math.sqrt(c/this.peak)*maxBar*(this.is3d?1.6:1);
    // smoothed spine in screen space: sample the route every `step` metres, project, box-smooth over ~30 km
    const step=Math.max(1000, Math.min(4000, route.total/300)); const n=Math.floor(route.total/step);
    const raw=[]; for(let i=0;i<=n;i++) raw.push(pr(pointAt(route, Math.min(route.total, i*step))));
    const win=Math.max(2, Math.round(30000/step)); const sp=raw.map((p,i)=>{ const a=Math.max(0,i-win), b=Math.min(raw.length-1,i+win); let x=0,y=0,c=0; for(let j=a;j<=b;j++){ x+=raw[j][0]; y+=raw[j][1]; c++; } return [x/c,y/c]; });
    sp[0]=raw[0]; sp[sp.length-1]=raw[raw.length-1];
    const spineAt=m=>{ const t=Math.min(sp.length-1, m/step); const i=Math.floor(t), f=t-i; const a=sp[i], b=sp[Math.min(sp.length-1,i+1)]; return [a[0]+(b[0]-a[0])*f, a[1]+(b[1]-a[1])*f]; };
    const normalAt=m=>{ const a=spineAt(Math.max(0,m-step*2)), b=spineAt(Math.min(route.total,m+step*2)); let tx=b[0]-a[0], ty=b[1]-a[1]; const l=Math.hypot(tx,ty)||1; tx/=l; ty/=l; return {tx,ty,nx:-ty*this.side, ny:tx*this.side}; };
    // clearance: how far the real road wanders from the smoothed spine on the bar side, so bars start clear of the road
    const items=[];
    for(const bin of this.bins){
      const from=bin.index*bm+bm*0.08, to=Math.min(route.total,(bin.index+1)*bm-bm*0.08); if(to<=from) continue;
      const mid=(from+to)/2; const nm=normalAt(mid);
      let nx, ny; if(this.is3d){ nx=0; ny=-1; } else { nx=nm.nx; ny=nm.ny; }
      let clear=0; for(let m=from;m<=to;m+=Math.max(500,bm/6)){ const r=pr(pointAt(route,m)), s=spineAt(m); clear=Math.max(clear,(r[0]-s[0])*nx+(r[1]-s[1])*ny); }
      const gap=this.is3d?6:Math.max(14, clear+12); const h=hPx(bin.count);
      const A=spineAt(from), B=spineAt(to);
      const a=[A[0]+nx*gap, A[1]+ny*gap], b=[B[0]+nx*gap, B[1]+ny*gap];
      const wpx=Math.hypot(b[0]-a[0],b[1]-a[1]); if(wpx<1.2||wpx>this.w) continue;
      items.push({bin, a, b, nx, ny, h, depth:(A[1]+B[1])/2, tx:nm.tx, ty:nm.ty});
    }
    if(this.is3d) items.sort((p,q)=>p.depth-q.depth);
    const hov=this.hover;
    for(const it of items){
      const v=Math.sqrt(it.bin.count/this.peak); const col=d3.color(ramp(v));
      const isH=hov&&hov.index===it.bin.index;
      const poly=[it.a,it.b,[it.b[0]+it.nx*it.h,it.b[1]+it.ny*it.h],[it.a[0]+it.nx*it.h,it.a[1]+it.ny*it.h]];
      if(this.is3d && it.h>0){
        const dx=it.tx*0.5, dy=it.ty*0.5-0.5, dl=Math.hypot(dx,dy)||1, dep=Math.max(3,Math.min(9,Math.hypot(it.b[0]-it.a[0],it.b[1]-it.a[1])*0.35));
        const ox=dx/dl*dep, oy=dy/dl*dep;
        const side=[poly[1],[poly[1][0]+ox,poly[1][1]+oy],[poly[2][0]+ox,poly[2][1]+oy],poly[2]];
        const top=[poly[3],poly[2],[poly[2][0]+ox,poly[2][1]+oy],[poly[3][0]+ox,poly[3][1]+oy]];
        fill(ctx, side, col.darker(1.1).formatRgb(), .95); fill(ctx, top, col.brighter(.7).formatRgb(), .95);
      }
      ctx.shadowColor=isH?"rgba(245,179,53,.9)":col.copy({opacity:.55}).formatRgb(); ctx.shadowBlur=isH?22:10; fill(ctx, poly, col.formatRgb(), isH?1:.9); ctx.shadowBlur=0;
      ctx.strokeStyle=isH?C.chalk:"rgba(31,35,39,.8)"; ctx.lineWidth=isH?1.8:.7; path(ctx,poly); ctx.stroke();
      if(isH){ ctx.font="800 12px Open Sans"; ctx.fillStyle=C.chalk; ctx.strokeStyle="rgba(31,35,39,.9)"; ctx.lineWidth=3;
        const lx=(poly[2][0]+poly[3][0])/2+it.nx*10, ly=(poly[2][1]+poly[3][1])/2+it.ny*10; ctx.textAlign="center"; ctx.textBaseline="middle";
        const label=String(it.bin.count); ctx.strokeText(label,lx,ly); ctx.fillText(label,lx,ly); }
      this.bars.push({poly, bin:it.bin});
    }
    // baseline along the road for readability
    if(items.length){ ctx.beginPath(); items.forEach((it,i)=>{ if(i===0) ctx.moveTo(it.a[0],it.a[1]); ctx.lineTo(it.a[0],it.a[1]); ctx.lineTo(it.b[0],it.b[1]); });
      ctx.strokeStyle="rgba(236,232,223,.45)"; ctx.lineWidth=1; ctx.stroke(); }
  }
}
function path(ctx,p){ ctx.beginPath(); ctx.moveTo(p[0][0],p[0][1]); for(let i=1;i<p.length;i++) ctx.lineTo(p[i][0],p[i][1]); ctx.closePath(); }
function fill(ctx,p,color,alpha){ ctx.globalAlpha=alpha; ctx.fillStyle=color; path(ctx,p); ctx.fill(); ctx.globalAlpha=1; }
function pip(poly,[x,y]){ let inside=false; for(let i=0,j=poly.length-1;i<poly.length;j=i++){ const [xi,yi]=poly[i],[xj,yj]=poly[j]; if(((yi>y)!==(yj>y)) && (x<(xj-xi)*(y-yi)/(yj-yi)+xi)) inside=!inside; } return inside; }
