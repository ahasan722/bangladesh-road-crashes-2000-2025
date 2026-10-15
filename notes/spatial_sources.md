# Spatial reference data for the Bangladesh highway crash map: sources, methods, caveats

Collected 2026-10-15. Shell could only reach GitHub raw and PyPI; everything else came through WebSearch / WebFetch.
WebSearch budget ran out (200 calls) before a second pass on RHD/ADB AADT documents; see "Not obtained" at the end.

## Files in /home/claude/work/data/raw/

| file | rows | what |
|---|---|---|
| blackspots.csv | 215 | named blackspots / hazardous road locations / RSF upazila listings on N1, N2, N3, N4, N405, N5, N6, N7, N8, N805 |
| corridors.csv | 123 | ordered waypoints, 3-22 per corridor, routed along the OSM major-routes network; km_from_start is routed chainage |
| population.csv | 72 | 8 divisions + 64 districts, BBS 2011 and 2022 census, area km2 |
| road_network.csv | 31 | RHD national/regional/zilla and LGED upazila/union/village km, 1991-2023 |
| traffic_exposure.csv | 23 | RHD 2016 link counts and JICA forecasts on N1 (Chattogram-Cox's Bazar); one press figure for N5 |
| roads/bd-major-routes.geojson | 4,555 features, ~10,600 km | OSM-derived trunk/primary roads for Bangladesh with `ref` tags (N1..N8, N1xx, R..) |
| roads/corridor_polylines.json | 10 corridors | routed polylines (lng,lat) used for chainage interpolation; drawn from the GeoJSON above |
| roads/admin/bangladesh.geojson | 544 polygons | BBS upazila/thana boundaries (ifahimreza repo, CC BY 4.0) |
| roads/admin/{districts,upazilas,unions}.json | | nuhil/bangladesh-geocode admin lists; districts carry DC-office lat/lon |
| roads/bd-{divisions,districts,upazilas}.json | | ifahimreza admin lists; districts/divisions carry lat/long |

Build scripts (re-runnable, `python3 notes/build_*.py`): `geo_tools.py` (upazila centroids, graph routing, chainage), `build_corridors.py`, `build_blackspots.py`, `build_tables.py`.

## 1. Road geometry (GitHub)

- **ifahimreza/bangladesh-geojson** (`src/data/bd-major-routes.geojson`, ODbL, OSM-derived): 4,555 LineStrings with `osm_id, name, bn_name, ref, highway (trunk|primary), surface, lanes, oneway`. Coverage by ref (sum of segment km; dual carriageways counted twice): N1 718, N2 292, N3 212, N4 208, N5 514, N6 240, N7 259, N8 271, N102 81, N105 76, N405 75, N805 110, N704 83, N509 104, plus N1xx-N8xx feeders and R-roads. Gaps exist (N4 north of Elenga has few nodes; N5 Thakurgaon section is tagged N508; Padma bridge expressway partly untagged), handled in routing by bridging dangling endpoints within 1.2 km and falling back to a straight line only when the network detour exceeds 1.7x crow distance + 6 km (only one straight leg survived: the Paturia-Kazirhat ferry on N5).
  URL: https://raw.githubusercontent.com/ifahimreza/bangladesh-geojson/master/src/data/bd-major-routes.geojson
- **ifahimreza/bangladesh-geojson** `bangladesh.geojson`: BBS upazila boundaries (544 incl. Dhaka/Chattogram thanas). Known label errors found while using it: Pirganj Rangpur/Thakurgaon polygons swapped; "Mohammadpur, Magura" is actually Dhaka city Mohammadpur; "Sreepur, Magura" polygon is Sreepur Gazipur; some sadar upazilas have blank district. `build_blackspots.py` has a FIX map.
- **nuhil/bangladesh-geocode**: districts.json has DC office lat/lon; upazilas/unions have no coordinates.
- GitHub search API is blocked in this session (repo-scoped endpoints only), so repo discovery went through WebSearch. Not downloaded: yasserius/bangladesh_geojson_shapefile (files on Google Drive), fahim-muntasir-niloy (file paths unknown), HDX OSM road export (geo.btaa.org / data.humdata.org not reachable from shell).

## 2. corridors.csv method

Seed points: Wikipedia infobox coords (fetched per page), district HQ coords (bd-districts.json), or BBS upazila representative points. Each seed is snapped to the nearest network node tagged with that corridor's ref (`seed_snap_offset_km` records how far the seed was from the line; >5 km means the seed was a town centre off the bypass, e.g. Thakurgaon, which N5 bypasses via Birganj). Legs are shortest paths through the OSM graph; `km_from_start` is the routed cumulative length. Routed lengths vs Wikipedia totals: N1 438 vs 465 (ends at Teknaf town, not Z1098), N2 286 vs 287, N3 108 vs 115, N4 148 vs 216 (Wikipedia 216 likely includes N405/Jamalpur extension; List_of_roads says 146), N5 510 vs 625 (Wikipedia 625 is RHD's N5 incl. old alignments; List_of_roads says 507), N6 227 vs 204 (Wikipedia 204 is only to Rajshahi; our line continues to Sona Masjid as the infobox west end), N7 252 vs 252, N8 198 vs 202, N805 121, N405 16.
Official route descriptions are paraphrased from en.wikipedia N1..N8 articles (which cite the RHD Road Master Plan); RHD's own road database site was not reachable.

