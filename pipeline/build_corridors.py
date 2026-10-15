"""Build corridors.csv: ordered waypoints routed over the OSM major-routes network.
Seeds: Wikipedia infobox coords (fetched 2026-10-15), district HQ coords from the
ifahimreza bd-districts.json (bangladesh.gov.bd / Google Maps per nuhil), or upazila
representative points from the BBS boundary GeoJSON. Each seed is snapped to the nearest
network node carrying the corridor's ref (or any trunk/primary node when ref=None)."""
import csv, json, sys
sys.path.insert(0, "/home/claude/work/data/notes")
from geo_tools import *

U = load_upazilas()
D = {d["name"]: (float(d["long"]), float(d["lat"])) for d in json.load(open(RAW + "bd-districts.json"))["districts"]}
R = load_routes()
G = build_graph(R)

def upz(name, dist):
    v = U[(name.lower(), dist.lower())]; return (v["lng"], v["lat"])

W = "wikipedia infobox"; H = "district HQ (bd-districts.json)"; P = "upazila representative point (BBS boundary)"; O = "OSM ref endpoint"
# corridor -> (total_length_km_wiki, official description, [(place, district, (lng,lat), seed_source, ref_filter)])
CORR = {
 "N1": (465, "Dhaka (Jatrabari) - Kanchpur - Daudkandi - Cumilla - Feni - Chattogram - Cox's Bazar - Teknaf (RHD; AH41)", [
    ("Jatrabari, Dhaka", "Dhaka", upz("Jatrabari", ""), P, "N1"),
    ("Kanchpur (Shitalakshya bridge)", "Narayanganj", (90.52, 23.705), "OSM N2/N1 junction approx", "N1"),
    ("Mograpara, Sonargaon", "Narayanganj", upz("Sonargaon", "Narayanganj"), P, "N1"),
    ("Meghna bridge, Gazaria", "Munshiganj", upz("Gazaria", "Munshiganj"), P, "N1"),
    ("Daudkandi", "Cumilla", (90.717, 23.533), W, "N1"),
    ("Chandina", "Cumilla", (91.0083, 23.483), W, "N1"),
    ("Cumilla (Cantonment / Alekharchar)", "Cumilla", D["Cumilla"], H, "N1"),
    ("Chauddagram", "Cumilla", (91.3133, 23.2283), W, "N1"),
    ("Feni (Mahipal)", "Feni", D["Feni"], H, "N1"),
    ("Baraiyarhat / Mirsharai", "Chattogram", (91.5362, 22.82321), P, "N1"),
    ("Sitakunda", "Chattogram", (91.6617, 22.617), W, "N1"),
    ("Chattogram city (Muradpur / Bahaddarhat)", "Chattogram", D["Chattogram"], H, "N1"),
    ("Patiya", "Chattogram", upz("Patiya", "Chattogram"), P, "N1"),
    ("Keranihat, Satkania", "Chattogram", upz("Satkania", "Chattogram"), P, "N1"),
    ("Chunati, Lohagara", "Chattogram", (92.13333, 21.9), W, "N1"),
    ("Chakaria", "Cox's Bazar", (92.07556, 21.7625), W, "N1"),
    ("Ramu", "Cox's Bazar", upz("Ramu", "Cox's Bazar"), P, "N1"),
    ("Cox's Bazar", "Cox's Bazar", D["Cox's Bazar"], H, "N1"),
    ("Ukhia", "Cox's Bazar", upz("Ukhia", "Cox's Bazar"), P, "N1"),
    ("Teknaf", "Cox's Bazar", upz("Teknaf", "Cox's Bazar"), P, "N1"),
 ]),
 "N2": (287, "Kanchpur - Bhulta - Narsingdi - Bhairab - Sarail - Madhabpur - Shaistaganj - Sherpur - Sylhet - Tamabil (RHD; AH1/AH2)", [
    ("Kanchpur", "Narayanganj", (90.52, 23.705), "OSM N2 start", "N2"),
    ("Bhulta, Rupganj", "Narayanganj", upz("Rupganj", "Narayanganj"), P, "N2"),
    ("Narsingdi (Panchdona / Sahepratap)", "Narsingdi", D["Narsingdi"], H, "N2"),
    ("Itakhola, Shibpur", "Narsingdi", upz("Shibpur", "Narsingdi"), P, "N2"),
    ("Bhairab", "Kishoreganj", upz("Bhairab", "Kishoreganj"), P, "N2"),
    ("Ashuganj", "Brahmanbaria", upz("Ashuganj", "Brahmanbaria"), P, "N2"),
    ("Sarail (Kuttapara / Bishwa Road)", "Brahmanbaria", upz("Sarail", "Brahmanbaria"), P, "N2"),
    ("Madhabpur", "Habiganj", (91.2917, 24.1033), W, "N2"),
    ("Shaistaganj / Mirpur, Bahubal", "Habiganj", upz("Bahubal", "Habiganj"), P, "N2"),
    ("Nabiganj (Aushkandi)", "Habiganj", upz("Nabiganj", "Habiganj"), P, "N2"),
    ("Sherpur, Moulvibazar", "Moulvibazar", (91.63, 24.60), "approx Sherpur bridge over Kushiyara (seed only; snapped)", "N2"),
    ("Osmaninagar / Goalabazar", "Sylhet", upz("Balaganj", "Sylhet"), P + " (Balaganj; Osmaninagar not in file)", "N2"),
    ("Dakshin Surma", "Sylhet", upz("Dakshin Surma", "Sylhet"), P, "N2"),
    ("Sylhet", "Sylhet", D["Sylhet"], H, "N2"),
    ("Jaintiapur", "Sylhet", upz("Jaintiapur", ""), P, "N2"),
    ("Tamabil", "Sylhet", (92.03, 25.18), "OSM N2 end approx", "N2"),
 ]),
 "N3": (115, "Dhaka (Banani) - Tongi - Joydebpur - Rajendrapur - Mawna - Bhaluka - Trishal - Mymensingh (RHD; AH2/AH41)", [
    ("Banani, Dhaka", "Dhaka", (90.40, 23.795), "approx Banani (seed only)", "N3"),
    ("Tongi", "Gazipur", (90.40, 23.89), "approx Tongi bridge (seed only)", "N3"),
    ("Joydebpur / Gazipur Chowrasta", "Gazipur", D["Gazipur"], H, "N3"),
    ("Rajendrapur", "Gazipur", (90.42, 24.10), "approx (seed only)", "N3"),
    ("Mawna, Sreepur", "Gazipur", (90.4898, 24.17637), P + " (file labels this polygon Sreepur/Magura; geometry is Sreepur, Gazipur)", "N3"),
    ("Bhaluka", "Mymensingh", (90.3783, 24.375), W, "N3"),
    ("Trishal", "Mymensingh", (90.3917, 24.575), W, "N3"),
    ("Mymensingh", "Mymensingh", D["Mymensingh"], H, "N3"),
 ]),
 "N4": (216, "Joydebpur - Chandra - Mirzapur - Tangail - Elenga - Madhupur - Jamalpur (RHD; AH2/AH41). Elenga - Bangabandhu Bridge east end is N405.", [
    ("Joydebpur / Gazipur Chowrasta", "Gazipur", D["Gazipur"], H, "N4"),
    ("Chandra, Kaliakair", "Gazipur", (90.217, 24.075), W, "N4"),
    ("Gorai", "Tangail", (90.159205, 24.099361), W, "N4"),
    ("Mirzapur", "Tangail", upz("Mirzapur", "Tangail"), P, "N4"),
    ("Tangail (Rabna bypass)", "Tangail", D["Tangail"], H, "N4"),
    ("Elenga, Kalihati", "Tangail", (89.92194, 24.33861), W, "N4"),
    ("Madhupur", "Tangail", upz("Madhupur", "Tangail"), P, "N4"),
    ("Jamalpur", "Jamalpur", D["Jamalpur"], H, "N4"),
 ]),
 "N405": (16, "Elenga - Bhuapur - Bangabandhu Bridge east end (RHD N405; Jamuna bridge link)", [
    ("Elenga, Kalihati", "Tangail", (89.92194, 24.33861), W, "N405"),
    ("Bhuapur", "Tangail", upz("Bhuapur", "Tangail"), P, "N405"),
    ("Bangabandhu Bridge east end", "Tangail", (89.815, 24.391), "OSM N405 west end", "N405"),
 ]),
 "N5": (625, "Dhaka (Gabtoli) - Savar - Nabinagar - Manikganj - Uthali - Paturia [ferry Paturia-Kazirhat] - Kashinathpur - Hatikumrul - Bogura - Gobindaganj - Rangpur - Saidpur - Dashmile/Beldanga - Birganj - Boda - Panchagarh - Tentulia - Banglabandha (RHD; AH2)", [
    ("Gabtoli, Dhaka", "Dhaka", (90.343, 23.78), "approx Gabtoli (seed only)", "N5"),
    ("Savar", "Dhaka", upz("Savar", "Dhaka"), P, "N5"),
    ("Nabinagar", "Dhaka", (90.26, 23.91), "approx Nabinagar (seed only)", "N5"),
    ("Dhamrai", "Dhaka", upz("Dhamrai", "Dhaka"), P, "N5"),
    ("Manikganj", "Manikganj", D["Manikganj"], H, "N5"),
    ("Paturia ferry ghat, Shibalaya", "Manikganj", upz("Shibalaya", "Manikganj"), P, "N5"),
    ("Kashinathpur, Bera (after Paturia-Kazirhat ferry)", "Pabna", upz("Bera", "Pabna"), P, "N5"),
    ("Shahjadpur", "Sirajganj", upz("Shahjadpur", "Sirajgonj"), P, "N5"),
    ("Hatikumrul, Ullapara", "Sirajganj", (89.551712, 24.419218), W, "N5"),
    ("Sherpur", "Bogura", upz("Sherpur", "Bogura"), P, "N5"),
    ("Bogura (Banani / Matidali)", "Bogura", D["Bogura"], H, "N5"),
    ("Mokamtala, Shibganj", "Bogura", upz("Shibganj", "Bogura"), P, "N5"),
    ("Gobindaganj", "Gaibandha", (89.3917, 25.133), W, "N5"),
    ("Palashbari", "Gaibandha", (89.350, 25.283), W, "N5"),
    ("Mithapukur (Shathibari)", "Rangpur", upz("Mithapukur", "Rangpur"), P, "N5"),
    ("Rangpur (Modern Mor)", "Rangpur", D["Rangpur"], H, "N5"),
    ("Taraganj", "Rangpur", upz("Taraganj", "Rangpur"), P, "N5"),
    ("Saidpur", "Nilphamari", (88.8975, 25.77806), W, "N5"),
    ("Birganj (N5 bypasses Thakurgaon town, which lies on N508)", "Dinajpur", upz("Birganj", "Dinajpur"), P, "N5"),
    ("Panchagarh", "Panchagarh", D["Panchagarh"], H, "N5"),
    ("Tetulia", "Panchagarh", upz("Tentulia", ""), P, "N5"),
    ("Banglabandha", "Panchagarh", (88.36, 26.65), "OSM N5 north end", "N5"),
 ]),
 "N6": (204, "Kashinathpur - Pabna bypass - Dasuria - Banpara - Natore - Puthia - Rajshahi - Godagari - Chapai Nawabganj - Sona Masjid (RHD; AH41)", [
    ("Kashinathpur, Bera", "Pabna", upz("Bera", "Pabna"), P, "N6"),
    ("Pabna", "Pabna", D["Pabna"], H, "N6"),
    ("Dasuria, Ishwardi", "Pabna", upz("Ishwardi", "Pabna"), P, "N6"),
    ("Banpara, Baraigram", "Natore", upz("Baraigram", "Natore"), P, "N6"),
    ("Natore", "Natore", D["Natore"], H, "N6"),
    ("Puthia", "Rajshahi", upz("Puthia", "Rajshahi"), P, "N6"),
    ("Rajshahi", "Rajshahi", D["Rajshahi"], H, "N6"),
    ("Godagari", "Rajshahi", upz("Godagari", "Rajshahi"), P, "N6"),
    ("Chapai Nawabganj", "Chapai Nawabganj", D["Nawabganj"], H, "N6"),
    ("Shibganj", "Chapai Nawabganj", upz("Shibganj", "Nawabganj"), P, "N6"),
    ("Sona Masjid", "Chapai Nawabganj", (88.14, 24.81), "OSM N6 west end", "N6"),
 ]),
 "N7": (252, "Daulatdia ferry ghat - Goalanda - Faridpur - Magura - Jhenaidah - Kaliganj - Jashore - Phultala - Khulna - Rupsha - Mongla (RHD; AH1/AH41)", [
    ("Daulatdia, Goalanda", "Rajbari", upz("Goalandaghat", "Rajbari"), P, "N7"),
    ("Faridpur", "Faridpur", D["Faridpur"], H, "N7"),
    ("Madhukhali (Majhkandi / Kamarkhali)", "Faridpur", upz("Madhukhali", "Faridpur"), P, "N7"),
    ("Magura", "Magura", D["Magura"], H, "N7"),
    ("Jhenaidah", "Jhenaidah", D["Jhenaidah"], H, "N7"),
    ("Kaliganj", "Jhenaidah", upz("Kaliganj", "Jhenaidah"), P, "N7"),
    ("Jashore (Palbari / Chanchra)", "Jashore", D["Jashore"], H, "N7"),
    ("Abhaynagar (Noapara)", "Jashore", upz("Abhaynagar", "Jashore"), P, "N7"),
    ("Phultala", "Khulna", upz("Phultala", "Khulna"), P, "N7"),
    ("Khulna", "Khulna", D["Khulna"], H, "N7"),
    ("Rupsha", "Khulna", upz("Rupsa", "Khulna"), P, "N7"),
    ("Rampal", "Bagerhat", upz("Rampal", "Bagerhat"), P, "N7"),
    ("Mongla port", "Bagerhat", (89.60, 22.47), "OSM N7 south end", "N7"),
 ]),
 "N8": (202, "Dhaka (Jatrabari) - Postogola - Sreenagar - Mawa - Padma Bridge - Zajira - Shibchar - Bhanga - Tekerhat - Madaripur - Gournadi - Barishal - Patuakhali (RHD; AH1). Jatrabari-Bhanga is the Dhaka-Mawa-Bhanga expressway.", [
    ("Jatrabari, Dhaka", "Dhaka", upz("Jatrabari", ""), P, "N8"),
    ("Keraniganj (Postogola / Abdullahpur)", "Dhaka", upz("Keraniganj", "Dhaka"), P, "N8"),
    ("Sreenagar", "Munshiganj", upz("Sreenagar", "Munshiganj"), P, "N8"),
    ("Mawa, Lohajang", "Munshiganj", upz("Lohajang", "Munshiganj"), P, "N8"),
    ("Zajira (Padma bridge south)", "Shariatpur", upz("Zanjira", ""), P, "N8"),
    ("Shibchar", "Madaripur", (90.1667, 23.35), W, "N8"),
    ("Bhanga", "Faridpur", (89.983, 23.383), W, "N8"),
    ("Tekerhat, Rajoir", "Madaripur", upz("Rajoir", "Madaripur"), P, "N8"),
    ("Madaripur (Mostafapur)", "Madaripur", D["Madaripur"], H, "N8"),
    ("Kalkini", "Madaripur", upz("Kalkini", "Madaripur"), P, "N8"),
    ("Gournadi", "Barishal", (90.2306, 22.9736), W, "N8"),
    ("Wazirpur", "Barishal", upz("Wazirpur", "Barishal"), P, "N8"),
    ("Barishal", "Barishal", D["Barishal"], H, "N8"),
    ("Bakerganj", "Barishal", upz("Bakerganj", "Barishal"), P, "N8"),
    ("Patuakhali", "Patuakhali", D["Patuakhali"], H, "N8"),
 ]),
 "N805": (110, "Bhanga - Muksudpur - Bhatiapara (Kashiani) - Gopalganj - Mollahat - Fakirhat - Khulna (RHD N805; the Dhaka-Khulna route via Padma Bridge)", [
    ("Bhanga", "Faridpur", (89.983, 23.383), W, None),
    ("Muksudpur", "Gopalganj", upz("Muksudpur", "Gopalganj"), P, "N805"),
    ("Bhatiapara, Kashiani", "Gopalganj", upz("Kashiani", "Gopalganj"), P, "N805"),
    ("Gopalganj", "Gopalganj", D["Gopalganj"], H, "N805"),
    ("Mollahat", "Bagerhat", upz("Mollahat", "Bagerhat"), P, "N805"),
    ("Fakirhat", "Bagerhat", upz("Fakirhat", "Bagerhat"), P, "N805"),
    ("Khulna (Katakhali / Rupsha east)", "Khulna", D["Khulna"], H, None),
 ]),
}

