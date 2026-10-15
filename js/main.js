import { initHero } from "./hero.js";
import { initGap } from "./gap.js";
import { initCorridors } from "./corridors.js";
import { initWhere } from "./where.js";
import { initWho } from "./who.js";
import { initWhen } from "./when.js";
import { initRoads } from "./roads.js";
import { initMethod } from "./method.js";

const J = p => fetch(p).then(r => { if(!r.ok) throw new Error(p+" "+r.status); return r.json(); });

(async () => {
  const [national, corridors, spots, where, who, when, roads, popAdmin, popNat, method] = await Promise.all([
    J("data/national.json"), J("data/corridors.json"), J("data/blackspots.json"), J("data/where.json"), J("data/who.json"), J("data/when.json"), J("data/roads.json"),
    J("data/population_admin.json"), J("data/population_national.json"), J("data/method.json")
  ]);
  const data = { national, corridors, spots, where, who, when, roads, popAdmin, popNat, method };
  window.__data = data;
  initHero(national, spots);
  initGap(national, popNat);
  initWhere(where, popAdmin, spots, national);
  initCorridors(corridors, spots);
  initWho(who);
  initWhen(when);
  initRoads(roads);
  initMethod(data);
  // chapter nav highlight
  const links=[...document.querySelectorAll("nav.chapters a")];
  const obs=new IntersectionObserver(es=>{ es.forEach(e=>{ if(e.isIntersecting) links.forEach(l=>l.classList.toggle("on", l.getAttribute("href")==="#"+e.target.id)); }); }, {rootMargin:"-40% 0px -50% 0px"});
  document.querySelectorAll("section.chapter").forEach(s=>obs.observe(s));
  document.getElementById("buildStamp").textContent = "Data compiled October 2026. Figures update when the sources publish; check the GitHub repository for the latest build.";
})().catch(e => { console.error(e); document.body.insertAdjacentHTML("afterbegin", `<div style="background:#D9442F;color:#fff;padding:10px 20px">Could not load data: ${e.message}</div>`); });
