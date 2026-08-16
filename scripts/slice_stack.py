# -*- coding: utf-8 -*-
"""
slice_stack.py — 3D mesh → horizontal contour layers for stacked laser-cut.

Slices an STL/OBJ along one axis every `board` mm, keeps the main body region
per layer (drops disconnected appendage islands, exported separately), places
SQUARE alignment holes (spread, >=1 per layer, rotation-proof), and writes one
DXF per layer + a _layers.pkl for the preview/assembly scripts.

Deps: trimesh, shapely, ezdxf, numpy.  See references/pipeline-notes.md.
"""
import os, argparse, pickle, numpy as np, trimesh, ezdxf
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely.prepared import prep

def parse():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stl", required=True, help="input STL/OBJ path")
    ap.add_argument("--out", required=True, help="project output dir")
    ap.add_argument("--size", type=float, default=150.0, help="target size (mm) along --size-axis")
    ap.add_argument("--size-axis", type=int, default=0, help="axis to scale by: 0=x(len) 1=y 2=z")
    ap.add_argument("--board", type=float, default=3.0, help="layer/board thickness mm")
    ap.add_argument("--axis", type=int, default=2, help="STACKING/slice axis: 2=z(default) 0=x 1=y")
    ap.add_argument("--hole", type=float, default=3.02, help="square alignment hole side mm")
    ap.add_argument("--wall", type=float, default=2.0, help="min wall around hole mm")
    ap.add_argument("--margin", type=float, default=5.0, help="dxf margin mm")
    ap.add_argument("--min-island", type=float, default=25.0, help="min island area mm^2 to export")
    ap.add_argument("--min-layer-area", type=float, default=0.0,
                    help="drop tiny polar cap layers below this area mm^2 (top/bottom only); "
                         "avoids fiddly slivers — sand the dome from 1-2 caps instead. 0=keep all")
    return ap.parse_args()

