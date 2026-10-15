"""Build blackspots.csv from the public blackspot / hazardous-road-location lists collected on
2026-10-15 (see notes/spatial_sources.md). Coordinates come from, in order of preference:
  wikipedia infobox            -> coords copied from the place's en.wikipedia infobox
  km_post on routed corridor   -> point interpolated at the paper's km post along the routed
                                  OSM polyline of that corridor (corridor_polylines.json), after
                                  calibrating the paper's chainage to the routed chainage with
                                  two anchor points named in the same paper
  upazila representative point -> BBS upazila boundary representative point (bangladesh.geojson)
  district HQ                  -> bd-districts.json district HQ coordinate
Never invented: if the only locator is the upazila, that is stated in lat_lng_source."""
import csv, json, sys
sys.path.insert(0, "/home/claude/work/data/notes")
from geo_tools import *

U = load_upazilas()
D = {d["name"]: (float(d["long"]), float(d["lat"])) for d in json.load(open(RAW + "bd-districts.json"))["districts"]}
POLY = json.load(open(RAW + "corridor_polylines.json"))

# BBS boundary file has a few mislabelled polygons (checked against district HQ coords):
# Pirganj: 'rangpur' polygon is in Thakurgaon and vice versa; Mohammadpur: 'magura' polygon is Dhaka city.
FIX = {("pirganj", "rangpur"): ("pirganj", "thakurgaon"), ("pirganj", "thakurgaon"): ("pirganj", "rangpur"),
       ("mohammadpur", "magura"): ("mohammadpur", ""), ("gazipur sadar", "gazipur"): ("gazipur sadar", ""),
       ("kaliakair", "gazipur"): ("kaliakair", ""), ("hajiganj", "chandpur"): ("hajiganj", "")}
def upz(name, dist=""):
    key = FIX.get((name.lower(), dist.lower()), (name.lower(), dist.lower()))
    for k, v in U.items():
        if k == key or (not key[1] and k[0] == key[0]):
            return v["lat"], v["lng"]
    raise KeyError((name, dist))

def chain(ref, km, anchors):
    """anchors: [(paper_km, routed_km), (paper_km, routed_km)] -> linear calibration."""
    (p1, r1), (p2, r2) = anchors
    rk = r1 + (km - p1) * (r2 - r1) / (p2 - p1)
    return point_at_km(POLY[ref], rk)

rows = []
def add(highway, name, upazila, district, lat, lng, src, year, sev, url, note="", km=""):
    rows.append(dict(highway=highway, name_place=name, upazila=upazila, district=district, km_post=km,
                     lat=lat, lng=lng, lat_lng_source=src, year_listed=year, severity_or_rank=sev, source_url=url, note=note))

W = "wikipedia infobox"
UP = "upazila representative point (BBS boundary; spot not located more precisely)"
HQ = "district HQ coordinate (bd-districts.json)"

# ---------------------------------------------------------------- N1 Dhaka-Chattogram
u = "https://www.prothomalo.com/bangladesh/১০-কারণে-ঝুঁকিপূর্ণ-৬৬-কিমি"
u2 = "https://en.prothomalo.com/bangladesh/accident/zup4j94jlf"
MIR = upz("Mirsharai", "Chattogram"); SIT = (22.617, 91.6617)
# Sitakunda-Mirsharai 66 km (City Gate -> Dhumghat); interpolate named points along routed N1 between
# Sitakunda (198.5 km) and Baraiyarhat/Mirsharai (172.1 km) using their relative order in the article.
N1_SM = [  # (name, upazila, approx routed km on N1 polyline, how)
    ("Dhumghat Bridge (Mirsharai north boundary, Feni river)", "Mirsharai", 158.0, "estimated along corridor: Mirsharai-Feni district boundary on routed N1"),
    ("Baraiyarhat (municipal market area)", "Mirsharai", 164.0, "estimated along corridor: Baraiyarhat bazar on routed N1 (~8 km S of Dhumghat)"),
    ("BSRM Gate area", "Mirsharai", 168.0, "estimated along corridor (order in source)"),
    ("Sonapahar Bishwaroad (Mirsharai EZ junction)", "Mirsharai", 171.0, "estimated along corridor (order in source)"),
    ("Mithachhara Bazar U-turn", "Mirsharai", 174.0, "estimated along corridor (order in source)"),
    ("Sufia Road junction", "Mirsharai", 177.0, "estimated along corridor (order in source)"),
    ("Nizampur College area", "Mirsharai", 179.0, "estimated along corridor (order in source)"),
    ("Boro Takia Bazar U-turn", "Mirsharai", 181.0, "estimated along corridor (order in source)"),
    ("Boro Darogarhat", "Sitakunda", 185.0, "estimated along corridor: Sitakunda-Mirsharai boundary"),
    ("Choto Darogarhat", "Sitakunda", 188.0, "estimated along corridor (order in source)"),
    ("Sitakunda bus stand", "Sitakunda", 198.5, "routed N1 waypoint at Sitakunda (wikipedia infobox seed)"),
    ("Fouzdarhat - Bandar link road junction", "Sitakunda", 222.0, "estimated along corridor: Fouzdarhat ~6 km N of City Gate"),
]
for name, upa, km, how in N1_SM:
    lat, lng = point_at_km(POLY["N1"], km)
    add("N1", name, upa, "Chattogram", lat, lng, how, 2021, "one of 25 spots on Sitakunda-Mirsharai 66 km (Fire Service / Highway Police data)", u,
        "Prothom Alo 2021 (Bangla): 232 crashes, 42 deaths Jan-Sep 2021 on the 66 km; RSF 2025 also lists Mirsharai Boro Darogarhat-Dhumghat 18 km as very high risk (82 crashes/42 deaths in a year)", "")
