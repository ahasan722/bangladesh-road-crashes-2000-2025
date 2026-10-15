# Breakdown sources: RSF and BJKS road-crash disaggregations

Generated 2026-10-15. Data in `../raw/breakdowns.csv` (tidy, one row per value) and `../raw/monthly.csv`.
All values are as printed in the cited article; nothing interpolated. Where two outlets disagree both rows are kept with a `note`.
The RSF Bangladesh website (roadsafetyfoundation.org resolves to the UK charity; roadsafetyfoundation.org.bd / rsfbd.org were unreachable or robots-blocked, and the sandbox proxy refuses them) so every figure comes from press reproductions of RSF/BJKS press releases.
Search budget (200 WebSearch calls) was exhausted; ~110 pages were fetched. Gaps below are what was not reachable in this pass, not confirmation that the data was never published.

## Column conventions (breakdowns.csv)

- `source`: RSF | BJKS | NISCHA | SCRF | BRTA (last three included only for context where they were the only series found).
- `period`: `annual`, `YYYY-MM`, `eid_fitr_YYYY`, `eid_azha_YYYY`, or a range such as `2024-01_to_2024-09`, `2019-01_to_2024-06`, `2020_to_2026-07`.
- `dimension`: total | vehicle_type | vehicles_involved | road_class | time_of_day | division | district | dhaka_city | month | victim | collision_type | other_mode | economic_loss | change_vs_prev | change_5yr.
  - `vehicle_type` = deaths (or accidents) by the vehicle the VICTIM was in/on. `vehicles_involved` = share/count of vehicles implicated in crashes (RSF) or "vehicles involved" (BJKS). Keep separate; RSF publishes both.
- `measure`: accidents | deaths | injuries | missing | share_pct | count | days | deaths_per_day | value. The `note` says what a `share_pct` is a share of when the article said.
- 2026 rows exist (Jan, Mar, Apr, Jun, Jul, Aug, Sep 2026; Eid-ul-Azha 2026; BJKS Jun 2026) because the fetched pages covered them. They are flagged "outside requested scope" in `note`.

## Category label mapping (as published -> csv category)

### RSF vehicle_type (victim's vehicle)
| csv category | labels as published (varies by article) |
|---|---|
| motorcycle | motorcycle / motorbike riders and passengers / two-wheeler |
| bus | bus passengers / passenger buses |
| truck_pickup_goods | trucks, covered vans, pickups, tractors, trolleys, lorries, drum trucks, oil tankers, cargo vehicles / goods-carrying vehicles / goods-laden vehicles / heavy vehicle occupants |
| car_microbus | private cars, microbuses, SUVs, ambulances, jeeps |
| three_wheeler | three-wheelers (CNG auto-rickshaws, easy-bikes, auto-rickshaws, battery vans, legunas, Mishuks) |
| local_vehicle | locally made vehicles (Nasimon, Korimon/Kariman, Votvoti/Bhotbhoti, Mahindra, Tomtom) |
| bicycle_rickshaw | bicycles, paddle rickshaws, rickshaw vans / cyclists and rickshaw passengers |

### RSF road_class
| csv | published |
|---|---|
| national_highway | national highways / highways |
| regional_road | regional roads / regional highways / local roads (one 2026 article) |
| rural_road | rural roads / village roads / feeder roads |
| city_road | city roads / urban roads / city streets / urban areas |
| other | other places / other locations (ferry docks, river banks, crop fields, driving training fields) |

### RSF collision_type
| csv | published |
|---|---|
| lost_control | loss of vehicle control / losing control of the wheel / driver lost control |
| head_on | head-on collisions / "collision" (2023 articles used plain "collision" for this band) |
| hit_pedestrian | pedestrians hit / pushed / run over / knocked down / struck |
| rear_end | hitting the rear of vehicles / rear-end collisions / vehicles striking others from behind |
| other | other / other reasons / other causes / unidentified |

