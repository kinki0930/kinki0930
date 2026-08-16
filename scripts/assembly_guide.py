# -*- coding: utf-8 -*-
"""
assembly_guide.py — _layers.pkl → assembly HTML (stack order, square holes, steps).
Generic across models; appendages are described as separate glue-on pieces.
"""
import os, argparse, pickle, numpy as np

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="Stacked laser-cut model")
    ap.add_argument("--peg", default="3mm square rod")
    a = ap.parse_args()
    d = pickle.load(open(os.path.join(a.out, "_layers.pkl"), "rb"))
    LAY, N, B, allb, HOLES, HS = d["LAY"], d["N"], d["board"], d["bounds"], d["holes"], d["hole"]
    X0, Y0, X1, Y1 = allb; W = X1-X0; D = Y1-Y0
    def xr(regs):
        xs = np.concatenate([r[:, 0] for r in regs]) if regs else np.array([X0]); return xs.min(), xs.max()
    col = lambda k: f"rgb({40+int(k/(N-1)*200)},120,{220-int(k/(N-1)*180)})"
    sc = 2.6; B_sc = B*sc*2.4; pad = 16

    Aw, Ah = W*sc+120, N*B_sc+50
    A = f'<text x="0" y="14" font-size="13" fill="#222">Stack order: L01 (bottom) to L{N:02d} (top), threaded on 2x {a.peg}</text>'
    for lab, Z, regs in LAY:
        xmin, xmax = xr(regs); k = int(lab)-1; y = Ah-20-k*B_sc
        A += f'<rect x="{40+(xmin-X0)*sc:.1f}" y="{y-B_sc:.1f}" width="{(xmax-xmin)*sc:.1f}" height="{B_sc-1:.1f}" fill="{col(k)}" fill-opacity="0.6" stroke="#555" stroke-width="0.5"/>'
        A += f'<text x="6" y="{y-B_sc/2+3:.1f}" font-size="10" fill="#333">L{lab}</text>'
    for (u, v) in HOLES:
        A += f'<line x1="{40+(u-X0)*sc:.1f}" y1="10" x2="{40+(u-X0)*sc:.1f}" y2="{Ah-20:.1f}" stroke="#c0392b" stroke-width="1.5" stroke-dasharray="4 3"/>'

    big = max(LAY, key=lambda t: sum(len(r) for r in t[2]))[2]
    Bw, Bh = W*sc+40, D*sc+50
    Bx = f'<text x="0" y="14" font-size="13" fill="#222">Alignment holes ({HS}mm SQUARE, same spot every layer)</text>'
    for r in big:
        pts = " ".join(f"{20+(x-X0)*sc:.1f},{20+(D-(y-Y0))*sc:.1f}" for x, y in r)
        Bx += f'<polygon points="{pts}" fill="#e8dcc0" stroke="#7d6231" stroke-width="1"/>'
    h = HS/2*sc
    for (u, v) in HOLES:
        Bx += f'<rect x="{20+(u-X0)*sc-h:.1f}" y="{20+(D-(v-Y0))*sc-h:.1f}" width="{2*h:.1f}" height="{2*h:.1f}" fill="none" stroke="#c0392b" stroke-width="1.5"/>'

    html = f"""<!doctype html><meta charset="utf-8"><title>{a.title} - assembly</title>
<style>body{{font:14px/1.6 "Noto Sans TC",sans-serif;margin:22px;color:#222;max-width:900px}}
h1{{font-size:20px;margin:0}}h2{{font-size:15px;margin:18px 0 6px;border-left:4px solid #c9a06a;padding-left:8px}}
.meta{{color:#666}}table{{border-collapse:collapse;font-size:13px}}td,th{{border:1px solid #ddd;padding:3px 9px}}th{{background:#f0ead9}}
.warn{{background:#fff4e5;border:1px solid #f0c674;padding:10px 12px;border-radius:6px}}
.row{{display:flex;gap:24px;flex-wrap:wrap;align-items:flex-start}}svg{{background:#fff;border:1px solid #eee}}
code{{background:#f3f0e8;padding:1px 5px;border-radius:4px}}ol li{{margin:5px 0}}</style>
<h1>{a.title}</h1>
<div class="meta">{N} body layers (L01-L{N:02d}, {B}mm) + appendages - laser-cut, stacked, sanded</div>
<h2>Parts</h2>
<table><tr><th>part</th><th>qty</th><th>file</th></tr>
<tr><td>body layers</td><td>{N}</td><td>dxf/L01.dxf ... L{N:02d}.dxf (each with square holes + label)</td></tr>
<tr><td>appendages (fins/ears/tails)</td><td>as needed</td><td>dxf/islands/ + any hinge parts</td></tr>
<tr><td>alignment pegs ({a.peg})</td><td>2</td><td>separate</td></tr></table>
<h2>1) Stack order &nbsp; 2) Alignment holes</h2>
<div class="row">
<svg viewBox="0 0 {Aw:.0f} {Ah:.0f}" width="{min(Aw,520):.0f}">{A}</svg>
<svg viewBox="0 0 {Bw:.0f} {Bh:.0f}" width="{min(Bw,360):.0f}">{Bx}</svg>
</div>
<h2>Steps</h2>
<ol>
<li><b>Cut</b> L01-L{N:02d} + appendages (and test-cut one layer + peg first to check hole fit).</li>
<li><b>Thread</b> 2 pegs into the bottom layer <code>L01</code>'s holes.</li>
<li><b>Stack bottom-up</b> L01 to L{N:02d}, gluing between each layer. Square holes keep every layer from rotating.</li>
<li><b>Clamp</b>, wipe squeeze-out, let cure.</li>
<li><b>Sand</b> the steps smooth (coarse to fine) - this creates the solid, product look.</li>
<li><b>Attach appendages</b> after sanding (glue flat / into slot / fold-and-lock for angled parts).</li>
<li><b>Finish</b> with oil or lacquer.</li>
</ol>
<div class="warn">The pegs are for <b>alignment during glue-up</b> - align every layer on them before the glue grabs. Tiny end-cap layers with no hole are aligned by eye. Attach appendages after sanding so they don't get sanded away.</div>
"""
    open(os.path.join(a.out, "assembly.html"), "w", encoding="utf-8").write(html)
    print("assembly.html written")

if __name__ == "__main__":
    main()
