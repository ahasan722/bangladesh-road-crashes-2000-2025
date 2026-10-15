"""population.csv, road_network.csv, traffic_exposure.csv from figures fetched 2026-10-15."""
import csv
OUT = "/home/claude/work/data/raw/"

# ------------------------------------------------------------------ population
# 2022 = BBS Population & Housing Census 2022 (final, enumerated) as carried on en.wikipedia division pages / Districts of Bangladesh.
# 2011 = BBS Census 2011 (enumerated) as carried on en.wikipedia division/district pages.
# Where the division page gave no 2011 column (Khulna, Rajshahi, Rangpur), 2011 came from each district article's infobox/demographics.
# Area from en.wikipedia Districts_of_Bangladesh table (km2).
WD = "https://en.wikipedia.org/wiki/Districts_of_Bangladesh"
DIV = {"Dhaka": "https://en.wikipedia.org/wiki/Dhaka_Division", "Chattogram": "https://en.wikipedia.org/wiki/Chittagong_Division",
       "Rajshahi": "https://en.wikipedia.org/wiki/Rajshahi_Division", "Khulna": "https://en.wikipedia.org/wiki/Khulna_Division",
       "Barishal": "https://en.wikipedia.org/wiki/Barisal_Division", "Sylhet": "https://en.wikipedia.org/wiki/Sylhet_Division",
       "Rangpur": "https://en.wikipedia.org/wiki/Rangpur_Division", "Mymensingh": "https://en.wikipedia.org/wiki/Mymensingh_Division"}
