# -*- coding: utf-8 -*-
"""
hinge_appendage.py — living-hinge fold appendage (e.g. a whale fluke that tilts up).
One flat piece = flat root (glue down) + perforated fold line (living hinge) + blade,
plus 2 angle-lock gussets. Glue root flat, fold up along the red line, glue gussets
to lock the angle. Read references/bending-methods.md before choosing this vs an
angled-slot two-piece (sturdier) or a real pivot (for moving parts).

Default blade is a crescent (fluke). Replace `blade` below for other shapes, or
pass --blade-dxf to load an outline. Outputs <name>.dxf + <name>_diagram.svg.
"""
import os, argparse, math, numpy as np, ezdxf

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", default="fluke_hinged")
    ap.add_argument("--angle", type=float, default=22.0, help="fold-up angle (deg)")
    ap.add_argument("--tongue-w", type=float, default=8.0, help="glue-root tongue width mm")
    ap.add_argument("--tongue-l", type=float, default=12.0, help="glue-root tongue length mm")
    ap.add_argument("--span", type=float, default=28.0, help="blade half-span mm")
    a = ap.parse_args()
    DXF = os.path.join(a.out, "dxf"); os.makedirs(DXF, exist_ok=True)
    TW, TL, S = a.tongue_w, a.tongue_l, a.span/28.0

    blade = [(0, 11), (7, 15), (16, 25), (23, 27), (20, 18), (14, 9), (10, 3), (8, 0),
             (10, -3), (14, -9), (20, -18), (23, -27), (16, -25), (7, -15), (0, -11)]
    blade = [(x*S, y*S) for x, y in blade]
    outline = [(-TL, TW/2), (0, TW/2), (0, 11*S)] + blade[1:] + [(0, -TW/2), (-TL, -TW/2)]

    def perfs(xf=1.0, y0=-10*S, y1=10*S, seg=2.6, gap=1.6):
        res, y = [], y0
        while y < y1:
            res.append([(xf, y), (xf, min(y+seg, y1))]); y += seg+gap
        return res
    PERF = perfs()
    GL = 20.0; GH = GL*math.tan(math.radians(a.angle)); gusset = [(0, 0), (GL, 0), (GL, GH)]

    doc = ezdxf.new(); doc.units = ezdxf.units.MM; msp = doc.modelspace()
    doc.layers.add("CUT", color=7); doc.layers.add("HINGE", color=1); doc.layers.add("LABEL", color=3)
    msp.add_lwpolyline(outline, close=True, dxfattribs={"layer": "CUT"})
    for s in PERF: msp.add_line(s[0], s[1], dxfattribs={"layer": "HINGE"})
    msp.add_text("root=glue flat | red=fold line", height=2.5, dxfattribs={"layer": "LABEL"}).set_placement((-TL, -30*S))
    ox = 40
    for i in range(2):
        msp.add_lwpolyline([(x+ox, y-20) for x, y in gusset], close=True, dxfattribs={"layer": "CUT"})
        msp.add_text(f"GUSSET {a.angle:.0f}deg", height=2.5, dxfattribs={"layer": "LABEL"}).set_placement((ox, -24)); ox += GL+8
    doc.saveas(os.path.join(DXF, f"{a.name}.dxf"))

    sc = 3.4
    def P(pts, off, fill): return f'<polygon points="{" ".join(f"{(x+off[0])*sc:.1f},{(off[1]-y)*sc:.1f}" for x,y in pts)}" fill="{fill}" stroke="#333" stroke-width="0.6"/>'
    o1 = (TL+6, 150)
    svg = f'<rect width="720" height="460" fill="#faf8f2"/><text x="14" y="22" font-size="15" fill="#222">Living-hinge appendage: cut flat -> glue root flat -> fold {a.angle:.0f}deg -> lock with gussets</text>'
    svg += P(outline, o1, "#d8c39a")
    for s in PERF:
        svg += f'<line x1="{(s[0][0]+o1[0])*sc:.1f}" y1="{(o1[1]-s[0][1])*sc:.1f}" x2="{(s[1][0]+o1[0])*sc:.1f}" y2="{(o1[1]-s[1][1])*sc:.1f}" stroke="#c0392b" stroke-width="1.4"/>'
    bx, by, L = 470, 340, 70; ang = math.radians(a.angle); tip = (bx+L*math.cos(ang), by-L*math.sin(ang))
    svg += f'<text x="{bx-60}" y="120" font-size="13" fill="#222">folded side view</text>'
    svg += f'<rect x="{bx-90}" y="{by-6}" width="120" height="10" fill="#c9a163" stroke="#7d6231"/>'
    svg += f'<line x1="{bx}" y1="{by}" x2="{tip[0]:.1f}" y2="{tip[1]:.1f}" stroke="#7d6231" stroke-width="6"/>'
    svg += f'<polygon points="{bx},{by} {bx+GL*1.4:.1f},{by} {bx+GL*1.4:.1f},{by-GH*1.4:.1f}" fill="#8fbf6a" fill-opacity="0.6" stroke="#4a7a2a"/>'
    svg += f'<text x="{bx+16}" y="{by-8}" font-size="11" fill="#2a6">gusset locks {a.angle:.0f}deg</text>'
    open(os.path.join(a.out, f"{a.name}_diagram.svg"), "w", encoding="utf-8").write(f'<svg viewBox="0 0 720 460" width="720" xmlns="http://www.w3.org/2000/svg">{svg}</svg>')
    print(f"done: dxf/{a.name}.dxf + {a.name}_diagram.svg  (angle {a.angle:.0f}deg)")

if __name__ == "__main__":
    main()
