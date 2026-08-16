# Choosing a bend / fold / hinge method for laser-cut parts

Do **not** default to a living hinge for everything. A living hinge in 3 mm
plywood is stiff and crack-prone; it suits a gentle one-time fold, not repeated
motion or sharp angles. Match the method to the situation:

| Situation | Best method | Why / notes |
|---|---|---|
| **Organic overall surface** (animal body, rounded form) | **Stacked contour layers** (this skill's main pipeline) | The curve is built from flat layers + sanding, not bent. This is the primary tool — reach for it first. |
| **Fixed angle between two flat parts** (a fin meeting the body, panels at an angle) | **Angled slot / mitered joint**, or **fold line + locking gusset** | Stronger and cleaner than a living hinge, and it won't crack. Preferred for a fin/fluke that sits at a set angle. |
| **Smooth continuous curve** (wrapping a cylinder, a rounded shell, a curved band) | **Living hinge** (kerf / lattice cuts) | This is the living hinge's real job: thin material, low load, continuous flex. |
| **Part that must move / open repeatedly** (a jaw, flapping wing, a joint) | **Real pivot** — dowel/pin or screw through aligned holes | Plywood living hinges fatigue and snap; don't use them as working hinges. |
| **Thick stock or load-bearing angle** | **Proper joinery** (mortise-tenon, brackets) | Living hinges are too weak to carry load. |

## One-time up-fold appendage (e.g. a whale fluke that tilts up)

Two good options, both let you **glue a flat root first** (easy, strong joint):

1. **Living-hinge fold + gusset** (`scripts/hinge_appendage.py`): one piece =
   flat root + perforated fold line + blade. Glue root flat, fold up to the
   target angle, then glue a small triangular **gusset** into the wedge to lock
   the angle. The gusset — not the hinge — is what makes it rigid.

2. **Two-piece angled slot** (sturdier): the blade is a separate flat piece; cut
   a slot at the target angle into the body/root; insert the blade + glue. No
   fragile hinge bridges. Prefer this if the fold line feels too brittle.

## Living-hinge practical notes (3 mm ply)

- Perforate the fold line (short through-cuts with small uncut bridges); the
  bridges bend. Space them so no single bridge takes all the strain.
- Fold **slowly**; a touch of moisture softens the wood and reduces cracking.
- It is a **one-time** fold to a fixed angle, then locked — not a moving hinge.
- If a smooth curve (not a crease) is wanted, use a **lattice hinge** (staggered
  slit rows) over a band, not a single perforated line.