def dist_url(n): return "https://en.wikipedia.org/wiki/" + n.replace(" ", "_") + "_District"
# name, division, pop2011, pop2022, area, source
D = [
 ("Dhaka","Dhaka",12043977,14734024,1463.60,DIV["Dhaka"]), ("Gazipur","Dhaka",3403912,5262978,1806.36,DIV["Dhaka"]),
 ("Manikganj","Dhaka",1392867,1557927,1383.66,DIV["Dhaka"]), ("Munshiganj","Dhaka",1445660,1625354,1004.29,DIV["Dhaka"]),
 ("Narayanganj","Dhaka",2948217,3908898,684.37,DIV["Dhaka"]), ("Narsingdi","Dhaka",2224944,2584335,1150.14,DIV["Dhaka"]),
 ("Kishoreganj","Dhaka",2911907,3267626,2688.53,DIV["Dhaka"]), ("Tangail","Dhaka",3750781,4037316,3414.35,DIV["Dhaka"]),
 ("Faridpur","Dhaka",1912969,2162754,2052.68,DIV["Dhaka"]), ("Gopalganj","Dhaka",1172415,1295005,1468.74,DIV["Dhaka"]),
 ("Madaripur","Dhaka",1165952,1292963,1125.69,DIV["Dhaka"]), ("Rajbari","Dhaka",1049778,1189743,1092.28,DIV["Dhaka"]),
 ("Shariatpur","Dhaka",1155824,1294511,1174.05,DIV["Dhaka"]),
 ("Brahmanbaria","Chattogram",2840498,3306563,1881.20,DIV["Chattogram"]), ("Cumilla","Chattogram",5387288,6212216,3146.30,DIV["Chattogram"]),
 ("Chandpur","Chattogram",2416018,2635748,1645.32,DIV["Chattogram"]), ("Lakshmipur","Chattogram",1729188,1938111,1440.39,DIV["Chattogram"]),
 ("Noakhali","Chattogram",3108083,3625252,3685.87,DIV["Chattogram"]), ("Feni","Chattogram",1437371,1648896,990.36,DIV["Chattogram"]),
 ("Khagrachhari","Chattogram",613917,714119,2749.16,DIV["Chattogram"]), ("Rangamati","Chattogram",595979,647587,6116.11,DIV["Chattogram"]),
 ("Bandarban","Chattogram",388335,481109,4479.01,DIV["Chattogram"]), ("Chattogram","Chattogram",7616352,9169464,5282.92,DIV["Chattogram"]),
 ("Cox's Bazar","Chattogram",2289990,2823265,2491.85,DIV["Chattogram"]),
 ("Rajshahi","Rajshahi",2595197,2915009,2425.37,dist_url("Rajshahi")), ("Bogura","Rajshahi",3400874,3734297,2898.68,"https://en.wikipedia.org/wiki/Bogra_District"),
 ("Pabna","Rajshahi",2523179,2909624,2376.13,dist_url("Pabna")), ("Joypurhat","Rajshahi",913768,956431,965.44,dist_url("Joypurhat")),
 ("Sirajganj","Rajshahi",3097489,3357706,2402.02,dist_url("Sirajganj")), ("Naogaon","Rajshahi",2600157,2784599,3435.67,dist_url("Naogaon")),
 ("Natore","Rajshahi",1706673,1859922,1900.19,dist_url("Natore")), ("Chapai Nawabganj","Rajshahi",1647521,1835528,1702.55,dist_url("Chapai Nawabganj")),
 ("Jashore","Khulna",2764547,3076144,2606.94,dist_url("Jashore")), ("Khulna","Khulna",2318527,2613385,4394.45,dist_url("Khulna")),
 ("Kushtia","Khulna",1946868,2149692,1608.78,dist_url("Kushtia")), ("Satkhira","Khulna",1985959,2196582,3817.29,dist_url("Satkhira")),
 ("Jhenaidah","Khulna",1771304,2005849,1964.77,dist_url("Jhenaidah")), ("Bagerhat","Khulna",1476090,1613076,3959.11,dist_url("Bagerhat")),
 ("Chuadanga","Khulna",1129015,1234054,1174.10,dist_url("Chuadanga")), ("Magura","Khulna",918419,1033115,1039.10,dist_url("Magura")),
 ("Narail","Khulna",721668,788671,967.99,dist_url("Narail")), ("Meherpur","Khulna",655392,705356,741.62,dist_url("Meherpur")),
 ("Barishal","Barishal",2324310,2570446,2784.52,DIV["Barishal"]), ("Barguna","Barishal",892781,1010531,1831.31,DIV["Barishal"]),
 ("Bhola","Barishal",1776795,1932518,3403.48,DIV["Barishal"]), ("Jhalokati","Barishal",682669,661160,706.76,DIV["Barishal"]),
 ("Patuakhali","Barishal",1535854,1727254,3221.31,DIV["Barishal"]), ("Pirojpur","Barishal",1113257,1198195,1277.80,DIV["Barishal"]),
 ("Habiganj","Sylhet",2089001,2358747,2536.58,DIV["Sylhet"]), ("Moulvibazar","Sylhet",1919062,2123349,2601.84,DIV["Sylhet"]),
 ("Sunamganj","Sylhet",2467968,2695294,3669.58,DIV["Sylhet"]), ("Sylhet","Sylhet",3434188,3856974,3490.40,DIV["Sylhet"]),
 ("Rangpur","Rangpur",2881086,3169614,2400.56,dist_url("Rangpur")), ("Dinajpur","Rangpur",2990128,3315236,3437.98,"https://en.wikipedia.org/wiki/Dinajpur_District,_Bangladesh"),
 ("Kurigram","Rangpur",2069073,2329160,2245.04,dist_url("Kurigram")), ("Gaibandha","Rangpur",2379255,2562233,2179.27,dist_url("Gaibandha")),
 ("Lalmonirhat","Rangpur",1256099,1428406,1247.37,dist_url("Lalmonirhat")), ("Nilphamari","Rangpur",1834231,2092568,1580.59,dist_url("Nilphamari")),
 ("Panchagarh","Rangpur",987644,1179843,1404.63,dist_url("Panchagarh")), ("Thakurgaon","Rangpur",1390042,1533895,1809.52,dist_url("Thakurgaon")),
 ("Mymensingh","Mymensingh",5110272,5898747,4394.57,DIV["Mymensingh"]), ("Jamalpur","Mymensingh",2292674,2499627,2115.16,DIV["Mymensingh"]),
 ("Netrokona","Mymensingh",2229642,2324665,2794.28,DIV["Mymensingh"]), ("Sherpur","Mymensingh",1358325,1501751,1364.67,DIV["Mymensingh"]),
]
assert len(D) == 64, len(D)
# Division totals: 2022 from en.wikipedia Divisions_of_Bangladesh (BBS 2022 final); 2011 from division pages where given, else sum of districts.
DIVTOT = {  # division: (pop2011_page, pop2022_page, area_page)
 "Dhaka": (36433505, 44215107, 20593.74), "Chattogram": (28423019, 33202326, 33908.55), "Rajshahi": (None, 20353119, 18153.08),
 "Khulna": (None, 17416645, 22284.22), "Barishal": (8325666, 9100102, 13225.20), "Sylhet": (None, 11034863, 12635.22),
 "Rangpur": (15787758, 17610956, 16184.99), "Mymensingh": (10990913, 12225498, 10584.06)}