### RSF time_of_day
RSF publishes six bands labelled: dawn (or early morning) / morning / noon / afternoon / evening (some articles "dusk" + "evening") / night. Published as % of accidents. Clock boundaries were never given in any fetched article; keep labels, do not map to hours.
Full 6-band sets captured: 2025-01, 2025-07, 2024-10, eid_fitr_2025, 2026-06. Partial sets: 2025-03, 2022-11, 2026-07, 2026-08, 2022 (Dhaka city only), 2023 (child deaths only), 2022-01_to_2022-10 (motorcycle only).

### RSF division
Eight divisions as spelled in the csv: Dhaka, Chattogram, Rajshahi, Khulna, Rangpur, Barishal, Sylhet, Mymensingh (articles use Chittagong/Barisal spellings interchangeably; normalised). `share_pct` is share of accidents unless the note says share of deaths. Most monthly articles print only the highest and lowest division; full 8-division shares captured for 2022-06, 2022-07, 2022-08, 2024-10, 2025-08, 2025-09, 2025-10, 2025-11, 2026-06, eid_fitr_2025 (accidents and deaths), eid_azha_2026 (deaths).

### RSF victim
women, children, students, pedestrian, drivers_helpers ("vehicle drivers and their assistants / transport workers"), working_age_18_65, men, plus occupational groups when printed (police, ansar, teachers, journalists, doctors, ngo_officials, businesspersons, local_political_leaders).

### BJKS
- vehicles_involved: motorcycle; bus; truck_pickup_lorry_covered_van; car_jeep_microbus; cng_autorickshaw; battery_rickshaw_easybike ("battery-operated rickshaws and easybikes / battery-run human haulers"); other_three_wheeler; local_vehicle_leguna_tractor ("Nasiman, Kariman, Mahindra, tractors, Leguna").
- road_class: national_highway; regional_highway; feeder_road; dhaka_city; chattogram_city; railway_crossing (BJKS reports city/rail-crossing shares in the same breakdown so they are kept in road_class).
- collision_type: hit_pedestrian ("vehicles running over/ramming pedestrians"); head_on; lost_control_ditch ("vehicles losing control and falling into ditches"); train_vehicle; clothing_in_wheel ("scarves/clothing entangled in wheels"); other/miscellaneous.
- victim: drivers; transport_workers; pedestrian; students; teachers; law_enforcement (police/BGB/Ansar); women; children; journalists; physicians/doctors; freedom_fighters; lawyers; engineers; political_activists; army; firefighters. Measure is `deaths` unless note says injured.

## Coverage summary

### RSF annual
| Year | totals | vehicle_type | road_class | time_of_day | division | victim | collision | econ loss |
|---|---|---|---|---|---|---|---|---|
| 2019 | NOT FOUND (only NISCHA 2019 and BJKS 2019 surfaced) | motorcycle via 2019-Jun2024 series only | - | - | - | - | - | - |
| 2020 | yes | motorcycle | counts for 5 classes | - | Dhaka/Sylhet shares | women, children, pedestrian, drivers | - | - |
| 2021 | yes | motorcycle | - | - | Dhaka/Rangpur | women, children, pedestrian, drivers | - | - |
| 2022 | yes | motorcycle (3,091) | - | Dhaka-city night/early morning | Dhaka (two conflicting death counts) | women, children, students, working-age | motorcycle-only (Jan-Oct) | Tk 18,046 cr (Prothom Alo) vs Tk 23,460 cr (Daily Star) |
| 2023 | yes | motorcycle; child-death shares only | child deaths: regional >37% | child deaths: afternoon >1/3 | - | women, children (+ child age bands) | - | - |
| 2024 | yes | full 7-class deaths + shares | 4-class shares | - | Dhaka/Sylhet + Dhaka city | women, children, pedestrian, drivers | - | Tk 21,800 cr |
| 2025 | yes | motorcycle; vehicles_involved shares; Dhaka city victim shares | - | Dhaka night 41.56% | Dhaka; Dhaka city | women, children, pedestrian, working-age | - | Tk 25,550.85 cr |
Cumulative: Jan-Sep 2024 (full vehicle/road breakdown); Jan 2019-Jun 2024 (vehicle, road, division, victim, Tk 87,884 cr); Oct 2024-Sep 2025 rolling; Dhaka city 2020-Jul 2026 (time of day in deaths).

