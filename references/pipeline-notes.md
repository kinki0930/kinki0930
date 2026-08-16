# Pipeline notes — environment, hole strategy, slicing, appendages

## Environment / dependencies

- Python 3 with `trimesh`, `shapely`, `ezdxf`, `numpy`:
  `pip install trimesh shapely ezdxf numpy`
- This user's machine (Windows): call Python by full path to avoid the Store
  stub, and set UTF-8 for a cp950 console:
  `PYTHONUTF8=1 "C:/Users/88691/AppData/Local/Programs/Python/Python312/python.exe" script.py ...`
- trimesh 5.x: use `path.to_2D()` (`to_planar` is deprecated). The scripts
  already do; it may print a DeprecationWarning on older paths — harmless.
- Proven on real builds: `cat_lasercut/` (side-slice stack) and `whale_stack/`
  (horizontal contour stack). This skill generalizes those.

## Getting the 3D model

The shape comes from the user's mesh, not from hand-tuned parametric geometry.
Good sources: **Meshy** (image/text → 3D — the user has used it), Sketchfab /
CGTrader / Thingiverse downloads, or CAD (Fusion/Blender). If the shape is
wrong, the user regenerates the mesh and you re-slice — do not try to fix a bad
shape by editing layer outlines by hand.

## Why square alignment holes, spread out

- **Square** (not round): a single square peg stops a layer from **rotating**.
  Round holes let a one-peg layer spin — the usual cause of a crooked stack.
- **Spread apart**, on the centerline: one **anchor** hole at the position that
  lies inside the most layers (covers the mid/belly slices), one pushed toward
  the head/end. Clustered holes leave the ends unconstrained and wobbly.
- **Coverage goal**: every non-tiny layer contains at least one hole; as many as
  possible contain two (full position + rotation lock). Tiny end-cap layers too
  small to fit a hole (need ~ hole + 2×wall of width) are aligned by eye.
- Holes are drawn at **nominal** size (default 3.02 mm for a 3 mm square rod);
  **laser kerf supplies the clearance**. Kerf varies, so always test-cut one
  layer + peg and adjust ±0.1 mm before cutting the full set.

## Slicing axis and layer count

- Slice **perpendicular to the stacking direction**. For a figure resting on its
  base, stack vertically → slice horizontally (constant-Z), the default.
- Pick the stacking axis so the layer count is sensible — usually the model's
  **shortest** axis. Length/3 mm = far too many layers; height/3 mm ≈ 15–25 is
  typical.
- Thinner board (2 mm) → smaller steps, less sanding, finer result, but more
  layers and more material/time. 3 mm is the usual default.

## Appendages (islands)

Horizontal slicing naturally captures flat appendages that lie in the slice
plane (a horizontal fluke shows up in the mid layers). Thin appendages at an
angle to the slice plane come out as **disconnected islands** in a few layers.
The slicer keeps only the main body per layer and exports islands to
`dxf/islands/`. Make those as **separate glue-on pieces after sanding**:
- flat glue-on, or into a slot (hidden, stronger), or
- angled → `scripts/hinge_appendage.py` (see `bending-methods.md`).

## Typical command sequence

```
PY=".../python.exe"; OUT="C:/.../myproject"
PYTHONUTF8=1 "$PY" scripts/slice_stack.py --stl model.stl --out "$OUT" --size 150 --board 3
PYTHONUTF8=1 "$PY" scripts/preview_stack.py --out "$OUT"      # show, get shape sign-off
PYTHONUTF8=1 "$PY" scripts/assembly_guide.py --out "$OUT" --title "My whale"
PYTHONUTF8=1 "$PY" scripts/hinge_appendage.py --out "$OUT" --angle 22   # if an angled fin is needed
```