add("N1", "Padua Bazar U-turn", "Cumilla Sadar Dakshin", "Cumilla", *point_at_km(POLY["N1"], 95.0), "estimated along corridor: Paduar Bazar ~10 km S of Cumilla Cantonment on routed N1", 2025, "20 deaths Jan-Aug 2025 (Highway Police)",
    "https://unb.com.bd/category/Special/road-safety-still-elusive-in-cumilla-141-killed-in-8-months/167345")
add("N1", "Nimsar Bazar U-turn", "Burichong", "Cumilla", *point_at_km(POLY["N1"], 76.0), "estimated along corridor: Nimsar between Chandina and Cumilla Cantonment", 2026, "recurring fatal crash site (Moynamoti Highway Police)",
    "https://bdnews24.com/bangladesh/dab79ceced09")
add("N1", "Katherpul, Chandina", "Chandina", "Cumilla", 23.483, 91.0083, W + " (Chandina Upazila)", 2026, "", "https://bdnews24.com/bangladesh/dab79ceced09")
add("N1", "Kanra, Daudkandi", "Daudkandi", "Cumilla", 23.533, 90.717, W + " (Daudkandi Upazila)", 2026, "", "https://bdnews24.com/bangladesh/dab79ceced09")
add("N1", "Miah Bazar", "Chauddagram", "Cumilla", *point_at_km(POLY["N1"], 108.0), "estimated along corridor: Miabazar between Padua Bazar and Chauddagram", 2026, "", "https://bdnews24.com/bangladesh/dab79ceced09")
add("N1", "Daudkandi toll plaza - City Gate stretch (worst in Cumilla region)", "Daudkandi", "Cumilla", 23.5316, 90.7176, "routed N1 waypoint at Daudkandi (wikipedia seed)", 2025, "465 crashes, 284 deaths Jan-Sep 2025 (Highway Police Cumilla region)",
    "https://unb.com.bd/category/Special/highway-horror-under-cumilla-region-525-killed-in-9-months/171235", "stretch, not a point")
for upa, dist, latlng, note in [("Patiya", "Chattogram", (22.300, 91.983), "RSF 2025: extremely high-risk upazila"),
                                 ("Sitakunda", "Chattogram", SIT, "RSF 2025: extremely high-risk upazila"),
                                 ("Chakaria", "Cox's Bazar", (21.7625, 92.07556), "RSF 2025: extremely high-risk upazila; Malumghat Bazar 5 brothers killed Feb 2022"),
                                 ("Brahmanpara", "Cumilla", upz("Brahmanpara", "Cumilla"), "RSF 2021: extremely accident-prone (Cumilla-Sylhet R140 area, not N1)"),
                                 ("Chauddagram", "Cumilla", (23.2283, 91.3133), "RSF 2021: accident-prone"),
                                 ("Daudkandi", "Cumilla", (23.533, 90.717), "RSF 2021: accident-prone"),
                                 ("Hajiganj", "Chandpur", upz("Hajiganj"), "RSF 2021: extremely accident-prone (Cumilla-Chandpur R140, not N1)"),
                                 ("Ukhia", "Cox's Bazar", upz("Ukhia", "Cox's Bazar"), "RSF 2021: extremely accident-prone"),
                                 ("Teknaf", "Cox's Bazar", upz("Teknaf", "Cox's Bazar"), "RSF 2021: accident-prone"),
                                 ("Satkania", "Chattogram", upz("Satkania", "Chattogram"), "RSF 2021: accident-prone")]:
    src = W + f" ({upa} Upazila)" if upa in ("Patiya", "Sitakunda", "Chakaria", "Chauddagram", "Daudkandi") else UP
    add("N1", f"{upa} upazila (RSF upazila-level listing)", upa, dist, latlng[0], latlng[1], src, 2025 if "2025" in note else 2021, note.split(":")[1].strip() if ":" in note else "",
        u2 if "2025" in note else "https://old.thefinancialexpress.com.bd/national/114-road-accident-prone-locations-identified-across-country-1619260534", note)
# Chattogram-Cox's Bazar (N1 south of Chattogram)
add("N1", "Chunati Jangalia bend", "Lohagara", "Chattogram", 21.9, 92.13333, W + " (Chunati Union)", 2025, ">90 deaths/yr in Lohagara area per locals; 15 killed in 3 crashes in 3 days Apr 2025",
    "https://en.bonikbarta.com/bangladesh/xen1AfNuqwyqCxoY/", "also https://www.dhakatribune.com/bangladesh/nation/377804/why-do-accidents-keep-occurring-on")
add("N1", "Keranihat chourasta", "Satkania", "Chattogram", 22.0981, 92.0747, "routed N1 waypoint at Keranihat (Satkania upazila seed)", 2026, "congestion/crash hotspot (Highway Police 94-point list)",
    "https://www.dhakatribune.com/bangladesh/410797/bgb-deployed-at-toll-plazas-key-routes-94")
jug = "https://www.jugantor.com/tp-city/1100071"
for name in ["Moijjarer Tek", "Patiya-Anwara crossing", "Monsar Tek", "Badamtola", "Goirarer Tek", "Nimtola Dargah", "Amjurhat", "Patiya post office", "Adalat Gate crossroad", "Thana crossroad", "Dakbanglar crossroad", "Patiya bus station", "Kamalmunshir Hat"]:
    add("N1", f"{name} (Patiya section)", "Patiya", "Chattogram", 22.300, 91.983, W + " (Patiya Upazila; individual point not located)", 2026, "one of 30 risky points Patiya-Chandanaish (50 bends on 45 km Karnaphuli bridge-Dohazari)", jug)