### RSF monthly (monthly.csv)
Months captured: 2020-01 (back-ref), 2020-08, 2021-01, 2021-05 (back-ref), 2021-06, 2022-04..09, 2022-11, 2023-02, 2023-03, 2023-06..12, 2024-02, 2024-03 (deaths only), 2024-04 (deaths/injuries only), 2024-06, 2024-09, 2024-10, 2025-01..04, 2025-07..12, plus 2026-01/03/04/06/07/08/09. Jan+Feb 2022 only as a two-month combined row in breakdowns.csv.
Missing (not reached before search budget ran out): 2020-02..07, 2020-09..12, 2021-02..04, 2021-07..12, 2022-01, 2022-02, 2022-03, 2022-10, 2022-12, 2023-01, 2023-04, 2023-05, 2023-08 (only accidents/deaths as back-ref), 2023-10 (back-ref only), 2024-01, 2024-05, 2024-07, 2024-08, 2024-11, 2024-12, 2025-05, 2025-06 (all June-2025 search hits turned out to be June 2026 articles). Known TBS headlines that exist but were not fetched: "Road accidents killed 679 in April" (2024), "Road accidents in November claims 467" (2023), "378 deaths in 403 road accidents in August" (2023).
TBS node 646738 "408 killed in 491 road accidents in May" gives a very full breakdown but prints no year; recorded as year "unknown".
Sub-breakdowns per month: road_class counts in nearly every captured month 2022-07 onward; collision_type in 2023-02, 2023-06, 2023-07, 2024-02, 2024-10, 2025-01..03, 2025-07, 2025-09, 2026-*; full 7-class victim-vehicle deaths in 2023-09 (4 classes), 2023-11, 2024-10, 2025-01, 2025-03, 2025-07, 2025-09, 2025-12, 2026-*; division share sets listed above; Dhaka city most months from 2023-09.

### RSF Eid
eid_azha 2020 (14 d, back-ref), 2021 (11 d, full), 2022/2023/2024 (deaths only from series), 2025 (12 d, full incl. vehicles involved, road, collision, division, district, Tk 1,218.72 cr), 2026 (13 d, full).
eid_fitr 2023 (14 d) and 2024 (15 d) totals from series; 2025 (11 d) full incl. 6-band time of day, 8-division accident and death shares, 16-class vehicles-involved counts.
Not found: eid_fitr 2019-2022 RSF, eid_azha 2019 RSF.

### BJKS annual
2015-2022 accidents+deaths series (one source); injuries for 2018-2024; 2019: vehicles involved, collision, road class, occupational victims; 2021: vehicles involved; 2022: road class incl. metro, women/children, rail/water; 2023: fullest (vehicles involved 7 classes, road, metro, collision, 14 victim groups, with DT vs bdnews24/FE conflicts preserved); 2024: totals, motorcycle, rail/water, pct change; 2025: totals only (Daily Star editorial) + Tk 60,000 cr/yr unattributed loss. 2014-Sep 2024 cumulative (60,980 accidents).
Not found: BJKS 2009-2014 annuals, BJKS 2016-2018 breakdowns, BJKS 2024 vehicle/road/collision/victim breakdown (press pieces fetched did not reproduce it), BJKS 2025 breakdown.

### BJKS monthly
2023-01 (full), 2023-03 (totals), 2024-01 (full incl. injured-victim groups), 2024-04 (totals+motorcycle), 2024-09 (full), 2025-05 (full), 2026-06 (full). BJKS Eid: fitr 2022, azha 2022 (Al Jazeera), fitr 2024 (back-ref), fitr 2025 (full), azha 2025.

### Other series captured for context
NISCHA 2018/2019 annual; SCRF Jan-Jun 2019 monthly (with women/children deaths); BRTA Jul 2025.