## 3. blackspots.csv sources

RHD has never published its 144 / 209 list. What is public:
1. **UNCRD 2016 (RHD presentation, "Black spot treatment")**: 209 identified (BRTA/police records + 2011 RSU field visit, ARI-BUET analysis), 144 selected for engineering treatment; names only 4 (Dandogaon 29 Mile, Saidpur Sutkir Mor, Kamarpukur, Narail). https://uncrd.un.org/sites/uncrd.un.org/files/9th-est_bangladesh-black-spot-treatment.pdf
2. **Daily Star 14 Oct 2014**: ECNEC approved Tk146 cr for 144 ARI-BUET blackspots; per-district counts only (Rangpur 35, Dhaka 34, Rajshahi 34, Sylhet 14, Khulna 11, Comilla 8, Gopalganj 6, Barisal 2). https://www.thedailystar.net/govt-okays-project-on-road-safety-45747
3. **Daily Star (Rangpur-Panchagarh 140 km, 19 RHD black spots)**: 13 named. https://online91.thedailystar.net/country/news/work-reduce-risk-accident-19-black-spots-136273
4. **Daily Star 2018 (Gaibandha 13 bends, Gaibandha RHD; ARI 7 most vulnerable)**: all 13 named. https://www.thedailystar.net/country/news/road-accidents-kill-112-five-years-1672255
5. **Prothom Alo 2021 (Bangla), Sitakunda-Mirsharai 66 km, 25 spots (Fire Service/Highway Police)**: 10 named. https://www.prothomalo.com/bangladesh/১০-কারণে-ঝুঁকিপূর্ণ-৬৬-কিমি
6. **Dhaka Tribune 2023, Highway Police Sylhet region 55 blackspots on N2**: 13 named. https://www.dhakatribune.com/bangladesh/nation/307192/police-identify-55-accident-blackspots-on
7. **TBS 2020 / Daily Star 2014, Brahmanbaria stretch of N2**: 7 bends + 10 Sarail points. https://www.tbsnews.net/bangladesh/dhaka-sylhet-highway-turns-deathtrap-37415 ; https://www.thedailystar.net/node/37094
8. **Goswami & Morshed 2016 (BIP conference), Joydebpur-Jamuna bridge (N4/N405) hazardous locations, 2009-14 police data, km chainage**: 14 locations. https://bip.org.bd/admin/uploads/member-publication/2016/201708211853221.pdf and .../2017/201708211844441.pdf
9. **JBETE 2017, N8 Dhaka-Barisal HRLs and black spots 2007-12, km chainage**: 14 locations. https://www.slideshare.net/slideshow/characterizing-hazardous-road-locations-and-black-spots-on-route-n8-dhakabarisal-national-highway-of-bangladesh/77448123
10. **JES (KUET) 2024, "Dhaka-Khulna national highway" HRLs 2018-22, km chainage**: 22 locations (N8 + N805). https://banglajol.info/index.php/JES/article/view/82168/53670
11. **Road Safety Foundation (RSF)** upazila-level lists: 2021 (114 locations: 51 extremely + 63 accident-prone) https://old.thefinancialexpress.com.bd/national/114-road-accident-prone-locations-identified-across-country-1619260534 ; 2025 (314 upazilas, 21 extremely high-risk named) https://en.prothomalo.com/bangladesh/accident/zup4j94jlf and https://www.dhakatribune.com/bangladesh/394788/rsf-identifies-314-accident-prone-upazilas-across
12. Single-site press items: Chunati Jangalia (Bonik Barta/Dhaka Tribune 2025), Padua Bazar U-turn (UNB 2025), Nimsar/Katherpul/Kanra/Miah Bazar (bdnews24 2026), Majhkandi (UNB 2021), Trishal (FE 2024), Salehpur/Uthali (DT 2010), Joka/Mulzan (DS 2011), Dhaka-Mawa expressway (Prothom Alo 2024), Patiya 13 points (Jugantor 2026, source unattributed), Highway Police 94 congestion points 2026 (Dhaka Tribune; congestion, not crash, only used for Itakhola/Keranihat/Chandaikona with note).

ARI-BUET's own N1/N2/N5 hazardous-location tables (Sarkar, Hoque et al. 2016 "N2 using GIS"; SWOV-indexed "Observational studies of hazardous road locations on national highways") are not online in full text; only abstracts were found.