# ---------------------------------------------------------------- N2 Dhaka-Sylhet
dt55 = "https://www.dhakatribune.com/bangladesh/nation/307192/police-identify-55-accident-blackspots-on"
SYL = [("Tetli, Dakshin Surma", "Dakshin Surma", upz("Dakshin Surma", "Sylhet")), ("Lalabazar 'Phasir Gach'", "Dakshin Surma", upz("Dakshin Surma", "Sylhet")),
       ("Rashidpur", "Dakshin Surma", upz("Dakshin Surma", "Sylhet")), ("Nazir Bazar", "Dakshin Surma", upz("Dakshin Surma", "Sylhet")),
       ("Brahmangram-Kashertal", "Osmaninagar", upz("Balaganj", "Sylhet")), ("Goalabazar-Goynaghat", "Osmaninagar", upz("Balaganj", "Sylhet")),
       ("Burunga road mouth (19 Mile)", "Osmaninagar", upz("Balaganj", "Sylhet")), ("Niraiyar Bridge", "Osmaninagar", upz("Balaganj", "Sylhet")),
       ("Kagajpur", "Osmaninagar", upz("Balaganj", "Sylhet")), ("Begumpur Bazar", "Osmaninagar", upz("Balaganj", "Sylhet")),
       ("Fakirabad", "Osmaninagar", upz("Balaganj", "Sylhet")), ("Bhanga (Gazia)", "Osmaninagar", upz("Balaganj", "Sylhet")),
       ("Sadipur bridge - toll plaza", "Osmaninagar", upz("Balaganj", "Sylhet"))]
for name, upa, (lat, lng) in SYL:
    note = "Osmaninagar upazila not in BBS boundary file; Balaganj (parent) point used" if upa == "Osmaninagar" else ""
    if name.startswith("Nazir Bazar"):
        note = "15 construction workers killed 7 Jun 2023 (https://www.dhakatribune.com/bangladesh/313092/why-are-accidents-increasing-on-dhaka-sylhet)"
    add("N2", name, upa, "Sylhet", lat, lng, UP, 2023, "one of 55 blackspots (Highway Police Sylhet region); 112 crashes/123 deaths on N2 Sylhet section 2022", dt55, note)
tbs = "https://www.tbsnews.net/bangladesh/dhaka-sylhet-highway-turns-deathtrap-37415"
BB = [("Ashuganj roundabout (Gol Chattar)", "Ashuganj", (24.0291, 91.0048), W + " (Ashuganj Upazila)"),
      ("Bend near Titas bridge, Shahbazpur", "Sarail", (24.1183, 91.125), W + " (Sarail Upazila)"),
      ("Bhoishamora bend", "Sarail", (24.1183, 91.125), W + " (Sarail Upazila; bend not located)"),
      ("Rampura bend", "Sarail", (24.1183, 91.125), W + " (Sarail Upazila; bend not located)"),
      ("Chandura bend", "Bijoynagar", upz("Bijoynagar", "Brahmanbaria"), UP),
      ("Birpasha bend", "Bijoynagar", upz("Bijoynagar", "Brahmanbaria"), UP),
      ("Khetabari bend", "Sarail", (24.1183, 91.125), W + " (Sarail Upazila; bend not located)")]
for name, upa, (lat, lng), src in BB:
    add("N2", name, upa, "Brahmanbaria", lat, lng, src, 2020, "one of 7 riskiest bends, Ashuganj-Sarail-Bijoynagar 34 km: 137 crashes/123 deaths 2017-19 (Highway Police)", tbs)
ds = "https://www.thedailystar.net/node/37094"
for name in ["Shohagpur", "Bahadurpur", "Bertola", "Biswa Road", "Kuttapara", "Islamabad", "Bariura", "Shahbazpur", "Rampur", "Islampur"]:
    add("N2", f"{name} (Sarail stretch)", "Sarail", "Brahmanbaria", 24.1183, 91.125, W + " (Sarail Upazila; point not located)", 2014, "Highway Police listed point; 37 deaths/18 crashes in Sarail 2010-14", ds)
add("N2", "Madhabpur upazila stretch", "Madhabpur", "Habiganj", 24.1033, 91.2917, W + " (Madhabpur Upazila)", 2025, "RSF: extremely high-risk upazila (2021 and 2025)", u2)
add("N2", "Osmaninagar upazila", "Osmaninagar", "Sylhet", *upz("Balaganj", "Sylhet"), UP + "; Balaganj parent polygon", 2021, "RSF: extremely accident-prone",
    "https://old.thefinancialexpress.com.bd/national/114-road-accident-prone-locations-identified-across-country-1619260534")
add("N2", "Sarail upazila", "Sarail", "Brahmanbaria", 24.1183, 91.125, W + " (Sarail Upazila)", 2021, "RSF: extremely accident-prone", "https://old.thefinancialexpress.com.bd/national/114-road-accident-prone-locations-identified-across-country-1619260534")
add("N2", "Bhairab (Bhairab Bazar)", "Bhairab", "Kishoreganj", 24.05, 90.9875, W + " (Bhairab Bazar)", 2021, "RSF: accident-prone", "https://old.thefinancialexpress.com.bd/national/114-road-accident-prone-locations-identified-across-country-1619260534")
add("N2", "Itakhola bus stand", "Shibpur", "Narsingdi", 23.9942, 90.7601, "routed N2 waypoint (Shibpur upazila seed)", 2026, "Highway Police 94-point list (congestion); repeated fatal crashes 2018",
    "https://www.dhakatribune.com/bangladesh/410797/bgb-deployed-at-toll-plazas-key-routes-94", "km 42.65 per Wikipedia N2 table")

