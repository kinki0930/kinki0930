# -*- coding: utf-8 -*-
"""
render_stack3d.py — _layers.pkl → isometric 3D mock-up of the glued stack.
Shows the terraced result (pre-sanding). Two 3/4 angles. --out project dir.
"""
import os, argparse, pickle, math, numpy as np

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="")
    a = ap.parse_args()
    d = pickle.load(open(os.path.join(a.out, "_layers.pkl"), "rb"))
    LAY, B, allb = d["LAY"], d["board"], d["bounds"]
    cx = 0.5*(allb[0]+allb[2]); cy = 0.5*(allb[1]+allb[3])
    N = len(LAY)

    def proj(x, y, z, az, el):
        X = x-cx; Y = y-cy; Z = z
        x1 = X*math.cos(az)-Y*math.sin(az); y1 = X*math.sin(az)+Y*math.cos(az)
        y2 = y1*math.cos(el)+Z*math.sin(el); z2 = -y1*math.sin(el)+Z*math.cos(el)
        return x1, -z2, y2

    def wood(k):  # bottom darker -> top lighter
        t = k/(N-1); r = int(150+t*70); g = int(110+t*60); b = int(70+t*45)
        return f"rgb({r},{g},{b})"

    def panel(azd, eld, PW, PH, label):
        az, el = math.radians(azd), math.radians(eld)
        pts_all = []
        prj = []
        for lab, Zt, regs in LAY:
            k = int(lab)-1; z = k*B
            layer = []
            for r in regs:
                pp = [proj(x, y, z, az, el) for x, y in r]
                layer.append(pp); pts_all += pp
            prj.append((k, layer))
        xs = [p[0] for p in pts_all]; ys = [p[1] for p in pts_all]
        mnx, mxx, mny, mxy = min(xs), max(xs), min(ys), max(ys)
        m = 22; sc = min((PW-2*m)/(mxx-mnx), (PH-2*m-16)/(mxy-mny))
        ox = m-mnx*sc+((PW-2*m)-(mxx-mnx)*sc)/2; oy = m+16-mny*sc+((PH-2*m-16)-(mxy-mny)*sc)/2
        X = lambda p: p[0]*sc+ox; Y = lambda p: p[1]*sc+oy
        s = f'<rect width="{PW}" height="{PH}" fill="#141013"/><text x="12" y="16" fill="#c9b79a" font-size="13" font-family="sans-serif">{label}</text>'
        for k, layer in prj:                       # bottom -> top (higher occludes lower)
            for pp in layer:
                s += f'<polygon points="{" ".join(f"{X(p):.1f},{Y(p):.1f}" for p in pp)}" fill="{wood(k)}" stroke="#3a2c1e" stroke-width="0.5"/>'
        return s

    PW, PH, G = 460, 420, 10
    views = [(40, 24, "front 3/4"), (145, 22, "back 3/4")]
    body = ""
    for i, (az, el, lb) in enumerate(views):
        body += f'<g transform="translate({i*(PW+G)},0)">{panel(az,el,PW,PH,lb)}</g>'
    W = 2*PW+G; H = PH
    open(os.path.join(a.out, "render3d.svg"), "w", encoding="utf-8").write(
        f'<svg viewBox="0 0 {W} {H}" width="{W}" xmlns="http://www.w3.org/2000/svg">'
        f'<rect width="{W}" height="{H}" fill="#0c0a0c"/>{body}</svg>')
    print("render3d.svg written")

if __name__ == "__main__":
    main()
