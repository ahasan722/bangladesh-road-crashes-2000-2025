"""Second pipeline step: derive section-ready JSON (where, who, when, roads) from breakdowns.csv and monthly.csv.
Every derived number carries the list of periods it was computed from, so the page can say exactly what it is showing."""
import json, math, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"; OUT = ROOT / "data"
b = pd.read_csv(RAW / "breakdowns.csv")
mo = pd.read_csv(RAW / "monthly.csv")
mo = mo[mo.year.astype(str).str.isdigit()].copy(); mo["year"] = mo.year.astype(int); mo["month"] = mo.month.astype(int)
b["value"] = pd.to_numeric(b["value"], errors="coerce")
DIVS = ["Dhaka", "Chattogram", "Rajshahi", "Khulna", "Barishal", "Sylhet", "Rangpur", "Mymensingh"]
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def period_label(p):
    m = re.match(r"^(\d{4})-(\d{2})$", str(p))
    if m: return f"{MONTHS[int(m.group(2))-1]} {m.group(1)}"
    m = re.match(r"^eid_(fitr|azha)_(\d{4})$", str(p))
    if m: return f"Eid-ul-{'Fitr' if m.group(1)=='fitr' else 'Azha'} {m.group(2)}"
    m = re.match(r"^(\d{4})-(\d{2})_to_(\d{4})-(\d{2})$", str(p))
    if m: return f"{MONTHS[int(m.group(2))-1]} {m.group(1)} to {MONTHS[int(m.group(4))-1]} {m.group(3)}"
    return str(p).replace("_", " ")

def cite(df):
    return sorted(set(df.citation_url.dropna()))

# ---------------- WHERE: division shares ----------------
d = b[(b.dimension == "division") & (b.source == "RSF")]
periods = []
for p, g in d.groupby("period"):
    sh = g[g.measure == "share_pct"].copy()
    sh["is_death"] = sh.note.fillna("").str.lower().str.contains("death")
    # prefer accident shares; if a period only has death shares use those
    pref = sh[~sh.is_death] if (~sh.is_death).sum() >= 7 else sh[sh.is_death]
    pref = pref.drop_duplicates(["category"], keep="first")
    shares = {r.category: float(r.value) for r in pref.itertuples() if r.category in DIVS}
    if len(shares) < 7 or not (85 <= sum(shares.values()) <= 115): continue
    basis_from_shares = "deaths" if (len(pref) and pref.is_death.iloc[0]) else "accidents"
    tot = b[(b.source == "RSF") & (b.period == p) & (b.dimension == "total") & (b.category == "all")]
    totals = {r.measure: float(r.value) for r in tot.itertuples()}
    # monthly.csv has month totals too
    m = re.match(r"^(\d{4})-(\d{2})$", str(p))
    if m:
        mm = mo[(mo.source == "RSF") & (mo.year == int(m.group(1))) & (mo.month == int(m.group(2)))]
        if len(mm):
            for k in ["accidents", "deaths", "injuries"]:
                if pd.notna(mm.iloc[0][k]): totals.setdefault(k, float(mm.iloc[0][k]))
    # the share is a share of accidents unless the note says deaths; RSF press tables are accident shares
    basis = basis_from_shares
    cnt = {r.category: float(r.value) for r in g[g.measure == basis].itertuples() if r.category in DIVS}
    periods.append({"period": p, "label": period_label(p), "shares": shares, "basis": basis, "totals": totals, "counts_published": cnt, "sources": cite(g)})
periods.sort(key=lambda x: x["period"])
# pooled: weighted by period accident total when known, else equal weight
pool = {k: 0.0 for k in DIVS}; wsum = 0.0
for pr in periods:
    w = pr["totals"].get("accidents", 1.0) if pr["basis"] == "accidents" else pr["totals"].get("deaths", 1.0)
    for k in DIVS: pool[k] += pr["shares"].get(k, 0) * w
    wsum += w
pooled = {k: round(v / wsum, 2) for k, v in pool.items()}
# annual highest/lowest rows
ann = d[(d.period == "annual")]
annual_rows = [{"year": int(r.year) if str(r.year).isdigit() else r.year, "division": r.category, "measure": r.measure, "value": float(r.value), "url": r.citation_url} for r in ann.itertuples() if r.category in DIVS]
json.dump({"divisions": DIVS, "periods": periods, "pooled": pooled, "pooled_n": len(periods), "annual_extremes": annual_rows},
          open(OUT / "where.json", "w"), ensure_ascii=False, indent=0)
print("where.json periods:", [p["period"] for p in periods])