# ---------------------------------------------------------------- N4 / N405 Joydebpur-Tangail-Jamuna bridge (Goswami & Morshed 2016; KUET paper, 2009-2014 police data)
bip = "https://bip.org.bd/admin/uploads/member-publication/2016/201708211853221.pdf"
# paper chainage: Chandra 16.7, Elenga 69.9; routed N4: Chandra 21.1, Elenga 82.0
anch = [(16.7, 21.1), (69.9, 68.9)]
N4 = [("Chandra", 16.7, "Kaliakair", "Gazipur", 4, "3 fatal"), ("Saheb Bazar", 21.3, "Kaliakair", "Gazipur", 4, "4 fatal"),
      ("Boardghar Bazar", 24.3, "Mirzapur", "Tangail", 4, "2 fatal"), ("Gorai", 27.1, "Mirzapur", "Tangail", 5, "5 fatal"),
      ("Dholla bus stop", 40.5, "Mirzapur", "Tangail", 4, "3 fatal"), ("Natiapara Bazar", 46.9, "Tangail Sadar", "Tangail", 5, "5 fatal"),
      ("Gollah Four Brothers petrol pump", 51.1, "Tangail Sadar", "Tangail", 3, ""), ("Elenga bus stop", 69.9, "Kalihati", "Tangail", 4, "4 fatal"),
      ("Echapur / Mymensingh link road", 70.5, "Kalihati", "Tangail", 4, "3 fatal"), ("Rajbari", 71.1, "Kalihati", "Tangail", 3, "")]
for name, km, upa, dist, n, fat in N4:
    if name == "Gorai": lat, lng, src = 24.099361, 90.159205, W + " (Gorai Union)"
    elif name == "Chandra": lat, lng, src = 24.075, 90.217, W + " (Kaliakair Upazila)"
    elif name.startswith("Elenga"): lat, lng, src = 24.33861, 89.92194, W + " (Elenga)"
    else:
        lat, lng = chain("N4", km, anch); src = "km post interpolated on routed N4 polyline (calibrated Chandra 16.7->21.1, Elenga 69.9->68.9)"
    add("N4", name, upa, dist, lat, lng, src, 2016, f"{n} crashes 2009-14 in 200 m ({fat})", bip, "Goswami & Morshed 2016, Joydebpur-Jamuna Bridge approach highway (RHD N4/N405)", km)
# N405 segment beyond Elenga (chainage continues; routed N405 starts at Elenga = 0)
for name, km, n in [("Chorbabla BBA 4 No. bridge", 72.7, 5), ("North side of Analiabari", 75.5, 3), ("Ibrahimabad rail station (in front)", 82.9, 4), ("SW side of Bangabandhu Bridge East rail station", 83.1, 3)]:
    rk = (km - 69.9) * (15.9 / 13.2)  # paper Elenga 69.9 -> bridge end ~83.1 (13.2 km) vs routed N405 0 -> 15.9
    lat, lng = point_at_km(POLY["N405"], rk)
    add("N405", name, "Kalihati / Bhuapur", "Tangail", lat, lng, "km post interpolated on routed N405 polyline (Elenga 69.9 -> 0, bridge east end 83.1 -> 15.9)", 2016, f"{n} crashes 2009-14 in 200 m", bip, "", km)
add("N4", "Kalihati upazila (incl. Elenga, Bangabandhu bridge east approach)", "Kalihati", "Tangail", 24.33861, 89.92194, W + " (Elenga)", 2025, "RSF: extremely high-risk upazila (2021 and 2025)", u2)
add("N4", "Mirzapur upazila", "Mirzapur", "Tangail", *upz("Mirzapur", "Tangail"), UP, 2021, "RSF: extremely accident-prone", "https://old.thefinancialexpress.com.bd/national/114-road-accident-prone-locations-identified-across-country-1619260534")
add("N4", "Chandra area, Kaliakair", "Kaliakair", "Gazipur", 24.075, 90.217, W + " (Kaliakair Upazila)", 2025, "RSF: extremely high-risk (random boarding, reckless overtaking)", u2)
add("N4", "Bhuapur", "Bhuapur", "Tangail", *upz("Bhuapur", "Tangail"), UP, 2021, "RSF: accident-prone", "https://old.thefinancialexpress.com.bd/national/114-road-accident-prone-locations-identified-across-country-1619260534")

# ---------------------------------------------------------------- N5 Dhaka-Aricha / Hatikumrul-Bogura-Rangpur / Rangpur-Banglabandha
dtr = "https://www.dhakatribune.com/opinion/op-ed/77165/black-spots-of-death"
add("N5", "Salehpur bridge (Turag)", "Savar", "Dhaka", *point_at_km(POLY["N5"], 11.0), "estimated along corridor: Salehpur bridge between Gabtoli and Savar on routed N5", 2010, "bus plunged into Turag; ARI-BUET built-in fault", dtr)
add("N5", "Utholi / Paturia link intersection", "Shibalaya", "Manikganj", *point_at_km(POLY["N5"], 68.0), "estimated along corridor: Uthali junction ~3 km before Paturia ghat on routed N5", 2010, "2 secretaries killed Jul 2010; ARI-BUET flagged junction", dtr)
add("N5", "Joka village curve", "Ghior", "Manikganj", 23.8875, 89.8375, W + " (Ghior Upazila)", 2011, "5 killed Aug 2011; ARI: 22 dangerous spots on Dhaka-Aricha", "https://thedailystar.net/node/827236")
add("N5", "Mulzan turn", "Ghior", "Manikganj", 23.8875, 89.8375, W + " (Ghior Upazila; turn not located)", 2011, "5 killed ~Apr 2011", "https://thedailystar.net/node/827236")
add("N5", "Dhamrai upazila stretch", "Dhamrai", "Dhaka", *upz("Dhamrai", "Dhaka"), UP, 2025, "RSF: extremely high-risk upazila (2021 and 2025)", u2)
add("N5", "Nabinagar - Paturia (11 of 209 ARI blackspots treated 2009-14)", "Savar / Manikganj", "Dhaka / Manikganj", *point_at_km(POLY["N5"], 24.0), "routed N5 waypoint at Nabinagar", 2014, "RHD: crashes 175 (2011) -> 25 (2013); 12 NH-5 blackspots in Manikganj road division",
    "https://today.thefinancialexpress.com.bd/print/black-spots-most-accident-prone-areas", "stretch; see also UNCRD slides")
