// 24-hour dial with two draggable handles. Calls onChange(startHour, endHour) with ints 0..24.
export function initDial(svgEl, onChange, initial=[0,24]){
  const svg=d3.select(svgEl), cx=150, cy=150, r=104;
  let [s,e]=initial; let drag=null;
  const ang=h=>(h/24)*2*Math.PI-Math.PI/2; const pos=h=>[cx+r*Math.cos(ang(h)), cy+r*Math.sin(ang(h))];
  const defs=svg.append("defs"); const dg=defs.append("linearGradient").attr("id","daynight").attr("x1",0).attr("y1",0).attr("x2",0).attr("y2",1);
  dg.append("stop").attr("offset",0).attr("stop-color","#1E2A3A"); dg.append("stop").attr("offset",.45).attr("stop-color","#3B4652"); dg.append("stop").attr("offset",1).attr("stop-color","#5C5540");
  svg.append("circle").attr("class","face").attr("cx",cx).attr("cy",cy).attr("r",r+22);
  svg.append("circle").attr("cx",cx).attr("cy",cy).attr("r",r).attr("fill","none").attr("stroke","url(#daynight)").attr("stroke-width",14);
  // sun at noon, moon at midnight
  svg.append("circle").attr("cx",cx).attr("cy",cy+r-26).attr("r",5).attr("fill","#F5B335").attr("opacity",.9);
  svg.append("path").attr("d",`M${cx-3},${cy-r+20} a5,5 0 1,0 6,0 a4,4 0 1,1 -6,0`).attr("fill","#C9D3DD").attr("opacity",.9);
  const arc=svg.append("path").attr("class","arc");
  for(let h=0;h<24;h++){ const [x1,y1]=[cx+(r+12)*Math.cos(ang(h)), cy+(r+12)*Math.sin(ang(h))], [x2,y2]=[cx+(r+(h%6?15:19))*Math.cos(ang(h)), cy+(r+(h%6?15:19))*Math.sin(ang(h))];
    svg.append("line").attr("class","tick").attr("x1",x1).attr("y1",y1).attr("x2",x2).attr("y2",y2).attr("stroke-width",h%6?1:2);
    if(h%3===0){ const [tx,ty]=[cx+(r-24)*Math.cos(ang(h)), cy+(r-24)*Math.sin(ang(h))]; svg.append("text").attr("x",tx).attr("y",ty).attr("text-anchor","middle").attr("dy","0.35em").text(h===0?"24":h); } }
  // day/night glyphs
  svg.append("text").attr("x",cx).attr("y",cy-r-26).attr("text-anchor","middle").text("midnight");
  svg.append("text").attr("x",cx).attr("y",cy+r+34).attr("text-anchor","middle").text("noon");
  const label=svg.append("text").attr("class","hr").attr("x",cx).attr("y",cy).attr("text-anchor","middle").attr("dy","0.35em");
  const sub=svg.append("text").attr("x",cx).attr("y",cy+22).attr("text-anchor","middle").text("drag the handles");
  const hs=svg.append("circle").attr("class","handle").attr("r",10), he=svg.append("circle").attr("class","handle").attr("r",10);
  function render(){
    const a0=ang(s), a1=ang(e); const full=(s%24===e%24)||(e-s>=24);
    const d=d3.arc().innerRadius(r).outerRadius(r)({startAngle:a0+Math.PI/2, endAngle:(full?a0+2*Math.PI:(e>s?a1:a1+2*Math.PI))+Math.PI/2});
    arc.attr("d", d3.arc().innerRadius(r-7).outerRadius(r+7).startAngle(a0+Math.PI/2).endAngle((full?a0+2*Math.PI:(e>s?a1:a1+2*Math.PI))+Math.PI/2)());
    const p0=pos(s), p1=pos(e); hs.attr("cx",p0[0]).attr("cy",p0[1]); he.attr("cx",p1[0]).attr("cy",p1[1]);
    label.text(full?"All day":`${pad(s)}:00–${pad(e%24)}:00`);
  }
  const pad=n=>String(n).padStart(2,"0");
  function hourFromEvent(ev){ const pt=d3.pointer(ev, svgEl); const a=Math.atan2(pt[1]-cy, pt[0]-cx)+Math.PI/2; let h=Math.round(((a<0?a+2*Math.PI:a)/(2*Math.PI))*24)%24; return h; }
  svg.on("pointerdown", ev=>{ const pt=d3.pointer(ev,svgEl); const ds=Math.hypot(pt[0]-pos(s)[0],pt[1]-pos(s)[1]), de=Math.hypot(pt[0]-pos(e)[0],pt[1]-pos(e)[1]); drag= ds<de? "s":"e"; svgEl.setPointerCapture(ev.pointerId); move(ev); });
  svg.on("pointermove", move); svg.on("pointerup pointercancel", ()=>{ drag=null; });
  function move(ev){ if(!drag) return; const h=hourFromEvent(ev); if(drag==="s") s=h; else e=h===0?24:h; render(); onChange(s,e); }
  render(); onChange(s,e);
  return { set(ns,ne){ s=ns; e=ne; render(); }, get:()=>[s,e] };
}
