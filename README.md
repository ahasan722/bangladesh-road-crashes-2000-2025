# Deadly Roads: Bangladesh 2000–2025

An independent, interactive look at twenty-five years of road crashes in Bangladesh. Seven chapters, one page, no server: the reporting gap between police, media monitors and the WHO; where the crashes are; the deadliest highways kilometre by kilometre; who dies; when; on which class of road; and a method page that tells you exactly where every number came from.

Live page: https://ahasan722.github.io/bangladesh-road-crashes-2000-2025/

![Deadly Roads screenshot](video/cover.jpg)

## What is on the page

| Chapter | What you can do |
|---|---|
| The gap | Eleven published series on one axis. Toggle sources, switch between deaths, crashes, injuries and deaths per 100,000, linear or log. Hover any year to read every source's figure and its caveat. |
| Where | Division shares of reported crashes from every 8-division table the Road Safety Foundation has published, pooled or period by period, with a play button. Switch to the district layer to see where listed hazardous locations sit. |
| Corridors | Pick N1, N2, N3, N4, N5, N6, N7, N8 or N805. A hazard ribbon beside the real OpenStreetMap alignment counts listed accident-prone locations per 5, 10 or 20 km. Hover a bar to light up that stretch and read what was listed there. Toggle 3D. |
| Who | Deaths by victim group 2020–2025, the full 2024 victim-vehicle breakdown, and collision types pooled from 14 monthly reports. |
| When | A 24-hour dial you drag to select a window of the day, a month-by-month heat strip 2020–2026, and deaths per day in each Eid travel window. |
| Road class | Share of crashes on national, regional, feeder/rural and city roads from every published table, set against the kilometres of each class, and 28 months of road-class counts. |
| Method | Source table, data-handling notes, disclaimer, and links to every CSV. |

Everything renders from static JSON and GeoJSON. The basemap is self-hosted (geoBoundaries and Natural Earth), so the page works offline and loads in under two seconds.

## Where the numbers come from

Nothing on the page is modelled, interpolated or estimated by me. Every figure was transcribed into a long-format CSV with the URL it came from. The main sources:

- **Bangladesh Police / BRTA / ARI-BUET (MAAP)**: police-registered crashes, deaths and injuries, 1998–2025 (with gaps).
- **Bangladesh Jatri Kalyan Samity (BJKS)**: media-monitored annual series 2014–2025 and selected breakdowns.
- **Road Safety Foundation (RSF)**: media-monitored annual series 2019–2025, monthly reports 2020–2026, and breakdowns by vehicle, victim, road class, time of day, division and Eid window, as reproduced in the press.
- **WHO Global Status Report on Road Safety**: modelled deaths and rates for 2007, 2010, 2013, 2016, 2021. **BHIS 2003 and 2016, NHIS 2022–23**: household-survey estimates.
- **Hazardous locations**: 215 blackspots and accident-prone locations on nine national highways, compiled from RHD presentations, Highway Police lists, three ARI-BUET and university papers, and RSF upazila lists; each located to a named place or, failing that, the upazila.
- **Geometry**: OpenStreetMap trunk and primary roads (ODbL) via `ifahimreza/bangladesh-geojson`; geoBoundaries ADM1/ADM2 (CC BY 4.0); Natural Earth rivers and coastlines; BBS census 2011/2022 and World Bank population.

Full URL lists, category mappings and gap tables are in `notes/`.

## Repository layout

```
index.html, css/, js/, lib/, assets/   the site (vanilla JS, MapLibre GL 5, D3 7, Open Sans)
data/*.json, data/highways.geojson      what the page reads, built by the pipeline
data/raw/*.csv                          the transcribed source data, one citation per row
data/raw/roads/                         OSM major routes GeoJSON and routed corridor polylines
pipeline/pipeline.ipynb                 rebuilds data/*.json from data/raw and runs checks
pipeline/build_site_data.py             step 1 and 2 (same code as the notebook)
pipeline/build_sections.py              step 3
pipeline/build_*.py, geo_tools.py       scripts used to derive corridors and hazardous locations from the raw web sources
pipeline/record_demo.py                 records the walkthrough video with Playwright
notes/                                  source notes: URLs, mappings, conflicts, gaps
video/                                  the demo video
```

## Run it yourself

```bash
git clone https://github.com/ahasan722/bangladesh-road-crashes-2000-2025.git
cd bangladesh-road-crashes-2000-2025
python -m http.server 8000      # then open http://localhost:8000
```

To rebuild the data after editing a CSV in `data/raw/`:

```bash
pip install pandas nbclient ipykernel
jupyter nbconvert --execute --to notebook --inplace pipeline/pipeline.ipynb
```

To publish on GitHub Pages: push to `main`, then in the repository go to Settings, Pages, and set the source to `main` branch, root folder. The page is live at the URL above a minute later. There is no build step.

## Known limits

- Police figures count registered cases; BJKS and RSF count media reports; WHO figures are estimates. They measure different things and the page keeps them apart.
- RSF division and time-of-day tables are only reproduced in the press for some months, so the Where and When chapters say which periods they draw on.
- No official national blackspot list has ever been published. The corridor ribbon counts listed locations, not crashes, and 72 of the 215 are located only to upazila level.
- Kilometre positions are measured along the OSM line and differ from RHD chainage by a few kilometres.
- Police 2017 and several 2020–2025 police cells are missing; BJKS 2009–2013 annual reports could not be found online.

## Disclaimer

This is an independent learning project by one person. It is not a product of, endorsed by, or affiliated with the Bangladesh Police, BRTA, the Roads and Highways Department, LGED, ARI-BUET, Bangladesh Jatri Kalyan Samity, the Road Safety Foundation, the WHO, or my employer. All figures are secondary data copied from published reports and press coverage of them; transcription errors are possible and every number links to its source. Nothing here should be used to make engineering or enforcement decisions without going back to the primary data. No individual crash, victim or vehicle is identified.

## Licence

Page, code and the cleaned CSVs: CC BY 4.0. OpenStreetMap data: ODbL. geoBoundaries: CC BY 4.0. Original reports remain under their publishers' terms.

Built by Abid Hasan, Dhaka, October 2026.