fe = "https://old.thefinancialexpress.com.bd/national/114-road-accident-prone-locations-identified-across-country-1619260534"
add("N5", "Hatikumrul intersection", "Ullapara", "Sirajganj", 24.419218, 89.551712, W + " (Hatikumrul Union)", 2021, "RSF: extremely accident-prone", fe)
add("N5", "Ullapara upazila", "Ullapara", "Sirajganj", *upz("Ullahpara", "Sirajgonj"), UP, 2021, "RSF: extremely accident-prone", fe)
add("N5", "Shahjadpur upazila", "Shahjadpur", "Sirajganj", *upz("Shahjadpur", "Sirajgonj"), UP, 2021, "RSF: accident-prone", fe)
add("N5", "Bangabandhu Bridge west approach (Sayedabad-Hatikumrul)", "Sirajganj Sadar", "Sirajganj", *upz("Sirajganj Sadar", "Sirajgonj"), UP, 2021, "RSF: extremely accident-prone", fe, "N507 link to N5")
add("N5", "Sherpur upazila stretch Dashmail-Shimabari (21 km) / Sherpur Upazila Parishad front", "Sherpur", "Bogura", 24.63, 89.4364, "routed N5 waypoint at Sherpur (BBS upazila seed)", 2025, "RSF: extremely high-risk (2021 and 2025)", u2)
add("N5", "Amtala, Sherpur", "Sherpur", "Bogura", 24.63, 89.4364, "routed N5 waypoint at Sherpur (point not located)", 2022, "5 killed Jan 2022", "https://www.banglanews24.com/english/national/news/bd/93272.details")
add("N5", "Chandaikona Bazar", "Raiganj", "Sirajganj", *point_at_km(POLY["N5"], 170.0), "estimated along corridor: Chandaikona between Hatikumrul and Sherpur", 2026, "Highway Police 94-point list", "https://www.dhakatribune.com/bangladesh/410797/bgb-deployed-at-toll-plazas-key-routes-94")
add("N5", "Mokamtala", "Shibganj", "Bogura", *upz("Shibganj", "Bogura"), UP, 2021, "RSF: Shibganj accident-prone", fe)
add("N5", "Shibganj (Bogura) upazila", "Shibganj", "Bogura", *upz("Shibganj", "Bogura"), UP, 2021, "RSF: accident-prone", fe)
# Gaibandha 13 bends (Gaibandha RHD; ARI-BUET 7 most vulnerable) - Daily Star 2018
gb = "https://www.thedailystar.net/country/news/road-accidents-kill-112-five-years-1672255"
GOB = (25.133, 89.3917); PAL = (25.283, 89.350)
for name in ["Fasitola", "Bakchar", "Boalia", "Kalitola", "Chapriganj", "Katakhali", "Komarpur", "Noondaha"]:
    add("N5", f"{name} bend", "Gobindaganj", "Gaibandha", *GOB, W + " (Gobindaganj Upazila; bend not located)", 2018, "one of 13 RHD-marked turning points; ARI-BUET 7 most vulnerable; 112 killed 2014-18 district-wide", gb)
for name in ["Nuniyagari", "Dakghar", "Giridharipur", "Brac More"]:
    add("N5", f"{name} bend", "Palashbari", "Gaibandha", *PAL, W + " (Palashbari Upazila; bend not located)", 2018, "one of 13 RHD-marked turning points", gb)
add("N5", "Dhaperhat bend", "Sadullapur", "Gaibandha", *upz("Sadullapur", "Gaibandha"), UP, 2018, "one of 13 RHD-marked turning points", gb)
add("N5", "Gobindaganj (Mayamoni Mor)", "Gobindaganj", "Gaibandha", *GOB, W + " (Gobindaganj Upazila)", 2021, "RSF: extremely accident-prone", fe)
add("N5", "Palashbari town", "Palashbari", "Gaibandha", *PAL, W + " (Palashbari Upazila)", 2021, "RSF: extremely accident-prone", fe)
# Rangpur-Panchagarh 140 km, 19 black spots (RHD project, Daily Star)
rp = "https://online91.thedailystar.net/country/news/work-reduce-risk-accident-19-black-spots-136273"
RNG = [("Rangpur Medical College intersection", "Rangpur Sadar", "Rangpur", 25.7602, 89.2315, "routed N5 waypoint Rangpur (Modern Mor); RMC is on N5 W of city"),
       ("Modern turning (Modern Mor)", "Rangpur Sadar", "Rangpur", 25.7602, 89.2315, "routed N5 waypoint at Rangpur Modern Mor (district HQ seed)"),
       ("Domdoma", "Rangpur Sadar", "Rangpur", None, None, UP), ("Gorer Math", "Rangpur Sadar", "Rangpur", None, None, UP),
       ("Shothibari (Shathibari) bazar", "Mithapukur", "Rangpur", 25.5691, 89.2744, "routed N5 waypoint at Mithapukur/Shathibari"),
       ("Borodarga", "Mithapukur", "Rangpur", None, None, UP), ("Laldighi", "Mithapukur", "Rangpur", None, None, UP),
       ("Pirganj market", "Pirganj", "Rangpur", None, None, UP),
       ("Ikorchali market", "Taraganj", "Rangpur", None, None, UP), ("Taraganj market", "Taraganj", "Rangpur", 25.8112, 89.0139, "routed N5 waypoint at Taraganj"),
       ("Chikli market", "Taraganj", "Rangpur", None, None, UP),
       ("Dry fish market turning (Sutkir Mor), Saidpur bus terminal", "Saidpur", "Nilphamari", 25.77806, 88.8975, W + " (Saidpur)"),
       ("Kamarpukur bazar", "Saidpur", "Nilphamari", None, None, UP)]