## Known conflicts recorded as paired rows
- RSF 2022 economic loss: 18,046 vs 23,460 Tk crore. RSF 2022 Dhaka division deaths: 1,841 vs 2,044.
- RSF 2023-07 injuries: 1,126 (TBS) vs 1,256 (DT).
- RSF 2025 motorcycle deaths: 2,672 (Prothom Alo) vs 2,671 (bdnews24, FE, UNB series).
- RSF 2025-08/2025-09 road-class counts: UNB/DT print identical 214/135/42/60 for both months; bdnews24 Sept counts (161/139/57/89) sum to 446 and are flagged preferred.
- RSF 2022-07/2022-08 road-class counts identical (252/199/109/64/8) in two UNB/TBS articles; flagged.
- RSF 2022-09 road-class counts sum to 507 against 407 accidents; as printed.
- RSF 2023-02 motorcycle deaths 96 printed alongside 40.24%; as printed.
- RSF 2025-12 motorcycle share 26.04% printed against 204/503; as printed.
- RSF 2024-02 motorcycle share: 37.86% and 32.07% both printed in same article.
- BJKS 2023 victim counts: Dhaka Tribune set vs bdnews24/FE set (both kept).
- BJKS 2015: 6,581/8,642 (DT series) vs 6,561/6,642 (TBS).
- BJKS 2022 change vs 2021: TBS prints deaths +19.89% / injuries +27.43%; UNB prints deaths +27.43%.
- BJKS 2025-05 injuries: 1,196 road; combined total printed as 1,210 (Observer) and 1,270 (UNB/DT).

