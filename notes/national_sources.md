# National road-crash series for Bangladesh: source notes

All series are kept separate in `national_yearly.csv` (column `source`). Never add or average across sources; they count different things.

## Population (population.csv)

World Bank WDI `SP.POP.TOTL` (UN WPP 2024 based), 1998-2025. BBS census anchors for reference: 2001 enumerated 124.36m / adjusted 130.52m; 2011 enumerated 142.32m / adjusted 152.52m; 2022 enumerated 165.16m / adjusted 169.83m (https://en.wikipedia.org/wiki/Demographics_of_Bangladesh, citing BBS). WDI tracks the adjusted series closely. `deaths_per_100k` in the yearly file is only filled where the source itself printed a rate; recompute from population.csv for the rest.

## 1. Police / BRTA / ARI-BUET (MAAP) series

- What it is: crashes registered as police FIR cases (First Information Reports), coded by ARI-BUET into the MAAP5 database since 1998. Counts fatal, grievous and simple-injury crashes reported to police. Deaths are mostly on-the-spot; hospital deaths after the FIR are rarely updated. Universally described as grossly under-reported (WHO estimates 5-12x higher).
- 1998-2016: three published tabulations of the same police data disagree by year because ARI re-coded the database over time. Used: ICME07 (Anjuman, Hasanat-E-Rabbi, Siddiqui, Hoque 2007, Table 2) for 1998-2003 (https://me.buet.ac.bd/public/old/icme/icme2007/Proceedings/PDF/ICME07-AM-30.pdf); IATSS/CIPRB (Abu Talab) slide Table 1 for 2004-2016 (https://iatss.or.jp/en/event/entry_img/event20_4.pdf). Cross-checks: Mahmud-Ahmed-Hoque, Jurnal Teknologi 70:4 (2014) urban/rural split 1998-2006 (https://journals.utm.my/jurnalteknologi/article/download/3487/2619/9361); ULAB "Death on the Road" 2014 (ARI 2011 vintage) for 1998, 2008-2011 (https://ulab.edu.bd/sites/default/files/Death-on-the-Road.pdf); Ahsan, Daily Star Forum July 2012 (https://tds-images.thedailystar.net/forum/2012/July/road.htm). Conflicts are in the note column (2004-2005 and 2008-2011 differ by 300-800 deaths across vintages).
- RHD series: Mahmud, Talukder, Ahmed, Raihan, Jurnal Teknologi 65:3 (2013) Table 2 gives a Roads and Highways Dept compilation for 1999/2000/2002/2004 (https://journals.utm.my/jurnalteknologi/article/download/2146/1711/4912); kept as a separate source row.
- 2017: no full-year police number found. 2018-2022: police figures quoted in Daily Star 22 Feb 2020 (https://www.thedailystar.net/backpage/news/crash-fatalities-bangladesh-good-trends-undermined-1871680), Daily Star multimedia 2018-2021 review (https://online92.thedailystar.net/star-multimedia/news-multimedia/news/2018-2021-what-has-govt-done-ensure-safe-roads-2906611), Dhaka Tribune 23 Sep 2023 (https://www.dhakatribune.com/amp/bangladesh/326098/road-accidents), Daily Star editorial 17 Jan 2023 (https://www.thedailystar.net/opinion/editorial/news/misguided-approach-road-safety-3223371). Note the Daily Star multimedia piece swaps crash/death columns for 2018-2019; the Feb 2020 article is taken as authoritative.
- 2023 onward: BRTA started its own compilation in January 2023 through 64 district/circle offices, cross-checked against police, DC offices and hospitals; it runs higher than police for injuries (ICCESD 2026 Table 7 compares Police HQ vs BRTA by month, Jul-Sep 2023). Sources: TBS/Dhaka Tribune/FE 16-17 Jan 2024 for 2023 (https://www.tbsnews.net/bangladesh/5024-killed-road-accidents-2023-brta-775982); TBS 1 Jun 2025 for 2023 revised and 2024 (https://www.tbsnews.net/bangladesh/deaths-road-doubles-nationwide-decade-1156681); Bonik Barta 9 Jan 2025 and 21 Jan 2026 for the BRTA 2018-2025 death series (https://en.bonikbarta.com/bangladesh/gyWM582NKumWKeL8). 2024 deaths appear as 5380 / 5479 / 5480 in three articles; 2025 only as 5490 deaths.
- ARI-BUET's own media-based compilation (ICCESD 2026, Mahmud) for 2021: 3203 crashes / 3775 deaths (https://iccesd.kuet.ac.bd/Papers/540.pdf); not a separate series row because only one year is public.

## 2. Bangladesh Jatri Kalyan Samity (BJKS / Passenger Welfare Association)

- Media monitoring of national and regional dailies, online portals and TV, compiled by a "monitoring cell"; road, rail and waterway counted separately; annual report issued in the first/second week of January. Highest of all series; counts include deaths reported in follow-up news. Critics (BRTA, NISCHA) say duplicates are possible.
- Yearly road-only figures 2014-2025 all verified in at least two outlets (see note column). Earliest annual figure found is 2014 (banglanews24 2 Apr 2015, https://www.banglanews24.com/english/national/news/bd/38455.details). 2009-2013 annual reports could not be found online (BJKS was founded ~2007 but its web-visible annual series starts at 2014; the organisation itself only ever cites 2015 onward in its multi-year totals).
- Key URLs: 2015-2019 table (https://en.prothomalo.com/bangladesh/accident/road-accidents-kill-37170-in-5-years-report); 2020 (https://old.thefinancialexpress.com.bd/national/6686-killed-in-road-accidents-in-2020-report-1610180378); 2021 (https://old.thefinancialexpress.com.bd/national/8516-killed-9751-injured-in-accidents-in-2021-jks-1642994119); 2022 (https://www.tbsnews.net/node/561678); 2023 (https://bdnews24.com/bangladesh/pwh9c85xxr); 2024 (https://en.prothomalo.com/amp/story/bangladesh/4s9rk62o86); 2025 (https://www.thedailystar.net/news/bangladesh/accidents-fires/news/over-9000-killed-road-accidents-last-year-jatri-kalyan-samity); 2015-2022 recap (https://www.dhakatribune.com/amp/bangladesh/328635/report-road-accidents-claim-21-lives-daily).
- Monthly series: BJKS publishes monthly press releases (e.g. Jan 2023: 593 crashes / 585 deaths; Oct 2023: 429/437/681; May 2025: 614 deaths; Oct 2025: 528 deaths). Not compiled here.

## 3. Road Safety Foundation (RSF)

- Media monitoring of 7 national dailies, 5 online portals and TV plus own sources; annual report in early/late January; road-only headline plus separate rail and waterway tables. Sits between BRTA and BJKS.
- Series 2019-2025 complete. URLs: 2019-2022 table (https://www.dhakatribune.com/amp/bangladesh/320155/clouded-figures-understanding-road-accidents-in); 2020-2021 (https://mail.thefinancialexpress.com.bd/national/both-deaths-injuries-in-road-accidents-see-sharp-rise-in-2021-1641633812?amp=true); 2022 (https://old.thefinancialexpress.com.bd/national/incidents-of-road-accidents-fatalities-jumped-in-2022-1673077056); 2023 (https://thefinancialexpress.com.bd/national/accident-deaths-report-2023-released-by-rsf); 2024 (https://www.thedailystar.net/news/bangladesh/accidents-fires/news/7294-killed-road-accident-2024-rsf-3794926); 2025 (https://en.prothomalo.com/bangladesh/accident/35tuiqg3oi). Rail/waterway figures for 2024 and 2025 are in the note column.
- RSF also publishes monthly reports (e.g. Jan 2020: 340 crashes / 445 deaths; Sep 2025: 417 deaths).

## 4. Nirapad Sarak Chai (NISCHA) and NCPSRR

- NISCHA (Ilias Kanchan): branch reports plus media monitoring; published annual statistics 2012-2022, then announced on 29 Jan 2024 it would stop publishing because of "controversy" (https://www.dhakatribune.com/bangladesh/338096/nischa-to-stop-publishing-road-accident-stats). 2012 figure not found. 2013-2019 are road figures; 2020-2022 headline totals are ALL MODES (road + rail + waterway), road-only components in the note column. 2018 deaths exist in three versions (3699 raw, 4439 adjusted for expected later deaths, 4039/4839 misprints).
- NCPSRR (National Committee to Protect Shipping, Roads and Railways): media monitoring, 2015-2017 annual figures found (https://www.dhakatribune.com/amp/bangladesh/134353/ncpsrr-road-accidents-killed-4-284-people-in-2017). No later years found.

## 5. WHO Global Status Report on Road Safety (modelled)

- WHO regresses reported deaths against covariates for countries without full vital registration; Bangladesh is modelled every edition. The table in Mahmud (ICCESD 2026, https://iccesd.kuet.ac.bd/Papers/540.pdf) lists each edition's point estimate, 90% CI and the police figure WHO used: 2007: 20038 (14882-29155) vs 3749; 2010: 17289 (15415-19164) vs 2443; 2013: 21316 (17349-25283) vs 1782; 2016: 24954 (20730-29177) vs 2376; 2021: 31578 (27441-35716) vs 5084. 2021 values confirmed directly from WHO GHO API RS_196 / RS_198 (rate 18.6). Rates for 2007 (12.7, PIARC 2011 paper), 2010 (11.6), 2013 (13.6, WHO Bangladesh office), 2016 (15.3, GSRRS 2018 profile; Daily Star says ">15") come from secondary citations; the WHO country-profile PDFs themselves were not fetchable. The World Bank "Delivering Road Safety in Bangladesh" (2020) quotes the WHO range as 20736-21316, so 20736 may be the GSRRS 2009 figure and 20038 a re-estimate; both are noted.
- The annual modelled rate series 2000-2019 (World Bank WDI `SH.STA.TRAF.P5`, WHO GHE based) is included as its own source; it is a smoothed model, not an observation, and newer GHE vintages revise it.
- IHME/GBD: country values are only in the appendix of the Lancet Public Health 2026 road-injury paper; not extracted.

## 6. Health and injury surveys (BHIS)

- BHIS 2003 (ICMH/UNICEF/TASC): ~13000 RTI deaths/yr, 9.2 per 100k (IATSS slide Table 1). BHIS 2016 (CIPRB/DGHS): 23116 deaths (printed 23166 in the slide table), 14.48 per 100k; 64 deaths/day (Daily Star 14 Feb 2017, https://www.thedailystar.net/node/1361245). NHIS 2022-23 (DGHS NCDC/CIPRB): 24233 deaths/yr (Daily Star Oct 2025, https://tds-images.thedailystar.net/news/bangladesh/accidents-fires/news/66-die-injuries-roads-day-4014991). These are household-survey extrapolations (verbal autopsy), independent of both police and media counts.

## 7. Registered vehicles (vehicles_registered.csv)

- Two measures are mixed in the public record and are flagged in the `measure` column: `cumulative_stock` (vehicles registered since independence, never net of scrappage) and `annual_new` (registrations in the calendar year; `annual_new_FY` = July-June fiscal year).
- Sources: Banglapedia BRTA article (cumulative to 2003 and annual 2004-2009 by type, https://en.banglapedia.org/index.php/Bangladesh_Road_Transport_Authority); BBS Statistical Yearbook 2016 stock by type 2011-2016 as reproduced in GED Study 12 (https://gedkp.gov.bd/wp-content/uploads/2021/02/GED-STUDY-NO.-12-TRANSPORTATION-AND-QUALITY-INFRASTRUCTURE_FINAL-1.docx); Financial Express and Daily Star BRTA reports for annual 2016-2020; CEIC (BRTA) page for annual totals/by type 2022-2024 and all-time highs/lows (https://www.ceicdata.com/en/bangladesh/motor-vehicle-registered); Daily Star / Wikipedia for 2020, 2022, 2024 stock. brta.gov.bd itself is robots-blocked for the fetcher.
- Gaps: no by-type stock for 2017-2023; annual registrations by type patchy before 2019 and after 2022; 2021 annual total not found (CEIC has it behind paywall); 2025 only motorcycles approx.

## Definitional summary

| Source | Unit counted | Deaths definition | Coverage |
|---|---|---|---|
| Police/ARI (MAAP) | FIR cases | mostly on-spot, FIR-recorded | 1998-2022 |
| BRTA (own) | district office reports, cross-checked | includes some hospital deaths | 2023-2025 |
| BJKS | news items | any death reported in media incl. follow-ups | 2014-2025 |
| RSF | news items (7 dailies + portals + TV) | as reported in media | 2019-2025 |
| NISCHA | branches + media | raw + adjustment for later deaths | 2013-2022 |
| NCPSRR | media | as reported | 2015-2017 |
| WHO GSRRS | model | all RTI deaths within 30 days | 2007/10/13/16/21 |
| BHIS/NHIS | household survey | verbal autopsy RTI deaths | 2003, 2016, 2022-23 |
