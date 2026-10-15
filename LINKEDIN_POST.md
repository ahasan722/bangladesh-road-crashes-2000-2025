**Deadly Roads: Bangladesh 2000–2025. An interactive explorer I built in my own time.**

🔗 https://ahasan722.github.io/bangladesh-road-crashes-2000-2025/

**Data source**
Bangladesh Police / BRTA / ARI-BUET police-reported series 1998–2025; Bangladesh Jatri Kalyan Samity annual reports 2014–2025; Road Safety Foundation annual, monthly and Eid reports 2019–2026; WHO Global Status Reports on Road Safety 2009–2023; BHIS 2003/2016 and NHIS 2022–23; 215 listed hazardous highway locations from RHD, Highway Police, ARI-BUET papers and RSF; OpenStreetMap highway geometry, geoBoundaries, BBS census 2022, World Bank population. 170 cited documents, every figure traceable to its URL.

**About the project**
Every day roughly twenty people in Bangladesh leave home and die on the road. But which twenty? The police say about 5,500 a year. Media monitors say 7,000 to 9,000. The WHO estimates 31,000. I wanted one page where those numbers sit on the same axis and where you can then go deeper: which division, which highway, which kilometre, which vehicle, which hour, which class of road.

The page has seven chapters. The one I am proudest of is the corridor view: pick N1, N2 or N5 and a hazard ribbon rises beside the real road alignment wherever police, RHD, researchers and the Road Safety Foundation have listed an accident-prone spot. Hover a bar and the stretch lights up with what was listed there. The idea came from a Norwegian NVDB accident-density map; the data, geometry and implementation are my own.

A few things the data says:
• Motorcycle deaths nearly doubled between 2020 and 2022 and now make up about 36% of all road deaths.
• Dhaka division carries about a quarter of reported crashes in every period tabulated; Sylhet is consistently lowest.
• National and regional highways are under 3% of the road network and carry roughly two thirds of reported crashes.
• Mornings (06–12), not nights, hold the largest share of reported crashes.
• Eid travel windows run at 16 to 27 deaths a day, against about 20 on an ordinary day.

And a few things it does not say, which matter just as much: there is no public geocoded crash dataset for Bangladesh, no official national blackspot list has ever been published, and police and media counts measure different things. The page says so wherever it applies.

**Technology**
1️⃣ Python (pandas, shapely): transcribed 2,500 rows from reports and press tables into tidy CSVs with a citation per row, snapped 215 hazardous locations to the OSM highway line with a nearest-segment projection, and built the JSON the page reads. One Jupyter notebook rebuilds everything and runs the checks.
2️⃣ MapLibre GL: a self-hosted vector basemap (no tile server), division choropleth, highway network layer and a 3D-capable corridor map.
3️⃣ HTML Canvas: the hazard ribbon, drawn on a canvas over the map with a smoothed spine so bars stay perpendicular to the road and clear of it.
4️⃣ D3.js: the reporting-gap chart with source toggles and log scale, victim lines, a draggable 24-hour dial, month heat strip, Eid bars and road-class shares.
5️⃣ OpenStreetMap, geoBoundaries and Natural Earth for geometry; BBS and World Bank for population.
6️⃣ GitHub Pages for hosting: static files only, so it loads in under two seconds and works offline.
7️⃣ Playwright for the walkthrough video.

Independent learning project, not affiliated with any of the agencies named above or with my employer. Secondary data, transcribed by hand, so please check the source link before quoting a number. Code and data are open (CC BY 4.0). If you work on road safety in Bangladesh and have primary data you can share, I would love to hear from you.

#Bangladesh #RoadSafety #DataVisualization #GIS #OpenData #MapLibre #D3js #Python #RoadAccidents #PublicHealth
