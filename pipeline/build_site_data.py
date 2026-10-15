"""Build the JSON files the site reads from the raw CSVs. Run from the repo root: python pipeline/build_site_data.py"""
import json, math, re, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data"
OUT.mkdir(parents=True, exist_ok=True)

def clean(v):
    if v is None or (isinstance(v, float) and math.isnan(v)): return None
    return v

def rows(df):
    return [{k: clean(v) for k, v in r.items()} for r in df.to_dict("records")]

# ---------- 1. national yearly ----------
nat = pd.read_csv(RAW / "national_yearly.csv")
pop = pd.read_csv(RAW / "population_national.csv").set_index("year")["population"]
# compute deaths per 100k where a source gives deaths but no rate (WHO rows keep their own published rate)
def rate(r):
    if pd.notna(r["deaths_per_100k"]): return float(r["deaths_per_100k"])
    if pd.notna(r["deaths"]) and r["year"] in pop.index: return round(float(r["deaths"]) / pop[r["year"]] * 1e5, 2)
    return None
nat["deaths_per_100k"] = nat.apply(rate, axis=1)
# short source labels used by the site
SHORT = {
    "Police/ARI-BUET (MAAP)": "Police/BRTA",
    "BRTA": "Police/BRTA",            # BRTA's own compilation of police cases, 2023-25
    "RHD (Mahmud et al 2013)": "RHD compilation",
    "BJKS": "BJKS", "RSF": "RSF", "NISCHA": "Nirapad Sarak Chai", "NCPSRR": "NCPSRR",
    "WHO GSRRS (modelled)": "WHO estimate",
    "WHO/World Bank SH.STA.TRAF.P5 (modelled rate)": "WHO/WB modelled rate",
    "BHIS (household survey)": "BHIS", "NHIS 2022-23 (household survey)": "BHIS",
}
nat["source_full"] = nat["source"]
nat["source"] = nat["source"].map(SHORT).fillna(nat["source"])
# police + BRTA overlap check: keep both rows if they conflict in the same year
dup = nat[nat.duplicated(["year", "source"], keep=False)]
if len(dup):
    print("WARN duplicate year/source rows:", dup[["year", "source", "deaths", "source_full"]].to_string())
    nat = nat.sort_values(["year", "source", "source_full"]).drop_duplicates(["year", "source"], keep="first")
nat = nat[nat.year >= 2000].sort_values(["source", "year"])
json.dump(rows(nat[["year", "source", "source_full", "accidents", "deaths", "injuries", "deaths_per_100k", "note", "citation_url"]]),
          open(OUT / "national.json", "w"), ensure_ascii=False)
print("national.json", len(nat), "rows; sources:", nat.source.unique().tolist())

# ---------- 2. corridors + blackspots ----------
poly = json.load(open(RAW / "roads" / "corridor_polylines.json"))
cor = pd.read_csv(RAW / "corridors.csv")
NAMES = {"N1": "Dhaka – Chattogram – Cox's Bazar – Teknaf", "N2": "Dhaka – Sylhet – Tamabil", "N3": "Dhaka – Mymensingh",
         "N4": "Dhaka – Tangail – Bangabandhu Bridge", "N405": "Elenga – Bangabandhu Bridge east approach", "N5": "Dhaka – Bogura – Rangpur – Banglabandha",
         "N6": "Dhaka – Natore – Rajshahi – Sona Masjid", "N7": "Daulatdia – Jashore – Khulna – Mongla", "N8": "Dhaka – Padma Bridge – Barishal", "N805": "Bhanga – Gopalganj – Mollahat (Dhaka–Khulna)"}
def hav(a, b):
    R = 6371000; la1, la2 = math.radians(a[1]), math.radians(b[1]); d1 = la2 - la1; d2 = math.radians(b[0] - a[0])
    s = math.sin(d1/2)**2 + math.cos(la1)*math.cos(la2)*math.sin(d2/2)**2; return 2*R*math.asin(math.sqrt(s))