for name, upa, dist, lat, lng, src in RNG:
    if lat is None:
        lat, lng = upz(upa, dist)
    add("N5", name, upa, dist, lat, lng, src, 2019, "one of 19 RHD black spots Rangpur-Panchagarh 140 km; >100 deaths in a year (Tk25 cr treatment)", rp,
        "Saidpur/Kamarpukur also in UNCRD 2016 RHD blackspot treatment slides (144 selected of 209)")
add("N5", "Dandogaon 29 Mile bus stand", "Pirganj", "Thakurgaon", *upz("Pirganj", "Thakurgaon"), UP, 2016, "RHD blackspot treatment project (Thakurgaon road division)", "https://uncrd.un.org/sites/uncrd.un.org/files/9th-est_bangladesh-black-spot-treatment.pdf")
for upa, dist, note in [("Taraganj", "Rangpur", "RSF 2021: extremely accident-prone"), ("Pirganj", "Rangpur", "RSF 2021: extremely accident-prone"),
                        ("Kishoreganj", "Nilphamari", "RSF 2021: extremely accident-prone"), ("Birganj", "Dinajpur", "RSF 2021: extremely accident-prone"), ("Badarganj", "Rangpur", "RSF 2021: accident-prone")]:
    add("N5", f"{upa} upazila", upa, dist, *upz(upa, dist), UP, 2021, note.split(":")[1].strip(), fe, note)

# ---------------------------------------------------------------- N6 Rajshahi corridor (RSF upazilas)
for upa, dist, note in [("Puthia", "Rajshahi", "RSF 2021: extremely accident-prone"), ("Baraigram", "Natore", "RSF 2025: extremely high-risk (2021 too); Banpara junction N6/N507"),
                        ("Ishwardi", "Pabna", "RSF 2025: extremely high-risk (2021 too); Dasuria junction N6/N704"), ("Lalpur", "Natore", "RSF 2021: accident-prone"),
                        ("Santhia", "Pabna", "RSF 2021: extremely accident-prone (N5/N6 Kashinathpur area)"), ("Chatmohar", "Pabna", "RSF 2021: accident-prone")]:
    add("N6", f"{upa} upazila", upa, dist, *upz(upa, dist), UP, 2025 if "2025" in note else 2021, note.split(":")[1].strip(), u2 if "2025" in note else fe, note)

# ---------------------------------------------------------------- N7 Dhaka-Khulna (Daulatdia-Khulna)
add("N7", "Majhkandi, Madhukhali", "Madhukhali", "Faridpur", 23.5417, 89.63, W + " (Madhukhali Upazila)", 2021, "9 killed 21 Mar 2021; 30 deaths in 13 months on Faridpur Sadar-Kamarkhali bridge 35 km", "https://unb.com.bd/category/Special/dhaka-khulna-highway-turns-death-trap/66807")
for upa, dist, note in [("Madhukhali", "Faridpur", "RSF 2021: accident-prone"), ("Abhaynagar", "Jashore", "RSF 2021: extremely accident-prone"),
                        ("Kaliganj", "Jhenaidah", "RSF 2021: extremely accident-prone"), ("Phultala", "Khulna", "RSF 2021: accident-prone"),
                        ("Mohammadpur", "Magura", "RSF 2021: accident-prone"), ("Damurhuda", "Chuadanga", "RSF 2025: extremely high-risk (2021 too); Chuadanga-Jhenaidah N704, not N7")]:
    lat, lng = (23.5417, 89.63) if upa == "Madhukhali" else upz(upa, dist)
    add("N7", f"{upa} upazila", upa, dist, lat, lng, W + " (Madhukhali Upazila)" if upa == "Madhukhali" else UP, 2025 if "2025" in note else 2021, note.split(":")[1].strip(), u2 if "2025" in note else fe, note)