def build():
    rows = []; lines = {}
    for ref, (wlen, desc, pts) in CORR.items():
        nodes = []
        for place, dist, xy, src, rf in pts:
            n, _ = nearest_node(G, xy[0], xy[1], rf)
            nodes.append(n)
        straight = {i for i, p_ in enumerate(pts) if p_[0].startswith("Paturia ferry")}
        coords, kms, methods = route_through(G, [(n[0], n[1]) for n in nodes], None, straight=straight)
        methods = ["start"] + methods
        lines[ref] = coords
        for i, ((place, dist, xy, src, rf), n, km, meth) in enumerate(zip(pts, nodes, kms, methods), 1):
            snap_off = km_len(LineString([xy, n]))
            rows.append(dict(corridor=ref, seq=i, place=place, district=dist, lat=round(n[1], 5), lng=round(n[0], 5),
                             km_from_start=km, total_length_km=wlen, routed_length_km=kms[-1],
                             leg_method=meth, seed_source=src, seed_snap_offset_km=round(snap_off, 1), official_route=desc))
    return rows, lines

if __name__ == "__main__":
    rows, lines = build()
    with open("/home/claude/work/data/raw/corridors.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    json.dump({k: [[round(x, 5), round(y, 5)] for x, y in v] for k, v in lines.items()}, open(RAW + "corridor_polylines.json", "w"))
    for r in rows: print(r["corridor"], r["seq"], r["place"], r["km_from_start"], r["lat"], r["lng"], "off", r["seed_snap_offset_km"])
