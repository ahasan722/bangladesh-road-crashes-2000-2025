import { fmt } from "./util.js";

export function initMethod(data){
  const nat=data.national; const bySrc={};
  nat.forEach(r=>{ const s=bySrc[r.source]||(bySrc[r.source]={years:[],n:0}); s.years.push(r.year); s.n++; });
  const ROWS=[
    ["Bangladesh Police / BRTA / ARI-BUET (MAAP)", "Police first-information reports compiled by BRTA and the Accident Research Institute, BUET", "Crashes, deaths, injuries by year, 1998–2025 (2017 missing; 2020 deaths only)", "Registered cases only; widely held to capture a fifth or less of deaths"],
    ["Bangladesh Jatri Kalyan Samity (BJKS)", "Passenger-welfare association's monitoring of national and regional newspapers and online media", "Annual 2014–2025, vehicle, road class, victim and collision breakdowns for some years, Eid windows", "Media-reported crashes only; definitions differ from police"],
    ["Road Safety Foundation (RSF)", "Monitoring of 9 national dailies, 7 online portals and 7 TV channels, with district correspondents", "Annual 2019–2025 and monthly 2020–2026, vehicle, victim, road class, time of day, division, Eid", "Media-reported; division and time-of-day tables only reproduced for some months"],
    ["Nirapad Sarak Chai (NISCHA), NCPSRR, SCRF", "Other NGO media-monitoring series", "Annual totals 2013–2022, 2015–2017, child deaths 2019", "Stopped publishing or only partial"],
    ["WHO Global Status Report on Road Safety", "Statistical model fitted on vital registration and survey data", "Estimated deaths and rate per 100,000 for 2007, 2010, 2013, 2016, 2021", "Modelled; government has disputed the figures"],
    ["Bangladesh Health and Injury Survey 2003, 2016; NHIS 2022–23", "National household surveys (ICMH, CIPRB, DGHS)", "Estimated annual road-injury deaths", "Survey estimate, not a count"],
    ["RHD, Highway Police, ARI-BUET and RSF hazardous-location lists", "Press reports, UNCRD slides, three academic papers, RSF upazila lists", "215 locations on nine national highways, located to a place or an upazila", "No official national blackspot list has been published"],
    ["OpenStreetMap, geoBoundaries, Natural Earth, BBS census, World Bank", "Geometry, boundaries, population", "Highway lines (ODbL), ADM1/ADM2 (CC BY), rivers, population 2011/2022 and annual", ""]
  ];
  document.getElementById("methodSources").innerHTML=`<div style="overflow-x:auto"><table class="src"><thead><tr><th>Source</th><th>What it is</th><th>Used here</th><th>Limit</th></tr></thead><tbody>${ROWS.map(r=>`<tr>${r.map(c=>`<td>${c}</td>`).join("")}</tr>`).join("")}</tbody></table></div>
  <p class="note" style="margin-top:14px">How the numbers were handled: every figure was transcribed into a long-format CSV with the URL it came from (${fmt(data.method?.n_citations||170)} distinct documents). Where two reports gave different values for the same cell both were kept and the chart uses the first; the CSV shows both. The Python pipeline (two scripts, in the repository) computes rates from World Bank population, snaps hazardous locations to the OSM highway line with a nearest-segment projection, and writes the JSON this page reads. Nothing is interpolated: a missing year is a gap in the line.</p>`;
  const files=[["data/raw/national_yearly.csv","National series"],["data/raw/breakdowns.csv","All breakdowns (long format)"],["data/raw/monthly.csv","Monthly series"],["data/raw/blackspots.csv","Hazardous locations"],["data/raw/corridors.csv","Corridor waypoints"],["data/raw/population_admin.csv","Population"],["data/raw/road_network.csv","Road network km"]];
  document.getElementById("downloads").innerHTML=files.map(([p,l])=>`<a class="btn" href="https://github.com/ahasan722/bangladesh-road-crashes-2000-2025/blob/main/${p}">${l}</a>`).join("")+`<a class="btn" href="https://github.com/ahasan722/bangladesh-road-crashes-2000-2025">Repository and notebook</a>`;
}
