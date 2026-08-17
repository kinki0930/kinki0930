---
name: stacked-lasercut
description: >-
  Turn a 3D model (STL/OBJ mesh from Meshy/CAD/scan) into laser-cuttable
  horizontal contour layers that stack + glue + sand into a SOLID wooden object
  — animal figurines, ornaments, product-grade shapes. Produces per-layer DXF
  with square alignment holes, separate appendage pieces (fins/ears/tails/wings),
  optional living-hinge fold parts, a cut preview, and an assembly guide. Use
  this whenever the user wants to laser-cut a 3D shape by STACKING flat layers
  ("分層堆疊", "等高切片", "contour/waterline stacking", "stacked plywood",
  "layered wood", "堆疊雷切"), convert an STL/Meshy/CAD model into DXF for a
  laser cutter, make a solid wooden animal/whale/figurine from a 3D model, or
  asks how to build curved/organic 3D forms out of flat laser-cut sheets. Also
  the reference for choosing a BEND/FOLD method (living hinge vs angled slot vs
  real pivot) on any laser-cut part. Trigger it even if the user only says "I
  have an STL, cut it in wood" or "make this 3D model into layers".
---

# Stacked laser-cut (3D model → contour layers → solid wooden object)

## What this makes and why it works

A laser cutter only cuts flat sheets — it cannot cut a curved board. So an
organic 3D form (a whale, a cat, a figurine) is built by **slicing the model
into many flat horizontal layers, stacking them, gluing, and sanding the steps
smooth**. Sanded, the stack looks like a solid carving. This is the reliable
route to a *product-grade* result, and it is far more dependable than trying to
hand-tune a parametric skeleton by eye — **the shape comes from the user's 3D
file, and this skill does the reliable engineering** (slicing, alignment,
appendages, DXF, assembly).

Key principle to remember and repeat to the user: **curves come from stacking,
not from bending.** Only reach for a bend/fold when a thin appendage must sit at
an angle (see `references/bending-methods.md`).

## Dependencies