## URLs used (108)
### RSF annual / cumulative
- https://old.thefinancialexpress.com.bd/national/road-crashes-took-5431-lives-last-year-says-report-1610100641
- https://d11.thedailystar.net/online/news/2020-more-5000-killed-road-waterway-accidents-report-2024477
- https://unb.com.bd/category/Bangladesh/perilous-roads-in-bangladesh-6284-killed-in-2021-rsf/85512
- https://old.thefinancialexpress.com.bd/national/incidents-of-road-accidents-fatalities-jumped-in-2022-1673077056
- https://en.prothomalo.com/bangladesh/city/p07evttpqj
- https://www.thedailystar.net/opinion/editorial/news/safe-roads-smart-cities-3216316
- https://en.prothomalo.com/bangladesh/accident/nr3n0krxfx
- https://www.dhakatribune.com/bangladesh/298626/report-motorcycle-accidents-killed-19.28%25-more
- https://www.banglanews24.com/english/national/news/bd/102376.details
- https://www.dhakatribune.com/bangladesh/337884/report-over-1-100-children-killed-in-road
- https://en.prothomalo.com/bangladesh/accident/fb1tip4hiv
- https://en.prothomalo.com/bangladesh/m4kzejfpvx
- https://www.dhakatribune.com/bangladesh/370317/report-bangladesh-witnessed-7-294-road-accident
- https://thefinancialexpress.com.bd/home/tk-218-billion-human-resources-lost-as-7294-killed-rsf
- https://observerbd.com/news/506510
- https://www.dhakatribune.com/bangladesh/372490/how-long-will-bangladesh%E2%80%99s-highways-remain-deadly
- https://www.dhakatribune.com/bangladesh/362548/report-over-5-500-lives-lost-on-roads-in-9-months
- https://www.dhakatribune.com/bangladesh/362084/35-384-killed-in-road-railway-waterway-accidents
- https://thefinancialexpress.com.bd/national/over-35000-killed-53000-injured-rsf
- https://en.prothomalo.com/bangladesh/accident/o9857h7tqw
- https://en.prothomalo.com/bangladesh/accident/zp74le7o3l
- https://en.prothomalo.com/bangladesh/accident/35tuiqg3oi
- https://bdnews24.com/bangladesh/f02d0595c9ee
- https://thefinancialexpress.com.bd/national/road-accidents-rise-60pc-deaths-36pc-in-five-years
- https://unb.com.bd/category/Bangladesh/219-killed-in-409-road-accidents-in-dhaka-in-2025/177856
- https://bdnews24.com/bangladesh/701eaea5f5ef
- https://unb.com.bd/category/Bangladesh/over-15700-killed-in-motorbike-crashes-young-people-make-up-58pc-rsf/192563
- https://www.dhakatribune.com/bangladesh/394788/rsf-identifies-314-accident-prone-upazilas-across (no per-district numbers)
### RSF monthly
- https://www.dhakatribune.com/bangladesh/237902/road-crashes-kill-484-in-january
- https://en.prothomalo.com/bangladesh/road-accidents-claim-379-lives-in-august
- https://mail.thefinancialexpress.com.bd/national/road-crashes-claim-398-lives-in-june-1625657975?amp=true
- https://old.thefinancialexpress.com.bd/public/print/bangladesh-sees-848-road-crashes-in-two-months-that-claim-1012-lives-1646537892
- https://en.prothomalo.com/bangladesh/accident/543-killed-in-427-road-accidents-in-april-rsf
- https://today.thefinancialexpress.com.bd/print/641-killed-in-528-crashes-in-may-1654538899
- https://unb.com.bd/category/bangladesh/road-crashes-claim-524-lives-in-june/96260
- https://www.dhakatribune.com/bangladesh/290270/report-road-crashes-claim-524-lives-in-june
- https://dhakacourier.com.bd/index.php/news/Society/Road-crashes-claim-524-lives-in-June/5419
- https://unb.com.bd/category/Bangladesh/739-lives-lost-on-roads-in-july-in-bangladesh-rsf/98335
- https://www.tbsnews.net/node/489326
- https://unb.com.bd/category/Bangladesh/476-people-killed-in-407-road-accidents-in-september-road-safety-foundation/101890
- https://www.dhakatribune.com/bangladesh/299745/report-554-killed-in-road-accidents-in-november
- https://unb.com.bd/category/Bangladesh/487-deaths-in-439-road-accidents-in-feb-road-safety-foundation/111468
- https://www.dhakatribune.com/bangladesh/306376/road-safety-foundation-487-deaths-in-439-road
- https://www.dhakatribune.com/bangladesh/308345/report-564-people-lost-lives-in-486-road
- https://unb.com.bd/category/Bangladesh/516-deaths-in-559-road-accidents-in-june-road-safety-foundation/118647
- https://www.dhakatribune.com/bangladesh/320232/report-559-road-accidents-in-june-claimed-516
- https://www.tbsnews.net/node/678302
- https://www.dhakatribune.com/bangladesh/321857/report-511-road-accidents-in-july-claimed-573
- https://www.dhakatribune.com/bangladesh/327393/report-394-lives-lost-on-roads-across-bangladesh
- https://unb.com.bd/category/Bangladesh/467-lives-lost-on-roads-across-country-in-nov-road-safety-foundation/127181
- https://www.dhakatribune.com/bangladesh/333398/report-467-lives-lost-on-roads-across-bangladesh
- https://www.dhakatribune.com/bangladesh/335789/report-512-killed-in-december-road-accidents
- https://observerbd.com/news.php?id=464297
- https://www.tbsnews.net/node/808498
- https://today.thefinancialexpress.com.bd/print/679-killed-934-injured-rsf-1715531825
- https://tds-images.thedailystar.net/news/bangladesh/accidents-fires/news/696-killed-road-accidents-june-3930696
- https://www.dhakatribune.com/bangladesh/361057/426-lives-lost-on-the-roads-in-september
- https://www.banglanews24.com/english/national/news/bd/157822.details
- https://en.ittefaq.com.bd/9582/469-dead-837-injured-in-oct-road-crashes-in
- https://thefinancialexpress.com.bd/national/bd-sees-621-road-accidents-in-jan-608-people-killed
- https://www.dhakatribune.com/bangladesh/372754/608-lives-lost-on-roads-in-january-highest-in
- https://en.prothomalo.com/bangladesh/rzlxsq34sz
- https://www.dhakatribune.com/bangladesh/375738/road-accident-596-crashes-claim-578-lives-in-last
- https://unb.com.bd/category/Bangladesh/accidents-kill-578-in-february-only-slightly-lower-than-previous-month/155047
- https://www.dhakatribune.com/bangladesh/378488/road-crashes-claim-604-lives-in-march
- https://unb.com.bd/category/Bangladesh/over-600-killed-in-road-accidents-across-bangladesh-in-march/157473
- https://en.prothomalo.com/bangladesh/accident/02bmtykq8x
- https://www.dhakatribune.com/bangladesh/380943/588-killed-1-124-injured-in-road-accidents-in
- https://www.banglanews24.com/english/national/news/bd/174917.details
- https://www.observerbd.com/news/525120
- https://www.tbsnews.net/node/646738 (year unknown)
- https://www.dhakatribune.com/bangladesh/389368/rsf-report-47-students-among-418-killed-in-road
- https://www.banglanews24.com/english/national/news/bd/183437.details
- https://bdnews24.com/bangladesh/2af125ed63e2
- https://en.prothomalo.com/bangladesh/accident/92uxvdz8dp
- https://www.dhakatribune.com/bangladesh/393162/rsf-417-lives-lost-on-roads-in-september-in
- https://bdnews24.com/bangladesh/5e6010dd20b6
- https://unb.com.bd/category/Bangladesh/bangladesh-sees-rise-in-road-accidents-deaths-in-october-rsf/173371
- https://www.dhakatribune.com/bangladesh/396791/rsf-bangladesh-sees-rise-in-road-accidents
- https://www.jagonews24.com/en/national/news/87254
- https://www.dhakatribune.com/bangladesh/399002/rsf-bangladesh-sees-rise-in-road-accidents
- https://en.prothomalo.com/bangladesh/5adgycvhw6
- https://timesofoman.com/article/166899-bangladesh-records-503-deaths-in-547-road-accidents-in-december-2025-report
- 2026: https://unb.com.bd/category/bangladesh/57-children-among-487-killed-in-january-road-crashes-in-bangladesh-rsf/179885 ; https://en.prothomalo.com/bangladesh/3f7xzpme5e ; https://unb.com.bd/category/Bangladesh/nearly-100-children-among-532-killed-in-march-road-crashes-in-bangladesh-rsf/183405 ; https://thefinancialexpress.com.bd/national/576-road-accidents-in-march-leave-532-dead-2221-hurt-rsf ; https://bdnews24.com/bangladesh/b2131eb8a841 ; https://bdnews24.com/bangladesh/9a8381f35de8 ; https://www.jagonews24.com/en/national/news/94027 ; https://en.prothomalo.com/bangladesh/accident/9a1ejcds7r ; https://www.dhakatribune.com/bangladesh/414380/rsf-road-crashes-claim-438-lives-in-june ; https://unb.com.bd/category/Bangladesh/road-crashes-claim-438-lives-in-june-rsf/189895 ; https://unb.com.bd/category/Bangladesh/bangladeshs-roads-remain-deadly-416-killed-in-july-alone/192431 ; https://en.prothomalo.com/bangladesh/4h7auhdz84 ; https://bdnews24.com/bangladesh/3fa3811aa635 ; https://unb.com.bd/category/Bangladesh/road-crashes-claim-481-lives-in-august-alone/194804 ; https://unb.com.bd/category/Bangladesh/14-deaths-a-day-as-423-killed-in-road-crashes-in-september-rsf/196955 ; https://www.jagonews24.com/en/national/news/96755
### RSF Eid
- https://thefinancialexpress.com.bd/public/national/road-accidents-kill-207-people-in-11-days-around-eid-ul-azha-1627297498
- https://www.dhakatribune.com/bangladesh/378096/eid-holiday-turns-deadly-over-249-lives-lost-in
- https://www.dhakatribune.com/bangladesh/384130/rsf-road-accidents-claim-312-lives-in-12-days
- https://www.dhakatribune.com/bangladesh/384402/report-road-accidents-in-bangladesh-nearly-double
- https://www.dhakatribune.com/bangladesh/411719/rsf-281-killed-in-road-crashes-during-eid-travel
### BJKS
- https://www.dhakatribune.com/bangladesh/328635/report-road-accidents-claim-21-lives-daily (2015-2022 series)
- https://www.thedailystar.net/backpage/road-accident-in-bangladeh-21-died-every-day-1852867 (2019)
- https://old.thefinancialexpress.com.bd/national/8516-killed-9751-injured-in-accidents-in-2021-jks-1642994119
- https://www.tbsnews.net/node/361057 ; https://www.jagonews24.com/en/national/news/60005 (2021)
- https://unb.com.bd/category/Bangladesh/bangladesh-sees-9951-road-accident-deaths-in-2022-highest-in-8yrs-report/107517 ; https://www.tbsnews.net/node/561678 ; https://www.dhakatribune.com/bangladesh/301802/road-accident-fatalities-in-2022-the-highest-in ; https://mail.thefinancialexpress.com.bd/national/bangladesh-road-deaths-hit-eight-year-high-in-2022-1672642851?amp=true
- https://bdnews24.com/bangladesh/pwh9c85xxr ; https://www.tbsnews.net/node/774622 ; https://thefinancialexpress.com.bd/national/7902-lives-lost-in-road-accidents-in-2023-study-finds ; https://www.dhakatribune.com/bangladesh/336755/report-bangladesh-saw-7-902-road-fatalities-last (2023)
- https://unb.com.bd/category/Bangladesh/road-fatalities-in-bangladesh-8543-lost-lives-in-2024/150389 ; https://www.jagonews24.com/en/national/news/79541 ; https://tds-images.thedailystar.net/news/bangladesh/news/road-accidents-kill-over-8500-2024-3791541 (2024)
- https://www.dhakatribune.com/bangladesh/362619/bangladesh-sees-60-980-road-accidents-killing (2014-Sep 2024)
- https://www.thedailystar.net/opinion/editorial/news/preventable-deaths-roads-must-stop-4074051 (2025)
- Monthly: https://www.dhakatribune.com/bangladesh/304218/report-january-saw-585-deaths-from-593-road ; https://www.dhakatribune.com/bangladesh/340314/report-road-accidents-claimed-486-lives-in ; https://d11.thedailystar.net/news/bangladesh/accidents-fires/news/708-killed-683-road-accidents-april-report-3616021 ; https://unb.com.bd/category/Bangladesh/road-accidents-claim-498-lives-in-sept-jatri-kalyan-samity/145027 ; https://www.dhakatribune.com/bangladesh/383639/jatri-kalyan-samity-may-sees-614-road-fatalities ; https://unb.com.bd/category/Bangladesh/may-sees-614-road-fatalities-in-bangladesh-jatri-kalyan-samity/161723 ; https://www.observerbd.com/news/529400 ; https://www.banglanews24.com/english/national/news/bd/177805.details ; https://unb.com.bd/category/Bangladesh/532-road-accidents-kill-463-in-june-jatri-kalyan-samity/190598
- Eid: https://www.aljazeera.com/news/2022/7/24/eid-holidays-in-bangladesh-saw-record-road-accident-deaths-group ; https://www.dhakatribune.com/bangladesh/378229/passenger-welfare-association-322-killed-in-315 ; https://www.dhakatribune.com/bangladesh/383925/390-killed-in-15-days-of-eid-travel-motorbikes ; https://observerbd.com/news/529881 ; https://www.banglanews24.com/english/national/news/bd/178157.details
### Context series
- NISCHA: https://old.thefinancialexpress.com.bd/national/road-accidents-claim-5227-lives-in-2019-1578136813 ; https://www.dhakatribune.com/bangladesh/197879/year-2019-a-surge-in-road-accidents-fatalities
- SCRF: https://www.dhakatribune.com/bangladesh/181330/report-2-329-killed-in-2-159-road-accidents-from

## Fetch failures (content not obtained)
asianews.network/?p=249140 (429), tbsnews 354856 (RSF 2021), 434166 (RSF May 2022), 1480066, 1535541, 380422, jhr.ssu.ac.ir PDF (robots), newagebd 302591 and 268849, roadsafetyfoundation.org.bd (robots), rsfbd.org, thedailystar tag pages (robots), tbsnews taxonomy 157294, TBS 1499951 (students 2019-2026).
