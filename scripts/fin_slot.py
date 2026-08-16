# -*- coding: utf-8 -*-
"""
fin_slot.py — side fins (pectoral) as tab-into-seam pieces for a stacked model.

A stacked body already has a horizontal seam at every layer edge. This makes a
hidden, self-aligning fin joint: cut a small NOTCH (pocket) into one layer's
left/right edge, give each fin a matching TAB, insert + glue. Stronger and
cleaner than surface-gluing a fin onto a sanded curve.

Re-saves the chosen layer L<n>.dxf with the two edge notches (holes preserved),
and writes PEC-R.dxf / PEC-L.dxf (tab + paddle blade). Attach after sanding.
"""
import os, argparse, pickle, numpy as np, ezdxf
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--layer", type=int, default=0, help="layer number to notch (0=auto ~35%% up)")
    ap.add_argument("--xfrac", type=float, default=0.42, help="fore-aft fin position along body (0=front)")
    ap.add_argument("--tab-w", type=float, default=8.0, help="tab width mm (along body)")
    ap.add_argument("--tab-l", type=float, default=6.0, help="tab length mm (into body)")
    ap.add_argument("--fin-len", type=float, default=20.0, help="blade length beyond edge mm")
    ap.add_argument("--fin-w", type=float, default=13.0, help="blade width mm")
    ap.add_argument("--fit", type=float, default=0.05, help="tab undersize per side mm (kerf gives rest)")
    a = ap.parse_args()
    DXF = os.path.join(a.out, "dxf")
    d = pickle.load(open(os.path.join(a.out, "_layers.pkl"), "rb"))
    LAY, HOLES, HS, allb = d["LAY"], d["holes"], d["hole"], d["bounds"]
    CLR = HS/2 + 2.0
    N = len(LAY)
    li = a.layer if a.layer > 0 else max(1, round(0.35*N))
    lab, Z, regs = LAY[li-1]
    poly = max((Polygon(r) for r in regs), key=lambda p: p.area)
    X0, X1 = allb[0], allb[2]; xpos = X0 + a.xfrac*(X1-X0)
    ymid = 0.5*(allb[1]+allb[3])
    inter = poly.intersection(LineString([(xpos, ymid-200), (xpos, ymid+200)]))
    if inter.is_empty: raise SystemExit(f"x={xpos:.1f} not inside layer L{lab}; adjust --xfrac/--layer")
    ys = np.array(inter.coords)[:, 1] if inter.geom_type == "LineString" else \
         np.concatenate([np.array(g.coords)[:, 1] for g in inter.geoms])
    yR, yL = ys.max(), ys.min()                    # right / left edge at xpos
    tw = a.tab_w
    notchR = box(xpos-tw/2, yR-a.tab_l, xpos+tw/2, yR+2)
    notchL = box(xpos-tw/2, yL-2, xpos+tw/2, yL+a.tab_l)
    body2 = poly.difference(notchR).difference(notchL)
    polys = list(body2.geoms) if body2.geom_type == "MultiPolygon" else [body2]

    def save(path, plist, holes=None):
        doc = ezdxf.new(); doc.units = ezdxf.units.MM; msp = doc.modelspace()
        doc.layers.add("CUT", color=7); doc.layers.add("LABEL", color=3)
        for p in plist:
            msp.add_lwpolyline(np.array(p.exterior.coords), close=True, dxfattribs={"layer": "CUT"})
            for h in p.interiors: msp.add_lwpolyline(np.array(h.coords), close=True, dxfattribs={"layer": "CUT"})
        h = HS/2
        if holes:
            for (u, v) in holes:
                msp.add_lwpolyline([(u-h, v-h), (u+h, v-h), (u+h, v+h), (u-h, v+h)], close=True, dxfattribs={"layer": "CUT"})
        doc.saveas(path)

    g2 = unary_union(polys)
    hh = [(u, v) for (u, v) in HOLES if g2.buffer(-CLR).contains(Point(u, v))]
    save(os.path.join(DXF, f"L{lab}.dxf"), polys, hh)

    # fin piece: tab (fits notch, minus fit) + paddle blade (y = outward)
    tw2 = tw/2 - a.fit; tl = a.tab_l; FL, FW = a.fin_len, a.fin_w/2
    fin = [(-tw2, 0), (tw2, 0), (tw2, tl),
           (FW, tl+FL*0.45), (FW*0.55, tl+FL), (-FW*0.55, tl+FL),
           (-FW, tl+FL*0.45), (-tw2, tl)]
    for nm in ("PEC-R", "PEC-L"):
        doc = ezdxf.new(); doc.units = ezdxf.units.MM; msp = doc.modelspace()
        doc.layers.add("CUT", color=7); doc.layers.add("LABEL", color=3)
        msp.add_lwpolyline(fin, close=True, dxfattribs={"layer": "CUT"})
        msp.add_text(nm, height=3, dxfattribs={"layer": "LABEL"}).set_placement((-tw2, -6))
        doc.saveas(os.path.join(DXF, f"{nm}.dxf"))

    print(f"notched layer L{lab} at x={xpos:.0f} (both edges); wrote PEC-R.dxf, PEC-L.dxf")
    print(f"insert each fin tab into its edge notch (in the seam) + glue, after sanding")

if __name__ == "__main__":
    main()