### Coordinate derivation (lat_lng_source column)
- `wikipedia infobox (...)`: 72 rows; coords copied from the named place/upazila article infobox (Mirsharai, Sitakunda, Chandina, Daudkandi, Chauddagram, Chakaria, Patiya, Lohagara, Chunati Union, Elenga, Gorai Union, Hatikumrul Union, Kaliakair, Bhanga, Shibchar, Madhabpur, Ashuganj, Sarail, Bhairab Bazar, Gobindaganj, Palashbari, Saidpur, Trishal, Bhaluka, Gaurnadi, Ghior, Madhukhali). Where the spot is a bend/bazar inside that upazila and no finer page exists, the row says "(…Upazila; bend not located)".
- `km post interpolated on routed … polyline`: 41 rows; paper chainage mapped onto the routed corridor after linear calibration between two anchors named in the same paper (N4: Chandra/Elenga; N405: Elenga/bridge end; N8: Tekerhat/Barishal; N805: Bhanga/Mollahat). N8 paper chainage predates the Padma bridge (old Mawa ferry alignment), so its Dhaka-Bhanga points are given at upazila level instead; Madaripur-Barishal points are +/- several km.
- `estimated along corridor`: 17 rows; place sequence known from the article, position interpolated between neighbouring known points on the routed line (Mirsharai-Sitakunda points, Padua Bazar, Nimsar, Miah Bazar, Salehpur, Uthali, Chandaikona).
- `upazila representative point (BBS boundary…)`: 72 rows; the only locator was the upazila (mostly RSF listings and Sylhet/Rangpur police lists). These should be drawn as upazila-level symbols, not point blackspots.
- `routed … waypoint`: the corridor waypoint itself (e.g. Daudkandi, Tekerhat).

## 4. population.csv
- 2022: BBS Population & Housing Census 2022 final (enumerated) as reproduced on en.wikipedia division pages and Divisions_of_Bangladesh / Districts_of_Bangladesh tables. Division totals from Divisions_of_Bangladesh.
- 2011: BBS Census 2011 enumerated figures from en.wikipedia division pages (Dhaka, Chattogram, Barishal, Sylhet, Mymensingh) and individual district articles (Rajshahi, Khulna, Rangpur divisions). Rajshahi/Khulna/Sylhet division 2011 = sum of districts (division pages lacked a 2011 column). Dhaka division 2011 page total (36,433,505) is 146k below the district sum; kept the page total and noted the sum.
- Area: Districts_of_Bangladesh table and division pages (km2). Some district articles carry two area figures; infobox value used.
- National sums: 2011 = 144.19 m (BBS enumerated 144.04 m), 2022 = 165.16 m (BBS 165.16 m). citypopulation.de carries *adjusted* 2011/2022 series (e.g. Dhaka 12.52 m / 15.21 m) which differ from the enumerated figures; not used except as cross-check. https://www.citypopulation.de/en/bangladesh/div/admin/

## 5. road_network.csv
RHD class lengths 1991/2007/2015 (JICA Matarbari EIA Table 3.1-2), 2006 (PIARC 2007, Hossain), 2011 and 2016 (ADB 40540-016 sector assessment), 2021 (ADB 40540-019 ld-04: national 3,991 / regional 4,898 / zilla 13,589 / total 22,478), 2020 HDM total 22,096 (Daily Star), undated RHD "Road Network at a Glance" copy (WFP LCA) and Wikipedia List_of_roads. LGED: 2006 (PIARC) and undated Wikipedia (37,800 / 44,750 / 215,750). No LGED annual report was reachable.

## 6. traffic_exposure.csv
Only one corridor has link-level counts online: N1 Chattogram-Cox's Bazar, RHD Traffic Summary Sheet 2016 (11 links, veh/day and PCU) and JICA 2015 base/forecast PCU per link, both from JICA documents. The 2024 "20,000 veh/day" for Dhaka-Rangpur is a Prothom Alo figure, not an RHD census. RHD's HDM/traffic census portal (rhd.gov.bd) and the ADB 40540-016/-019 and 53382-001 linked documents with AADT tables were not fetchable (robots / permission prompt not answered: https://www.adb.org/sites/default/files/linked-documents/40540-016-ld-05.pdf, 40540-016-ld-04.pdf, 53382-001-ld-04.pdf, 53382-001-ld-05.pdf). ADB 45019-001 TACR (iRAP) has no AADT in text.

## 7. Not obtained / caveats
- No official RHD list of the 144/209 blackspots exists in public; the CSV is a union of press, academic and RSF lists. Treat `year_listed` and `severity_or_rank` as per-source, not comparable.
- RSF "upazila" rows (72) are not point blackspots.
- Osmaninagar (Sylhet) and Tarakanda (Mymensingh) upazilas are missing from the BBS boundary file; parent upazila polygons (Balaganj, Phulpur) used and noted.
- Blocked/unreachable: citypopulation.de Chattogram/Sylhet pages (robots), World Bank 2011 district XLSX (host not allowed), prothomalo Bangla Gaibandha article (fetch error), itvbd (URL too long), LGED feasibility PDF (fetch error), slideshare "Road safety in Bangladesh" (JS wall).
- WebSearch budget exhausted after ~200 calls; a follow-up pass could target: RHD HDM traffic census tables, ARI-BUET N1/N2/N5 HRL papers (ResearchGate), LGED annual report road statistics, BBS 2022 district report PDF for exact 2011 adjusted figures.
