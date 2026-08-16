# stacked-lasercut

A Claude skill that turns a 3D model (STL/OBJ from Meshy / CAD / scan) into
**laser-cuttable horizontal contour layers** that stack, glue, and sand into a
**solid wooden object** — animal figurines, ornaments, product-grade shapes.

## What it produces
- `dxf/L01.dxf … LNN.dxf` — body layers, each with square alignment holes + a layer label
- `dxf/islands/` — detached appendage pieces (fins / ears / tails), cut separately
- a cut **preview** (top contours + stepped side/front elevation + per-layer thumbnails)
- an **assembly guide** (stack order, hole map, step-by-step)
- optional **living-hinge fold parts** for angled appendages

## Contents
- `SKILL.md` — the skill (workflow + instructions)
- `scripts/` — `slice_stack.py`, `preview_stack.py`, `assembly_guide.py`, `hinge_appendage.py`
- `references/` — `bending-methods.md` (bend/fold method decision table), `pipeline-notes.md` (env, hole strategy, slicing)

## Requirements
Python 3 with `trimesh`, `shapely`, `ezdxf`, `numpy`:
```
pip install trimesh shapely ezdxf numpy
```

## Quick use
```
python scripts/slice_stack.py --stl model.stl --out project --size 150 --board 3
python scripts/preview_stack.py --out project      # confirm shape before final DXF
python scripts/assembly_guide.py --out project --title "My whale"
python scripts/hinge_appendage.py --out project --angle 22   # optional angled fin
```

Proven on real builds (a stacked cat and a sperm whale). The shape comes from
your 3D file; the skill does the reliable slicing / alignment / DXF / assembly.
Made by AC (台南 AC文創).
