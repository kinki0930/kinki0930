# -*- coding: utf-8 -*-
"""
preview_stack.py — _layers.pkl → preview SVG.
Panels: (1) top contour overlay, (2) side stepped elevation (raw stack, pre-sand),
(3) front stepped elevation, (4) per-layer thumbnails (multi-region flagged red).
Shows the user the real shape + where appendages detach, BEFORE final DXF.
"""
import os, argparse, pickle, numpy as np

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="project dir containing _layers.pkl")
    a = ap.parse_args()
    d = pickle.load(open(os.path.join(a.out, "_layers.pkl"), "rb"))
    LAY, N, B, allb = d["LAY"], d["N"], d["board"], d["bounds"]
    W = allb[2]-allb[0]; D = allb[3]-allb[1]
    col = lambda k: f"rgb({40+int(k/(N-1)*200)},120,{220-int(k/(N-1)*180)})"
    pad, sc = 14, 2.2
    zsc = sc*2.2
    def poly(pts, extra): return f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}" {extra}/>'
    svg = []

    gx, gy = pad, pad+18
    s = f'<text x="{gx}" y="{gy-4}" font-size="13" fill="#333">1) top: {N} contour layers (blue=bottom to red=top)</text>'
    for lab, Z, regs in LAY:
        k = int(lab)-1
        for r in regs:
            pts = [(gx+(x-allb[0])*sc, gy+(D-(y-allb[1]))*sc) for x, y in r]
            s += poly(pts, f'fill="none" stroke="{col(k)}" stroke-width="1"')
    svg.append(s); topH = D*sc

    ex, ey = pad, gy+topH+40
    s = f'<text x="{ex}" y="{ey-6}" font-size="13" fill="#333">2) side elevation (raw stack; sand to smooth)</text>'
    for lab, Z, regs in LAY:
        k = int(lab)-1
        xs = np.concatenate([r[:, 0] for r in regs]) if regs else np.array([allb[0]])
        z = ey + (N*B - k*B)*zsc
        s += f'<rect x="{ex+(xs.min()-allb[0])*sc:.1f}" y="{z-B*zsc:.1f}" width="{(xs.max()-xs.min())*sc:.1f}" height="{B*zsc:.1f}" fill="{col(k)}" fill-opacity="0.55" stroke="#555" stroke-width="0.4"/>'
    svg.append(s)

    fx = ex + W*sc*0.62
    s = f'<text x="{fx}" y="{ey-6}" font-size="13" fill="#333">3) front elevation</text>'
    for lab, Z, regs in LAY:
        k = int(lab)-1
        ys = np.concatenate([r[:, 1] for r in regs]) if regs else np.array([allb[1]])
        z = ey + (N*B - k*B)*zsc
        s += f'<rect x="{fx+(ys.min()-allb[1])*sc:.1f}" y="{z-B*zsc:.1f}" width="{(ys.max()-ys.min())*sc:.1f}" height="{B*zsc:.1f}" fill="{col(k)}" fill-opacity="0.55" stroke="#555" stroke-width="0.4"/>'
    svg.append(s)

    ty = ey + N*B*zsc + 46
    s = f'<text x="{pad}" y="{ty-8}" font-size="13" fill="#333">4) each layer (red = multi-region / detached appendage)</text>'
    tsc, cols, cw, ch = 0.9, 8, W*0.9+10, D*0.9+22
    for i, (lab, Z, regs) in enumerate(LAY):
        cx = pad+(i % cols)*cw; cy = ty+(i//cols)*ch; multi = len(regs) > 1
        s += f'<text x="{cx}" y="{cy+10}" font-size="10" fill="{"#c0392b" if multi else "#333"}">L{lab}{" *"+str(len(regs)) if multi else ""}</text>'
        for r in regs:
            pts = [(cx+(x-allb[0])*tsc, cy+14+(D-(y-allb[1]))*tsc) for x, y in r]
            s += poly(pts, f'fill="{col(int(lab)-1)}" fill-opacity="0.35" stroke="#333" stroke-width="0.5"')
    svg.append(s)

    TW = W*sc + 2*pad + 20
    TH = ty + (N//8+1)*ch + 20
    open(os.path.join(a.out, "preview.svg"), "w", encoding="utf-8").write(
        f'<svg viewBox="0 0 {TW:.0f} {TH:.0f}" width="{TW:.0f}" xmlns="http://www.w3.org/2000/svg">'
        f'<rect width="{TW:.0f}" height="{TH:.0f}" fill="#faf8f2"/>{"".join(svg)}</svg>')
    print("preview.svg written")

if __name__ == "__main__":
    main()