# ---------------------------------------------------------------- N8 Dhaka-Mawa-Bhanga-Barishal (ARI-style HRL/blackspot paper, 2007-2012 data)
n8p = "https://www.slideshare.net/slideshow/characterizing-hazardous-road-locations-and-black-spots-on-route-n8-dhakabarisal-national-highway-of-bangladesh/77448123"
# paper chainage: Takerhat bridge 184.5 (routed 93.8 at Tekerhat), Barisal jute mill 266.2 (~ routed 160; Barishal waypoint 165.2). Old alignment via Mawa ferry/Bhanga; paper km 0 at Postogola?
# calibrate on Tekerhat (184.5->93.8) and Barishal (266.2->160.0): slope 0.81 -> paper chainage includes Mawa-Kawrakandi ferry + old road; treat with caution.
anch8 = [(184.5, 93.8), (266.2, 160.0)]
N8 = [("Equria Bazar / bus stand", 7.2, "Keraniganj", "Dhaka", "HRL", 5), ("Abdullahpur Bazar / bus stand", 13.95, "Keraniganj", "Dhaka", "black spot", 4),
      ("Arial Khan bridge (E)", 50.85, "Shibchar", "Madaripur", "black spot", 3), ("Solindia bridge", 57.65, "Shibchar", "Madaripur", "black spot", 3),
      ("Maligram bus stand / high school", 59.3, "Bhanga", "Faridpur", "HRL", 12), ("Takerhat bridge / Gopalganj (L) intersection", 184.9, "Rajoir", "Madaripur", "HRL", 5),
      ("Mostafapur bus stand", 199.7, "Madaripur Sadar", "Madaripur", "HRL", 6), ("Illah bus stand", 214.95, "Kalkini", "Madaripur", "black spot", 4),
      ("Jorchuri bus stand", 236.9, "Gaurnadi", "Barishal", "HRL", 4), ("Barisal Jute Mill (R)", 266.5, "Barisal Sadar", "Barishal", "black spot", 3),
      ("Boalia Bazar / Bailey bridge", 271.6, "Barisal Sadar", "Barishal", "HRL", 4), ("Bharpasha Bottola bus stand", 278.55, "Bakerganj", "Barishal", "black spot", 3),
      ("Laxmipasha primary school / Bharpasha Bazar", 280.25, "Bakerganj", "Barishal", "HRL", 4), ("Badarpur bus stand / bazar", 289.65, "Bakerganj", "Barishal", "black spot", 4)]
for name, km, upa, dist, typ, n in N8:
    if km < 60:   # Dhaka-Mawa / old Kawrakandi-Bhanga segment: chainage pre-dates Padma bridge; locate by upazila
        lat, lng = upz(upa, dist) if upa != "Bhanga" else (23.383, 89.983); src = UP + " (paper chainage predates Padma bridge alignment)" if upa != "Bhanga" else W + " (Bhanga Upazila)"
    elif km > 200:
        lat, lng = chain("N8", km, anch8); src = "km post interpolated on routed N8 polyline (calibrated Takerhat 184.5->93.8, Barishal 266.2->160.0; old-alignment chainage, +/- several km)"
    else:
        lat, lng = chain("N8", km, anch8); src = "km post interpolated on routed N8 polyline (calibrated; +/- several km)"
    add("N8", name, upa, dist, lat, lng, src, 2017, f"{typ}: {n} crashes 2007-12", n8p, "Journal of Built Environment, Technology and Engineering 2017 (ARI-type HRL/blackspot analysis of RHD N8)", km)
add("N8", "Kutubpur, Shibchar (expressway; 19 killed 19 Mar 2023)", "Shibchar", "Madaripur", 23.35, 90.1667, W + " (Shibchar Upazila)", 2024, "Dhaka-Mawa-Bhanga expressway: 135 crashes/131 deaths Mar 2023-Feb 2024 (Highway Police)", "https://en.prothomalo.com/bangladesh/7in6m5obxw")
add("N8", "Maligram flyover area, Bhanga (ambulance crash, 8 killed Jun 2023)", "Bhanga", "Faridpur", 23.383, 89.983, W + " (Bhanga Upazila)", 2024, "", "https://en.prothomalo.com/bangladesh/7in6m5obxw")
add("N8", "Bhanga Gol Chattar (N8/N804/N805 interchange)", "Bhanga", "Faridpur", 23.383, 89.983, W + " (Bhanga Upazila)", 2025, "RSF: extremely high-risk upazila (2021 and 2025); JES 2024 paper H1: 41 crashes/14 fatal 2018-22 at km 72-72.6", u2)
add("N8", "Tekerhat", "Rajoir", "Madaripur", 23.205, 90.0361, "routed N8 waypoint at Tekerhat (Rajoir upazila seed)", 2025, "RSF: extremely high-risk (2021 and 2025)", u2)
add("N8", "Shibchar upazila", "Shibchar", "Madaripur", 23.35, 90.1667, W + " (Shibchar Upazila)", 2025, "RSF: extremely high-risk", u2)
add("N8", "Gournadi upazila", "Gaurnadi", "Barishal", 22.9736, 90.2306, W + " (Gaurnadi Upazila)", 2025, "RSF: extremely high-risk (2021 and 2025)", u2)
for upa, dist, note in [("Kalkini", "Madaripur", "RSF 2021: extremely accident-prone"), ("Agailjhara", "Barishal", "RSF 2021: extremely accident-prone"),
                        ("Babuganj", "Barishal", "RSF 2021: accident-prone"), ("Bakerganj", "Barishal", "RSF 2021: accident-prone"), ("Sreenagar", "Munshiganj", "RSF 2021: 'Asian Expressway (Munshiganj)' extremely accident-prone")]:
    add("N8", f"{upa} upazila", upa, dist, *upz(upa, dist), UP, 2021, note.split(":")[1].strip(), fe, note)