def main():
    a = parse()
    import glob
    DXF = os.path.join(a.out, "dxf"); ISL = os.path.join(DXF, "islands")
    os.makedirs(ISL, exist_ok=True)
    for f in glob.glob(os.path.join(DXF, "*.dxf")) + glob.glob(os.path.join(ISL, "*.dxf")):
        os.remove(f)                                   # clear stale layers from a previous run
    CLR = a.hole/2 + a.wall
    AX = a.axis
    IN = [i for i in range(3) if i != AX]        # in-plane axes
    m = trimesh.load(a.stl, force='mesh')
    parts = m.split(only_watertight=False)
    if len(parts): m = sorted(parts, key=lambda p: len(p.faces), reverse=True)[0]
    m.apply_scale(a.size / m.extents[a.size_axis])
    bmin, bmax = m.bounds
    # in-plane extents decide LONG (spread holes along it) / SHORT (centerline)
    P, Q = IN
    if (bmax[P]-bmin[P]) >= (bmax[Q]-bmin[Q]): LONG, SHORT = P, Q
    else: LONG, SHORT = Q, P
    o = {i: bmin[i] for i in IN}
    N = int(round((bmax[AX]-bmin[AX]) / a.board))
    print(f"scaled extents {m.extents.round(1)}  slice axis={AX}  -> {N} layers @ {a.board}mm")

    def toUV(p3):  # global-aligned 2D coords (LONG->u, SHORT->v)
        return np.column_stack([p3[:, LONG]-o[LONG]+a.margin, p3[:, SHORT]-o[SHORT]+a.margin])

    def polys_at(t):
        origin = [0, 0, 0]; origin[AX] = t
        normal = [0, 0, 0]; normal[AX] = 1
        sec = m.section(plane_origin=origin, plane_normal=normal)
        if sec is None: return []
        planar, to3d = sec.to_2D()
        res = []
        for poly in planar.polygons_full:
            def g(r):
                c2 = np.array(r.coords)
                return toUV(trimesh.transform_points(np.column_stack([c2, np.zeros(len(c2))]), to3d))
            e = g(poly.exterior)
            if len(e) >= 4:
                res.append(Polygon(e, [g(h) for h in poly.interiors if len(h.coords) >= 4]).buffer(0))
        return res

    ts = [bmin[AX] + (k+0.5)*a.board for k in range(N)]
    LAY = [(None, t, polys_at(t)) for t in ts]

    # Optional: drop tiny polar-cap layers at the top/bottom ends (fiddly slivers
    # that get sanded into the dome anyway). Only trims contiguous small runs at
    # the ENDS — never removes an interior layer — so a waisted shape stays intact.
    if a.min_layer_area > 0:
        area = [sum(p.area for p in ps) for _, _, ps in LAY]
        keep = [True]*len(LAY)
        for i in range(len(LAY)-1, -1, -1):
            if area[i] < a.min_layer_area: keep[i] = False
            else: break
        for i in range(len(LAY)):
            if area[i] < a.min_layer_area: keep[i] = False
            else: break
        dropped = keep.count(False)
        LAY = [L for L, k in zip(LAY, keep) if k]
        print(f"min-layer-area {a.min_layer_area}: dropped {dropped} polar-cap layers -> {len(LAY)} kept")

    LAY = [(f"{i+1:02d}", t, ps) for i, (_, t, ps) in enumerate(LAY)]   # renumber bottom-up
    N = len(LAY)
    geom = [unary_union(ps) if ps else Polygon() for _, _, ps in LAY]

    # ---- square alignment holes: anchor(max coverage) + spread(forward), centerline ----
    allb = unary_union([g for g in geom if not g.is_empty]).bounds
    W = allb[2]-allb[0]
    gu = np.arange(allb[0]+CLR, allb[2]-CLR, 1.5)
    gv = np.arange(allb[1]+CLR, allb[3]-CLR, 1.5)
    inner = [prep(g.buffer(-CLR)) if not g.is_empty else None for g in geom]
    vmid = 0.5*(allb[1]+allb[3])
    cand = []
    for u in gu:
        for v in gv:
            if abs(v-vmid) > 2.5: continue          # lock to centerline
            c = sum(1 for gi, g in enumerate(geom) if (not g.is_empty) and inner[gi].contains(Point(u, v)))
            if c >= 4: cand.append((c, u, v))
    if not cand:
        raise SystemExit("No valid hole location found — model too thin/small for this hole size.")
    cand.sort(reverse=True)
    h1 = cand[0]                                     # anchor: covers the most layers
    pool = [c for c in cand if c[0] >= 8 and abs(c[1]-h1[1]) >= 32]
    pool.sort(key=lambda t: t[1])                    # most-forward high-coverage
    h2 = pool[0] if pool else cand[1]
    if h2[1] > h1[1]: h1, h2 = h2, h1
    HOLES = [(h1[1], h1[2]), (h2[1], h2[2])]
    print("square holes (u,v):", [(round(u, 1), round(v, 1)) for u, v in HOLES],
          " coverage:", [h1[0], h2[0]], "/", N)

    # ---- keep main body per layer (regions containing a hole); islands -> appendages ----
    def in_hole(p): return any(p.buffer(1e-6).contains(Point(u, v)) for u, v in HOLES)
    hs = a.hole/2
    def sq(u, v): return [(u-hs, v-hs), (u+hs, v-hs), (u+hs, v+hs), (u-hs, v+hs)]

    def save(path, polys, holes=None):
        doc = ezdxf.new(); doc.units = ezdxf.units.MM; msp = doc.modelspace()
        doc.layers.add("CUT", color=7); doc.layers.add("LABEL", color=3)
        for poly in polys:
            msp.add_lwpolyline(np.array(poly.exterior.coords), close=True, dxfattribs={"layer": "CUT"})
            for h in poly.interiors:
                msp.add_lwpolyline(np.array(h.coords), close=True, dxfattribs={"layer": "CUT"})
        if holes:
            for (u, v) in holes:
                msp.add_lwpolyline(sq(u, v), close=True, dxfattribs={"layer": "CUT"})
        doc.saveas(path)

    KEPT, summary, nisl = [], [], 0
    for lab, t, ps in LAY:
        if not ps: KEPT.append((lab, t, [])); continue
        body = [p for p in ps if in_hole(p)]
        if not body: body = [max(ps, key=lambda p: p.area)]
        KEPT.append((lab, t, body))
        g = unary_union(body)
        hh = [(u, v) for (u, v) in HOLES if g.buffer(-CLR).contains(Point(u, v))]
        save(os.path.join(DXF, f"L{lab}.dxf"), body, hh)
        summary.append((lab, len(body), len(hh)))
        for p in ps:
            if p not in body and p.area >= a.min_island:
                nisl += 1
                save(os.path.join(ISL, f"L{lab}_island{nisl}.dxf"), [p])

    print("\nlayer | body-regions | holes")
    for lab, r, h in summary: print(f"  {lab}  |  {r}  |  {h}")
    print(f"appendage islands exported: {nisl} (dxf/islands/)")

    pickle.dump({"LAY": [(lab, t, [np.array(p.exterior.coords) for p in body]) for lab, t, body in KEPT],
                 "bounds": allb, "holes": HOLES, "board": a.board, "N": N, "hole": a.hole},
                open(os.path.join(a.out, "_layers.pkl"), "wb"))
    print("DXF ->", DXF, "\n_layers.pkl written")

if __name__ == "__main__":
    main()