# ---------------- WHO ----------------
rsf = b[(b.source == "RSF") & (b.period == "annual")]
def series(dim, cats, measure="deaths"):
    out = {}
    for y, g in rsf[(rsf.dimension == dim) & (rsf.measure == measure)].groupby("year"):
        if not str(y).isdigit(): continue
        row = {}
        for c in cats:
            v = g[g.category == c].value
            if len(v): row[c] = float(v.iloc[0])
        if row: out[int(y)] = row
    return out
victims = series("victim", ["women", "children", "pedestrian", "drivers_helpers", "motorcycle", "motorcycle_all", "students", "working_age_18_65"])
veh_counts = series("vehicle_type", ["motorcycle", "three_wheeler", "local_three_wheeler", "truck_pickup_goods", "bus", "car_microbus", "local_vehicle", "bicycle_rickshaw", "bus_truck_car_combined"])
veh_share = series("vehicle_type", ["motorcycle", "three_wheeler", "local_three_wheeler", "truck_pickup_goods", "bus", "car_microbus", "local_vehicle", "bicycle_rickshaw", "bus_truck_car_combined"], "share_pct")
moto_acc = series("vehicle_type", ["motorcycle"], "accidents")
totals = {int(r.year): float(r.value) for r in rsf[(rsf.dimension == "total") & (rsf.measure == "deaths")].itertuples() if str(r.year).isdigit()}
tot_acc = {int(r.year): float(r.value) for r in rsf[(rsf.dimension == "total") & (rsf.measure == "accidents")].itertuples() if str(r.year).isdigit()}
bj = b[(b.source == "BJKS") & (b.period == "annual")]
bj_moto = {int(r.year): float(r.value) for r in bj[(bj.dimension == "vehicle_type") & (bj.category == "motorcycle") & (bj.measure == "deaths")].itertuples() if str(r.year).isdigit()}
bj_victims = {}
for y, g in bj[(bj.dimension == "victim") & (bj.measure == "deaths")].groupby("year"):
    if str(y).isdigit(): bj_victims[int(y)] = {r.category: float(r.value) for r in g.itertuples()}
# collision types: pooled RSF monthly accident counts + BJKS annual shares
col = b[(b.dimension == "collision_type")]
rsf_col = col[(col.source == "RSF") & (col.measure == "accidents") & col.period.str.match(r"^\d{4}-\d{2}$")]
pooled_col = rsf_col.groupby("category").value.sum().to_dict(); col_months = sorted(rsf_col.period.unique().tolist())
bj_col = {}
for y, g in col[(col.source == "BJKS") & (col.period == "annual") & (col.measure == "share_pct")].groupby("year"):
    if str(y).isdigit(): bj_col[int(y)] = {r.category: float(r.value) for r in g.itertuples()}
who = {"rsf_totals_deaths": totals, "rsf_totals_accidents": tot_acc, "victims": victims, "veh_counts": veh_counts, "veh_share": veh_share, "moto_accidents": moto_acc,
       "bjks_moto_deaths": bj_moto, "bjks_victims": bj_victims, "collision_pooled_rsf": pooled_col, "collision_months": col_months, "collision_bjks": bj_col,
       "sources": cite(pd.concat([rsf[rsf.dimension.isin(["victim", "vehicle_type", "total"])], bj[bj.dimension.isin(["victim", "vehicle_type"])], col]))}
json.dump(who, open(OUT / "who.json", "w"), ensure_ascii=False, indent=0)
print("who.json victims years:", sorted(victims), "veh_counts:", sorted(veh_counts))

# ---------------- WHEN ----------------
BANDS = {"dawn": [4, 6], "early_morning": [4, 6], "morning": [6, 12], "noon": [12, 15], "afternoon": [15, 18], "late_afternoon": [15, 18], "evening": [18, 20], "dusk": [18, 20], "night": [20, 28]}
tod = b[(b.dimension == "time_of_day") & (b.source == "RSF") & (b.measure == "share_pct")]
tod_periods = []
for p, g in tod.groupby("period"):
    sh = {r.category: float(r.value) for r in g.itertuples()}
    cov = sum(sh.values())
    if len(sh) >= 5 and 90 <= cov <= 110:
        tod_periods.append({"period": p, "label": period_label(p), "shares": sh, "coverage_pct": round(cov, 1), "sources": cite(g)})
tod_periods.sort(key=lambda x: x["period"])
# pooled time of day: simple mean of full-coverage periods (no totals for Eid periods vs months; say so)
keys = sorted({k for pr in tod_periods for k in pr["shares"]})
canon = {}
for pr in tod_periods:
    for k, v in pr["shares"].items():
        ck = {"early_morning": "dawn", "dusk": "evening", "late_afternoon": "afternoon"}.get(k, k)
        canon.setdefault(ck, []).append(v)