# ---------------------------------------------------------------- N805 Bhanga-Gopalganj-Khulna (JES 2024, 2018-2022 data; paper calls it N8 Dhaka-Khulna)
jes = "https://banglajol.info/index.php/JES/article/view/82168/53670"
# paper km: Bhanga Gol Chottor 72.0 (routed N805 0), Mollahat bus stop 152.2 (routed 84.6) -> calibrate
anch805 = [(72.0, 0.0), (152.2, 84.6)]
JES = [("Bhanga Gol Chottor", 72.3, "Bhanga", "Faridpur", 41, 14), ("Bogail bus stop", 69.85, "Bhanga", "Faridpur", 10, 4),
       ("Algadia bridge", 83.75, "Muksudpur", "Gopalganj", 5, 4), ("Gazaria Bazar", 86.25, "Muksudpur", "Gopalganj", 7, 5),
       ("Muksudpur College More bus stand", 90.3, "Muksudpur", "Gopalganj", 11, 7), ("Muksudpur filling station", 90.8, "Muksudpur", "Gopalganj", 6, 1),
       ("Rishatola bus stand", 91.35, "Muksudpur", "Gopalganj", 8, 1), ("Gerakhola bus stand", 96.75, "Muksudpur", "Gopalganj", 5, 2),
       ("Pona bus stop", 107.4, "Kashiani", "Gopalganj", 5, 3), ("Bhatiapara Ural Setu (flyover)", 109.35, "Kashiani", "Gopalganj", 3, 3),
       ("Rakhi LPG filling station", 114.25, "Kashiani", "Gopalganj", 5, 1), ("Tilsara Bazar", 117.65, "Kashiani", "Gopalganj", 8, 3),
       ("Gopalpur Bazar", 118.55, "Gopalganj Sadar", "Gopalganj", 7, 1), ("Fukra launch ghat road", 121.2, "Kashiani / Gopalganj Sadar", "Gopalganj", 5, 1),
       ("Fukra bus stand", 121.5, "Kashiani / Gopalganj Sadar", "Gopalganj", 5, 1), ("Sharif Para bus station", 126.25, "Gopalganj Sadar", "Gopalganj", 11, 3),
       ("Dumdia Nimtola", 136.45, "Gopalganj Sadar", "Gopalganj", 10, 3), ("Haridaspur bridge", 137.8, "Gopalganj Sadar", "Gopalganj", 5, 3),
       ("Char Pathalia, Dola filling station", 147.75, "Mollahat", "Bagerhat", 9, 6), ("Ghonapara Bazar / bus stand", 149.3, "Mollahat", "Bagerhat", 6, 3),
       ("Mollahat bus stop", 152.3, "Mollahat", "Bagerhat", 3, 3)]
JES.insert(2, ("Sreenagar filling station road (Dhaka-Mawa segment)", 25.75, "Sreenagar", "Munshiganj", 6, 5))
for name, km, upa, dist, n, fat in JES:
    if km < 60:
        lat, lng = upz("Sreenagar", "Munshiganj"); src = UP + " (paper km 25.5 on Dhaka-Mawa expressway)"; hw = "N8"
    else:
        lat, lng = chain("N805", km, anch805); src = "km post interpolated on routed N805 polyline (calibrated Bhanga 72.0->0, Mollahat 152.2->84.6)"; hw = "N805"
    add(hw, name, upa, dist, lat, lng, src, 2024, f"{n} crashes / {fat} fatal 2018-22 (rank by crashes)", jes, "JES (KUET) 2024: 'Dhaka-Khulna national highway' = N8 Dhaka-Bhanga + N805 Bhanga-Khulna", km)
for upa, dist, note in [("Muksudpur", "Gopalganj", "RSF 2021: extremely accident-prone"), ("Kotalipara", "Gopalganj", "RSF 2021: accident-prone (off N805)")]:
    add("N805", f"{upa} upazila", upa, dist, *upz(upa, dist), UP, 2021, note.split(":")[1].strip(), fe, note)

# ---------------------------------------------------------------- N3 Dhaka-Mymensingh
add("N3", "Trishal upazila stretch (~20 km)", "Trishal", "Mymensingh", 24.575, 90.3917, W + " (Trishal Upazila)", 2024, "47 crashes/54 deaths 2023; RSF 2025 extremely high-risk", "https://thefinancialexpress.com.bd/national/country/trishal-a-notorious-accident-black-spot")
add("N3", "Bhaluka upazila stretch (Bhaluka bus stand, Square Masterbari, Seed Store, Bharadoba)", "Bhaluka", "Mymensingh", 24.375, 90.3783, W + " (Bhaluka Upazila)", 2025, "RSF: extremely high-risk (2021 and 2025)", u2)
for upa, dist, note in [("Sreepur", "Gazipur", "RSF 2025: extremely high-risk (Mawna chowrasta / MC Bazar / Jaina Bazar)"), ("Gazipur Sadar", "Gazipur", "RSF 2025: extremely high-risk (Chowrasta / Bhabanipur Bazar)"),
                        ("Phulpur", "Mymensingh", "RSF 2021: extremely accident-prone (N3 north extension to Haluaghat)"), ("Tarakanda", "Mymensingh", "RSF 2021: extremely accident-prone"),
                        ("Gaffargaon", "Mymensingh", "RSF 2021: accident-prone (off N3)"), ("Nandail", "Mymensingh", "RSF 2021: accident-prone (off N3)")]:
    if upa == "Sreepur": lat, lng = 24.17637, 90.4898; src = "BBS upazila polygon (Sreepur, Gazipur)"
    elif upa == "Tarakanda": lat, lng = upz("Phulpur", "Mymensingh"); src = UP + "; Tarakanda not in BBS file, Phulpur parent used"
    else: lat, lng = upz(upa, dist); src = UP
    add("N3", f"{upa} upazila", upa, dist, lat, lng, src, 2025 if "2025" in note else 2021, note.split(":")[1].strip(), u2 if "2025" in note else fe, note)

if __name__ == "__main__":
    with open("/home/claude/work/data/raw/blackspots.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    import collections
    print(len(rows), "rows"); print(collections.Counter(r["highway"] for r in rows))
    print(collections.Counter(r["lat_lng_source"].split("(")[0].split(":")[0].strip() for r in rows))
    for r in rows:
        assert 20.5 < r["lat"] < 26.7 and 88.0 < r["lng"] < 92.7, r
