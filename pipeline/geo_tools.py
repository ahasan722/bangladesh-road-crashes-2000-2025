"""Helpers: upazila centroids from the ifahimreza boundary GeoJSON, and
ordered corridor polylines + chainage from the OSM-derived bd-major-routes.geojson.
Run with: python3 -I geo_tools.py  (prints sanity checks)."""
import json, math, collections
from shapely.geometry import shape, LineString, Point, MultiLineString
from shapely.ops import linemerge, nearest_points

RAW = "/home/claude/work/data/raw/roads/"

def load_upazilas():
    d = json.load(open(RAW + "admin/bangladesh.geojson"))
    out = {}
    for f in d["features"]:
        p = f["properties"]; g = shape(f["geometry"])
        c = g.representative_point()
        key = (p["name"].lower(), p["district_name"].lower())
        out[key] = dict(name=p["name"], district=p["district_name"], division=p["division_name"],
                        lat=round(c.y, 5), lng=round(c.x, 5), geom=g)
    return out

def load_routes():
    d = json.load(open(RAW + "bd-major-routes.geojson"))
    by_ref = collections.defaultdict(list)
    for f in d["features"]:
        r = f["properties"].get("ref") or ""
        g = f["geometry"]
        if g["type"] == "LineString":
            by_ref[r].append(LineString(g["coordinates"]))
        else:
            for c in g["coordinates"]:
                by_ref[r].append(LineString(c))
    return by_ref

def km_len(line):
    s = 0.0
    cs = list(line.coords)
    for (x1, y1), (x2, y2) in zip(cs, cs[1:]):
        dx = (x2 - x1) * math.cos(math.radians((y1 + y2) / 2)) * 111.32
        dy = (y2 - y1) * 110.574
        s += math.hypot(dx, dy)
    return s

def corridor_line(by_ref, ref, start_xy):
    """Merge OSM ways for a ref into one longest polyline, oriented from start_xy.
    Dual carriageways produce parallel strands; we keep the longest merged strand."""
    merged = linemerge(MultiLineString(by_ref[ref]))
    lines = list(merged.geoms) if hasattr(merged, "geoms") else [merged]
    lines.sort(key=km_len, reverse=True)
    main = lines[0]
    cs = list(main.coords)
    if Point(cs[-1]).distance(Point(start_xy)) < Point(cs[0]).distance(Point(start_xy)):
        cs = cs[::-1]
    return LineString(cs), lines

def chainage_km(line, lng, lat):
    """km from line start of the nearest point on line; also offset in km."""
    p = Point(lng, lat)
    q = nearest_points(line, p)[0]
    d = line.project(q)  # in degrees along line
    # convert: walk the line up to d
    cs = list(line.coords); acc = 0.0; accdeg = 0.0
    for (x1, y1), (x2, y2) in zip(cs, cs[1:]):
        seg = math.hypot(x2 - x1, y2 - y1)
        if accdeg + seg >= d:
            frac = (d - accdeg) / seg if seg else 0
            dx = (x2 - x1) * frac * math.cos(math.radians(y1)) * 111.32
            dy = (y2 - y1) * frac * 110.574
            acc += math.hypot(dx, dy)
            break
        accdeg += seg
        dx = (x2 - x1) * math.cos(math.radians((y1 + y2) / 2)) * 111.32
        dy = (y2 - y1) * 110.574
        acc += math.hypot(dx, dy)
    off = math.hypot((q.x - lng) * math.cos(math.radians(lat)) * 111.32, (q.y - lat) * 110.574)
    return round(acc, 1), round(q.y, 5), round(q.x, 5), round(off, 2)

if __name__ == "__main__":
    U = load_upazilas()
    print("upazilas", len(U), U[("mirsharai", "chattogram")] if ("mirsharai", "chattogram") in U else [k for k in U if k[0].startswith("mirs")])
    R = load_routes()
    for ref, start in [("N1", (90.43, 23.71)), ("N2", (90.52, 23.70)), ("N3", (90.40, 23.81)), ("N4", (90.40, 23.99)),
                       ("N5", (90.34, 23.78)), ("N6", (89.6, 24.0)), ("N7", (89.75, 23.77)), ("N8", (90.43, 23.71)), ("N405", (89.92, 24.34))]:
        line, strands = corridor_line(R, ref, start)
        print(ref, "strands", len(strands), "main km", round(km_len(line)), "top5", [round(km_len(s)) for s in strands[:5]],
              "start", [round(v, 3) for v in line.coords[0]], "end", [round(v, 3) for v in line.coords[-1]])