rows = []
for dv, (p11, p22, area) in DIVTOT.items():
    s11 = sum(d[2] for d in D if d[1] == dv); s22 = sum(d[3] for d in D if d[1] == dv)
    rows.append(dict(level="division", name=dv, division=dv, pop_2011=p11 if p11 else s11, pop_2022=p22, area_km2=area,
                     source_url="https://en.wikipedia.org/wiki/Divisions_of_Bangladesh" + ("" if p11 else " (2011 = sum of district rows)"),
                     note=f"sum of districts: 2011={s11}, 2022={s22}"))
for n, dv, p11, p22, a, u in D:
    rows.append(dict(level="district", name=n, division=dv, pop_2011=p11, pop_2022=p22, area_km2=a, source_url=u, note="BBS Census 2011 / Census 2022 (final) as carried on en.wikipedia"))
with open(OUT + "population.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("population rows", len(rows), "nat 2011", sum(d[2] for d in D), "nat 2022", sum(d[3] for d in D))

# ------------------------------------------------------------------ road network
RN = [
 # year, agency, class, km, url, note
 (2006, "RHD", "national", 3529, "https://proceedings-paris2007.piarc.org/ressources/files/8/Presentation-TS4-4-HOSSAIN.pdf", "Road Fund Establishment Office 2006 (PIARC 2007 paper)"),
 (2006, "RHD", "regional", 4127, "https://proceedings-paris2007.piarc.org/ressources/files/8/Presentation-TS4-4-HOSSAIN.pdf", ""),
 (2006, "RHD", "zilla", 13126, "https://proceedings-paris2007.piarc.org/ressources/files/8/Presentation-TS4-4-HOSSAIN.pdf", ""),
 (2006, "LGED", "upazila", 36166, "https://proceedings-paris2007.piarc.org/ressources/files/8/Presentation-TS4-4-HOSSAIN.pdf", "17,889 km paved"),
 (2006, "LGED", "union", 42329, "https://proceedings-paris2007.piarc.org/ressources/files/8/Presentation-TS4-4-HOSSAIN.pdf", "8,515 km paved"),
 (2006, "LGED", "village", 171335, "https://proceedings-paris2007.piarc.org/ressources/files/8/Presentation-TS4-4-HOSSAIN.pdf", "7,583 km paved"),
 (1991, "RHD", "national", 3163, "https://www.jica.go.jp/english/our_work/social_environmental/id/asia/south/bangladesh/c8h0vm0000bikdzb-att/c8h0vm0000dqx3lv.pdf", "paved 3,002 + unpaved 161 (JICA Matarbari access road EIA, Table 3.1-2)"),
 (1991, "RHD", "regional", 2911, "https://www.jica.go.jp/english/our_work/social_environmental/id/asia/south/bangladesh/c8h0vm0000bikdzb-att/c8h0vm0000dqx3lv.pdf", "paved 2,262 + unpaved 649"),
 (1991, "RHD", "zilla", 9596, "https://www.jica.go.jp/english/our_work/social_environmental/id/asia/south/bangladesh/c8h0vm0000bikdzb-att/c8h0vm0000dqx3lv.pdf", "paved 4,440 + unpaved 5,156"),
 (2007, "RHD", "national", 3570, "https://www.jica.go.jp/english/our_work/social_environmental/id/asia/south/bangladesh/c8h0vm0000bikdzb-att/c8h0vm0000dqx3lv.pdf", "paved 3,485 + unpaved 85"),
 (2007, "RHD", "regional", 4323, "https://www.jica.go.jp/english/our_work/social_environmental/id/asia/south/bangladesh/c8h0vm0000bikdzb-att/c8h0vm0000dqx3lv.pdf", "paved 4,117 + unpaved 206"),
 (2007, "RHD", "zilla", 13678, "https://www.jica.go.jp/english/our_work/social_environmental/id/asia/south/bangladesh/c8h0vm0000bikdzb-att/c8h0vm0000dqx3lv.pdf", "paved 9,719 + unpaved 3,959"),
 (2011, "RHD", "national", 3537, "https://ewsdata.rightsindevelopment.org/files/documents/16/ADB-40540-016_cYNExBY.pdf", "ADB 40540-016 sector assessment Table 2; 65% good-fair"),
 (2011, "RHD", "regional", 4275, "https://ewsdata.rightsindevelopment.org/files/documents/16/ADB-40540-016_cYNExBY.pdf", "46% good-fair"),
 (2011, "RHD", "zilla", 13458, "https://ewsdata.rightsindevelopment.org/files/documents/16/ADB-40540-016_cYNExBY.pdf", "25% good-fair"),
 (2015, "RHD", "national", 3813, "https://www.jica.go.jp/english/our_work/social_environmental/id/asia/south/bangladesh/c8h0vm0000bikdzb-att/c8h0vm0000dqx3lv.pdf", "paved 3,759 + unpaved 54; same figure in ADB 2016 table"),
 (2015, "RHD", "regional", 4247, "https://www.jica.go.jp/english/our_work/social_environmental/id/asia/south/bangladesh/c8h0vm0000bikdzb-att/c8h0vm0000dqx3lv.pdf", "paved 4,043 + unpaved 204"),
 (2015, "RHD", "zilla", 13242, "https://www.jica.go.jp/english/our_work/social_environmental/id/asia/south/bangladesh/c8h0vm0000bikdzb-att/c8h0vm0000dqx3lv.pdf", "paved 11,584 + unpaved 1,658"),
 (2021, "RHD", "national", 3991, "https://www.adb.org/sites/default/files/linked-documents/40540-019-ld-04.pdf", "ADB 40540-019 sector assessment Table 3; 92% good-fair"),
 (2021, "RHD", "regional", 4898, "https://www.adb.org/sites/default/files/linked-documents/40540-019-ld-04.pdf", "88% good-fair"),
 (2021, "RHD", "zilla", 13589, "https://www.adb.org/sites/default/files/linked-documents/40540-019-ld-04.pdf", "74% good-fair; total 22,478"),
 (2020, "RHD", "total", 22096, "https://www.thedailystar.net/frontpage/news/20pc-roads-sorry-state-1926745", "HDM survey Nov 2019-Mar 2020 (19,282 km surveyed; 18.6% poor-very bad)"),
 ("n.d. (RHD 'Road Network at a Glance', c.2015-2019)", "RHD", "national", 3544.06, "https://d10.dlca.logcluster.org/node/4469", "WFP Logistics Capacity Assessment copy of RHD table"),
 ("n.d. (RHD 'Road Network at a Glance', c.2015-2019)", "RHD", "regional", 4280.02, "https://d10.dlca.logcluster.org/node/4469", ""),
 ("n.d. (RHD 'Road Network at a Glance', c.2015-2019)", "RHD", "zilla", 13659.13, "https://d10.dlca.logcluster.org/node/4469", "total 21,483.21"),
 ("n.d. (Wikipedia, c.2023)", "RHD", "national", 3990.75, "https://en.wikipedia.org/wiki/List_of_roads_in_Bangladesh", "matches ADB 2021 figure (3,991)"),
 ("n.d. (Wikipedia, c.2023)", "RHD", "regional", 4206.121, "https://en.wikipedia.org/wiki/List_of_roads_in_Bangladesh", ""),
 ("n.d. (Wikipedia, c.2023)", "RHD", "zilla", 13121.757, "https://en.wikipedia.org/wiki/List_of_roads_in_Bangladesh", ""),
 ("n.d. (Wikipedia, c.2023)", "LGED", "upazila", 37800, "https://en.wikipedia.org/wiki/List_of_roads_in_Bangladesh", "page total network >375,000 km in 2023"),
 ("n.d. (Wikipedia, c.2023)", "LGED", "union", 44750, "https://en.wikipedia.org/wiki/List_of_roads_in_Bangladesh", ""),
 ("n.d. (Wikipedia, c.2023)", "LGED", "village", 215750, "https://en.wikipedia.org/wiki/List_of_roads_in_Bangladesh", ""),
]
with open(OUT + "road_network.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["year", "agency", "road_class", "length_km", "source_url", "note"]); w.writerows(RN)
print("road_network rows", len(RN))

# ------------------------------------------------------------------ traffic exposure
J = "https://www.jica.go.jp/english/our_work/social_environmental/id/asia/south/bangladesh/c8h0vm0000bikdzb-att/c8h0vm0000dqx3lv.pdf"
TE = [  # corridor, section, year, aadt, unit, url, note
 ("N1", "N1-38 Chittagong (Bahaddarhat) - Maizzertek (Z1804)", 2016, 9697, "veh/day (17,850 PCU)", J, "RHD Traffic Summary Sheet 2016 link counts, quoted in JICA Matarbari access road EIA"),
 ("N1", "N1-40 Sikolbaha (Z1018) - Shantirhat (Z1071)", 2016, 9204, "veh/day (17,169 PCU)", J, ""),
 ("N1", "N1-43 Mansertek (N107) - Patiya (Z1059)", 2016, 10352, "veh/day (18,338 PCU)", J, ""),
 ("N1", "N1-44 Patiya (Z1059) - Patiya Dakbanglo (Z1057)", 2016, 9130, "veh/day (14,688 PCU)", J, ""),
 ("N1", "N1-46 Patiya (Z1039) - Khanhat (Z1026)", 2016, 11842, "veh/day (17,701 PCU)", J, ""),
 ("N1", "N1-49 Keranihat (N108) - Z1019", 2016, 12680, "veh/day (17,160 PCU)", J, ""),
 ("N1", "N1-52 Chunati (R171) - Aziznagar (Z1007)", 2016, 10851, "veh/day (21,450 PCU)", J, ""),
 ("N1", "N1-56 Baraitali (Z1002) - Z1126", 2016, 7178, "veh/day (14,469 PCU)", J, ""),
 ("N1", "N1-59 Chakaria (R172) - Faishakhali (Z1005)", 2016, 8846, "veh/day (13,499 PCU)", J, ""),
 ("N1", "N1-61 Dulahazra (Z1130) - Khutakhali (Z1131)", 2016, 5053, "veh/day (7,523 PCU)", J, ""),
 ("N1", "N1-63 Ramu (Z1001) - Ramu (N109)", 2016, 5053, "veh/day (7,250 PCU)", J, ""),
 ("N1", "near Chakaria (sectional count)", 2017, 13008, "veh/day (16,489 PCU), 24h count not annualised", J, "motorcycle 2,427; 3-wheeler 5,168; car 1,175; utility 1,548; bus 827; truck 1,863"),
 ("N1", "Chittagong - Keranihat (forecast)", 2026, 48206, "PCU/day forecast", J, ""),
 ("N1", "Int. Z1018 - Int. N107 (Chattogram south)", 2015, 14200, "PCU/day (JICA forecast base year)", "https://openjicareport.jica.go.jp/pdf/12249504_02.pdf", "JICA Table 6.2.30, 100 PCU/day units; 2020: 18,000; 2030: 25,200"),
 ("N1", "Int. N107 - Patiya", 2015, 17100, "PCU/day", "https://openjicareport.jica.go.jp/pdf/12249504_02.pdf", "2020: 21,500; 2030: 30,000"),
 ("N1", "Patiya - Chandanaish", 2015, 15700, "PCU/day", "https://openjicareport.jica.go.jp/pdf/12249504_02.pdf", "2020: 19,800; 2030: 27,700"),
 ("N1", "Chandanaish - Int. N108 (Keranihat)", 2015, 13000, "PCU/day", "https://openjicareport.jica.go.jp/pdf/12249504_02.pdf", "2020: 16,400; 2030: 23,100"),
 ("N1", "Int. N108 - Chunati", 2015, 27200, "PCU/day", "https://openjicareport.jica.go.jp/pdf/12249504_02.pdf", "2020: 34,500; 2030: 48,500"),
 ("N1", "Chunati - Int. R172 (Chakaria)", 2015, 13000, "PCU/day", "https://openjicareport.jica.go.jp/pdf/12249504_02.pdf", "2020: 16,400; 2030: 23,000"),
 ("N1", "Int. R172 - Dulahazara", 2015, 14900, "PCU/day", "https://openjicareport.jica.go.jp/pdf/12249504_02.pdf", "2020: 18,900; 2030: 26,600"),
 ("N1", "Dulahazara - Int. Z1009", 2015, 8300, "PCU/day", "https://openjicareport.jica.go.jp/pdf/12249504_02.pdf", "2020: 10,500; 2030: 14,800"),
 ("N5", "Dhaka-Rangpur highway (whole), normal day", 2024, 20000, "veh/day (press figure, not RHD census)", "https://en.prothomalo.com/bangladesh/local-news/j7uyuxyd4v", "rises to >50,000 at Eid (Prothom Alo)"),
 ("N1", "Dhaka-Chattogram (whole, 2-lane pre-4-laning)", "n.d.", None, "", "https://pppo.gov.bd/projects-dhaka-chittagong-access-controlled-highway.php", "PPP Office page gives no AADT; N1 231 km Dhaka-Chattogram"),
]
with open(OUT + "traffic_exposure.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["corridor", "section", "year", "aadt", "unit", "source_url", "note"]); w.writerows(TE)
print("traffic rows", len(TE))