tod_pooled = {k: sum(v) / len(v) for k, v in canon.items()}
_tot = sum(tod_pooled.values()) or 1
tod_pooled = {k: round(v / _tot * 100, 2) for k, v in tod_pooled.items()}  # renormalised to 100 (published tables round to 99-101)
cum = b[(b.dimension == "time_of_day") & (b.period == "2020_to_2026-07") & (b.measure == "deaths")]
cum_rows = {r.category: float(r.value) for r in cum.itertuples()}
cum_note = " ".join(cum.note.dropna().astype(str).unique().tolist())
# monthly series RSF 2020-2026
mrows = mo[mo.source == "RSF"].copy()
mrows = mrows[mrows.year.astype(str).str.isdigit()]
monthly = [{"year": int(r.year), "month": int(r.month), "accidents": None if pd.isna(r.accidents) else float(r.accidents), "deaths": None if pd.isna(r.deaths) else float(r.deaths), "injuries": None if pd.isna(r.injuries) else float(r.injuries), "url": r.citation_url} for r in mrows.itertuples()]
# Eid windows
eid = b[b.period.str.startswith("eid") & (b.dimension == "total") & (b.source == "RSF")]
eids = {}
for p, g in eid.groupby("period"):
    rec = {r.measure: float(r.value) for r in g.itertuples()}
    rec["label"] = period_label(p); rec["year"] = int(p[-4:]); rec["kind"] = "Fitr" if "fitr" in p else "Azha"; rec["sources"] = cite(g)
    eids[p] = rec
json.dump({"bands": BANDS, "tod_periods": tod_periods, "tod_pooled": tod_pooled, "tod_pooled_n": len(tod_periods), "cumulative_deaths_2020_2026": cum_rows, "cumulative_note": cum_note,
           "monthly": monthly, "eid": eids, "sources": cite(pd.concat([tod, eid]))}, open(OUT / "when.json", "w"), ensure_ascii=False, indent=0)
print("when.json tod periods:", [p["period"] for p in tod_periods], "monthly rows:", len(monthly), "eid:", sorted(eids))

# ---------------- ROADS ----------------
rc = b[b.dimension == "road_class"]
CLASS_MAP = {"national_highway": "National highway", "regional_highway": "Regional highway", "regional_road": "Regional highway", "feeder_road": "Feeder / rural road", "rural_road": "Feeder / rural road",
             "city_road": "City road", "dhaka_city": "City road", "chattogram_city": "City road", "other": "Other", "railway_crossing": "Other"}
shares = []
for (s, p), g in rc[rc.measure == "share_pct"].groupby(["source", "period"]):
    row = {}
    gg = g.groupby("category").value.mean()
    for cat, v in gg.items():
        k = CLASS_MAP.get(cat, cat); row[k] = row.get(k, 0) + float(v)
    if not (85 <= sum(row.values()) <= 115): print("  skip road share", s, p, round(sum(row.values()),1)); continue
    yr = g.year.iloc[0]
    shares.append({"source": s, "period": p, "label": period_label(p) if p != "annual" else str(yr), "year": str(yr), "shares": row, "sources": cite(g)})
shares.sort(key=lambda x: (x["source"], x["period"]))
monthly_rc = []
for p, g in rc[(rc.source == "RSF") & (rc.measure == "accidents") & rc.period.str.match(r"^\d{4}-\d{2}$")].groupby("period"):
    row = {}
    gg = g.groupby("category").value.mean()
    for cat, v in gg.items():
        k = CLASS_MAP.get(cat, cat); row[k] = row.get(k, 0) + float(v)
    monthly_rc.append({"period": p, "label": period_label(p), "counts": row, "sources": cite(g)})
monthly_rc.sort(key=lambda x: x["period"])
rn = pd.read_csv(RAW / "road_network.csv")
json.dump({"shares": shares, "monthly_counts": monthly_rc, "network": [{k: (None if (isinstance(v, float) and math.isnan(v)) else v) for k, v in r.items()} for r in rn.to_dict("records")]},
          open(OUT / "roads.json", "w"), ensure_ascii=False, indent=0)
print("roads.json shares:", [(s["source"], s["label"]) for s in shares], "monthly:", len(monthly_rc))

# ---------------- METHOD: citation index ----------------
urls = sorted(set(b.citation_url.dropna()) | set(mo.citation_url.dropna()) | set(pd.read_csv(RAW / "national_yearly.csv").citation_url.dropna()) | set(pd.read_csv(RAW / "blackspots.csv").source_url.dropna()))
json.dump({"n_citations": len(urls), "n_breakdown_rows": int(len(b)), "n_monthly_rows": int(len(mo))}, open(OUT / "method.json", "w"))
print("citations:", len(urls))