# ---------------- graph routing over the OSM major-routes network ----------------
import networkx as nx

def build_graph(by_ref, snap=4):
    """Nodes = coordinates rounded to `snap` decimals (~11 m); edges = way segments with km weight.
    Also bridge dangling endpoints within 250 m so dual-carriageway gaps are passable."""
    G = nx.Graph()
    def key(x, y): return (round(x, snap), round(y, snap))
    ends = []
    for ref, lines in by_ref.items():
        for ln in lines:
            cs = list(ln.coords)
            for (x1, y1), (x2, y2) in zip(cs, cs[1:]):
                a, b = key(x1, y1), key(x2, y2)
                if a == b: continue
                w = km_len(LineString([(x1, y1), (x2, y2)]))
                if G.has_edge(a, b): w = min(w, G[a][b]["w"])
                G.add_edge(a, b, w=w, ref=ref)
            ends.append(key(*cs[0])); ends.append(key(*cs[-1]))
    # bridge gaps between endpoints
    from shapely.strtree import STRtree
    pts = [Point(e) for e in ends]
    tree = STRtree(pts)
    for i, p in enumerate(pts):
        for j in tree.query(p.buffer(0.012)):
            if j <= i: continue
            a, b = ends[i], ends[j]
            if a == b or G.has_edge(a, b): continue
            d = km_len(LineString([a, b]))
            if d <= 1.2:
                G.add_edge(a, b, w=d, ref="gap")
    return G

def nearest_node(G, lng, lat, ref=None):
    best, bd = None, 1e9
    for n in G.nodes:
        if ref and not any(G[n][m].get("ref") == ref for m in G[n]): continue
        d = (n[0] - lng) ** 2 + ((n[1] - lat) * 1.0) ** 2
        if d < bd: bd, best = d, n
    return best, math.sqrt(bd) * 111

def route_through(G, waypoints, ref=None, straight=(), detour_factor=1.7, detour_slack=6.0):
    """waypoints: list of (lng,lat). Returns list of coords, cumulative km at each waypoint, and
    a per-leg method list ('network' | 'straight'). Legs whose index is in `straight` (ferry crossings)
    or whose network path is > detour_factor*crow + slack km (missing data) use a straight line."""
    nodes = [nearest_node(G, x, y, ref)[0] for x, y in waypoints]
    coords, kms, acc, methods = [], [0.0], 0.0, []
    for i, (a, b) in enumerate(zip(nodes, nodes[1:])):
        crow = km_len(LineString([a, b]))
        path, method = [a, b], "straight"
        if i not in straight:
            try:
                cand = nx.shortest_path(G, a, b, weight="w")
                L = sum(G[u][v]["w"] for u, v in zip(cand, cand[1:]))
                if L <= detour_factor * crow + detour_slack:
                    path, method = cand, "network"
            except nx.NetworkXNoPath:
                pass
        for u, v in zip(path, path[1:]):
            acc += G[u][v]["w"] if (method == "network" and G.has_edge(u, v)) else km_len(LineString([u, v]))
        coords.extend(path if not coords else path[1:])
        kms.append(round(acc, 1)); methods.append(method)
    return coords, kms, methods

def point_at_km(coords, km):
    acc = 0.0
    for (x1, y1), (x2, y2) in zip(coords, coords[1:]):
        seg = km_len(LineString([(x1, y1), (x2, y2)]))
        if acc + seg >= km:
            f = (km - acc) / seg if seg else 0
            return round(y1 + (y2 - y1) * f, 5), round(x1 + (x2 - x1) * f, 5)
        acc += seg
    return round(coords[-1][1], 5), round(coords[-1][0], 5)