Python 3 with `trimesh`, `shapely`, `ezdxf`, `numpy`. See
`references/pipeline-notes.md` for install and environment notes (including this
user's Python path and the Windows `PYTHONUTF8=1` console note).

## The workflow

Do these in order. Confirm the shape with the user (preview) BEFORE producing
final DXF — never jump straight to cut files.

### 1. Inspect the model
Load the STL/OBJ, check it is watertight, and read its extents to decide
orientation. The longest axis is usually the length; the axis you slice along
(the *stacking* axis) is normally the shortest one so you get a sensible layer
count. Report extents and proposed layer count to the user.

### 2. Slice into contour layers
Run `scripts/slice_stack.py`. It scales the model to the target size, slices
along the chosen axis every `board` mm, and for each layer:
- keeps only the **main body region** (the region(s) containing the alignment
  holes) and drops disconnected **islands** (these are appendages — fins, ears —
  saved separately for step 4);
- writes `dxf/L01.dxf … dxf/LNN.dxf` with a layer-number label.

Numbering runs from the bottom of the stack upward (L01 = first-glued layer).

### 3. Alignment holes (critical — get this right)
The slicer places **square** holes (default 3.02 mm) — square, not round, so a
single peg stops a layer from rotating. Strategy, in priority order:
1. Every non-tiny layer must contain **at least one** hole.
2. As many layers as possible contain **two** (full position lock).
3. Holes sit on the centerline and are **spread apart** (one anchor at maximum
   layer coverage, one pushed toward the head/end) — clustered holes leave the
   ends free to wobble, which is the #1 cause of a crooked stack.
Tiny end-cap layers too small to fit a hole are aligned by eye at glue-up.
See `references/pipeline-notes.md` for the full rationale.

**Polar caps** — at the very top and bottom the layers shrink to fiddly slivers
that just get sanded into the dome anyway. Pass `--min-layer-area <mm2>` to drop
those tiny end caps (top/bottom only; interior layers are never removed), leaving
1–2 solid caps you round off by sanding. Choose the threshold from the printed
per-layer areas — enough to remove the specks, not so much that the form goes
flat. Cutting a 9 mm² "layer" is pointless; dropping half the body is not.

### 4. Appendages (fins / ears / tails / wings)
Thin parts that slicing spits out as islands, or that would be fragile as
layers, are made as **separate flat pieces glued on after sanding**. The slicer
exports each dropped island to `dxf/islands/`. Decide per part:
- flat glue-on (simplest);
- **side fins (pectoral)** → `scripts/fin_slot.py`: cuts a notch into one
  layer's left/right edge and makes tabbed fins that insert into that **seam**.
  In a stacked body the layer seams are natural horizontal slots, so this hides
  the joint, self-aligns, and holds far better than surface glue. Preferred for
  side fins/flippers.
- inserted into a slot for a hidden, stronger joint;
- **angled** (e.g. a whale fluke that tilts up) → use `scripts/hinge_appendage.py`
  to make a living-hinge fold part (glue root flat, fold up, lock with a gusset)
  or, if sturdier is wanted, a two-piece angled-slot part. Read
  `references/bending-methods.md` before choosing.

### 5. Preview and confirm
Run `scripts/preview_stack.py` to render an SVG: top contour overlay, side/front
**stepped** elevation (what the raw glued stack looks like before sanding), and
per-layer thumbnails (multi-region layers flagged). For a friendlier check, also
run `scripts/render_stack3d.py` for an **isometric 3D mock-up** (the terraced
stack from two 3/4 angles — closest to how the glued piece will look before
sanding). Show these to the user. If the
shape is wrong, they regenerate the 3D model (e.g. in Meshy) and you re-slice —
the pipeline is unchanged and fast. Do not proceed to a final cut sheet until
they approve the shape.

### 6. Assembly guide
Run `scripts/assembly_guide.py` to produce an HTML guide: stack order, hole
positions, appendage placement, and the step list (cut → thread pegs → glue
bottom-up → clamp → **sand smooth** → attach appendages → oil/finish). The
sanding step is what creates the product feel — always call it out.

## Scripts

| Script | Does | Main args |
|---|---|---|
| `scripts/slice_stack.py` | STL → layer DXFs + square holes + islands + `_layers.pkl` | `--stl --out --size --board --axis --hole --min-layer-area` |
| `scripts/preview_stack.py` | `_layers.pkl` → preview SVG (contours + elevations + thumbnails) | `--out` |
| `scripts/render_stack3d.py` | `_layers.pkl` → isometric 3D mock-up SVG (terraced stack, 2 angles) | `--out` |
| `scripts/assembly_guide.py` | `_layers.pkl` → assembly HTML | `--out` |
| `scripts/fin_slot.py` | side fin as tab-into-seam (notch a layer + PEC-R/L pieces) | `--out --layer --xfrac --tab-w` |
| `scripts/hinge_appendage.py` | living-hinge fold part + gusset (angled appendage, e.g. an up-tilted fluke) | `--out --angle --span` |

All scripts take `--out <project_dir>` and share `_layers.pkl` in it. Run
`python <script> --help` for the full option list. Prefer editing args over
editing the scripts; only edit a script when a genuinely new behavior is needed.

## Decisions to confirm with the user early

- **Target size** (usually total length in mm).
- **Board thickness** (3 mm typical; 2 mm = finer steps, less sanding, more
  layers, more cost).
- **Stacking axis** (default: shortest axis → fewest layers). Slicing along a
  different axis changes the look and layer count.
- **Which appendages are separate** and whether any need to be angled/hinged.
- **Peg size** (default 3 mm square rod → 3.02 mm holes; laser kerf adds the
  clearance).

## Fit and first-cut advice

Holes/slots are drawn at nominal size and rely on **laser kerf** for clearance.
Kerf varies by machine and material, so tell the user to **test-cut one layer +
peg first** and adjust the hole size (±0.1 mm) before cutting the whole set.