corridors = {}
for ref, coords in poly.items():
    m = [0.0]
    for i in range(1, len(coords)): m.append(m[-1] + hav(coords[i-1], coords[i]))
    w = cor[cor.corridor == ref].sort_values("seq")
    corridors[ref] = {"ref": ref, "name": NAMES.get(ref, ref), "coords": [[round(x, 5), round(y, 5)] for x, y in coords], "total_m": round(m[-1]),
                      "official_route": clean(w.official_route.iloc[0]) if len(w) else None,
                      "wiki_length_km": clean(float(w.total_length_km.iloc[0])) if len(w) else None,
                      "waypoints": [{"place": r.place, "district": r.district, "km": float(r.km_from_start), "lng": float(r.lng), "lat": float(r.lat)} for r in w.itertuples()]}
json.dump(corridors, open(OUT / "corridors.json", "w"), ensure_ascii=False)
print("corridors.json", {k: (round(v["total_m"]/1000), len(v["coords"])) for k, v in corridors.items()})

bs = pd.read_csv(RAW / "blackspots.csv")
def precision(s):
    s = str(s).lower()
    if "upazila representative" in s or "point not located" in s or "bend not located" in s or "individual point not located" in s or "upazila polygon" in s: return "upazila"
    return "point"
bs["precision"] = bs.lat_lng_source.map(precision)
# route-metre of every spot on its corridor (nearest point on polyline)
def project(ref, p):
    coords = corridors[ref]["coords"]; best = (None, 1e18); m = 0.0
    kx = 111320*math.cos(math.radians(p[1])); ky = 111320
    for i in range(1, len(coords)):
        a, b = coords[i-1], coords[i]; L = hav(a, b)
        ax, ay = (a[0]-p[0])*kx, (a[1]-p[1])*ky; bx, by = (b[0]-p[0])*kx, (b[1]-p[1])*ky
        dx, dy = bx-ax, by-ay; LL = dx*dx+dy*dy; t = 0 if LL == 0 else max(0, min(1, -(ax*dx+ay*dy)/LL))
        d = math.hypot(ax+dx*t, ay+dy*t)
        if d < best[1]: best = (m + L*t, d)
        m += L
    return best
recs = []
for r in bs.itertuples():
    if r.highway not in corridors: continue
    m, d = project(r.highway, [float(r.lng), float(r.lat)])
    recs.append({"highway": r.highway, "place": r.name_place, "upazila": clean(r.upazila), "district": clean(r.district), "lat": float(r.lat), "lng": float(r.lng),
                 "route_m": round(m), "off_m": round(d), "precision": r.precision, "year": clean(int(r.year_listed)) if pd.notna(r.year_listed) else None,
                 "rank": clean(r.severity_or_rank), "source_url": clean(r.source_url), "note": clean(r.note), "located_by": clean(r.lat_lng_source)})
far = [x for x in recs if x["off_m"] > 8000]
print("blackspots.json", len(recs), "rows;", len(far), "more than 8 km off their corridor (kept, flagged)")
for x in far: x["flag"] = "far_from_corridor"
json.dump(recs, open(OUT / "blackspots.json", "w"), ensure_ascii=False)

# highway context layer: N and R roads, light simplification, split by class
g = json.load(open(RAW / "roads" / "bd-major-routes.geojson"))
feats = []
for f in g["features"]:
    ref = (f["properties"].get("ref") or "").strip()
    if not re.match(r"^[NR]\d+", ref): continue
    cls = "national" if ref.startswith("N") else "regional"
    c = [[round(x, 4), round(y, 4)] for x, y in f["geometry"]["coordinates"]]
    if len(c) < 2: continue
    feats.append({"type": "Feature", "properties": {"ref": ref.split(";")[0], "cls": cls}, "geometry": {"type": "LineString", "coordinates": c}})
json.dump({"type": "FeatureCollection", "features": feats}, open(OUT / "highways.geojson", "w"), separators=(",", ":"))
print("highways.geojson", len(feats), "features")

# ---------- 3. population + network ----------
pa = pd.read_csv(RAW / "population_admin.csv")
json.dump(rows(pa[["level", "name", "division", "pop_2011", "pop_2022", "area_km2"]]), open(OUT / "population_admin.json", "w"), ensure_ascii=False)
json.dump(rows(pd.read_csv(RAW / "population_national.csv")[["year", "population"]]), open(OUT / "population_national.json", "w"))
print("done; now run build_sections.py")
