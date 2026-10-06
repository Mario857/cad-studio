"""headphone-desk-clamp: desk-edge C-clamp with a headphone hook, tightened by a screw knob.

Spec: C-clamp profile (XZ plane) extruded BODY_W = 20 mm (slips into a laptop sleeve).
Desk occupies x < 0; spine at x = 0..SPINE_T sits against the desk edge. Upper jaw lies on the
desk top, lower jaw under it carries an M5 heat-set insert; an M5 hex bolt held in a printed knob
pushes a printed pressure pad up against the desk underside. Clamps desks 15-40 mm thick.
Hook arm sticks out from the spine at lower-jaw level (+X) with an upturned lip; headband rests
on it crosswise, ear cups hang either side along the desk edge. Rated load ~400 g headphones.

Hardware: 1x M5 heat-set insert (OD ~7, L <= 9 mm), 1x M5x50 hex-head bolt (head sits in the
knob's hex pocket; glue/press), pad rests loose on the bolt tip (dab of glue optional).
Assumptions: desk edge is square; 2 mm margin above 40 mm desks; PETG for creep resistance
under constant clamp force. Knob and pad are laid out with axes along Y in model coords so that
the shared print orientation (rx=90, body on its side) puts them flat on the bed (3 separate
bodies are intended). Knob hex pocket and pad bolt socket print facing up; flip them to assemble.
Printing on its side makes the C-clamp and hook bending stresses run along the layers.
"""

from build123d import *

from cadlib import *

# Parameters
BODY_W = 20.0      # extrusion thickness (sleeve-flat dimension)
SPINE_T = 10.0     # spine thickness against desk edge
JAW_LEN = 45.0     # jaw reach over the desk
LOW_JAW_T = 14.0   # lower jaw thickness (holds insert)
UP_JAW_T = 9.0     # upper jaw thickness
DESK_MAX = 40.0
DESK_MIN = 15.0
PAD_T = 6.0
PAD_D = 22.0
OPEN = DESK_MAX + PAD_T + 2.0   # gap between jaws
GUSSET = 6.0       # 45 deg inner-corner gussets
HOOK_LEN = 55.0    # hook arm length beyond spine
LIP_T = 6.0
LIP_H = 14.0       # lip height above arm top
BOLT_X = -JAW_LEN / 2 - 2.0
INSERT_DEPTH = 9.0
KNOB_D = 32.0
KNOB_H = 14.0
HEX_POCKET = 4.0   # M5 hex head height ~3.5
EDGE_CH = 0.6

Z1 = LOW_JAW_T
Z2 = Z1 + OPEN
Z3 = Z2 + UP_JAW_T
X_END = SPINE_T + HOOK_LEN

META = dict(
    material="PETG",
    quality="strong",
    standing=False,
    loads=[dict(at=(SPINE_T + HOOK_LEN / 2, 0, Z1), grams=400)],
    print_orientation=(90, 0, 0),  # lying on its side: bending loads run along layers
    supports="auto",
    brim="auto",
)


def z_teardrop(d: float, h: float) -> Part:
    """Hole along +Z from z=0, with a 45 deg point toward +Y (up when printed at rx=90)."""
    import math
    r = d / 2
    pts = [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in range(135, 406, 10)]
    pts.append((0, r * math.sqrt(2)))
    return extrude(Polygon(*pts, align=None), h)


def body() -> Part:
    g = GUSSET
    pts = [
        (-JAW_LEN, 0), (X_END, 0), (X_END, Z1 + LIP_H), (X_END - LIP_T, Z1 + LIP_H),
        (X_END - LIP_T, Z1), (SPINE_T + g, Z1), (SPINE_T, Z1 + g), (SPINE_T, Z3),
        (-JAW_LEN, Z3), (-JAW_LEN, Z2), (-g, Z2), (0, Z2 - g), (0, Z1 + g), (-g, Z1),
        (-JAW_LEN, Z1),
    ]
    prof = Polygon(*pts, align=None)
    p = extrude(Plane.XZ * prof, BODY_W / 2, both=True)
    # chamfer edges of both side faces (bed face on print + sleeve-friendly)
    side_edges = p.faces().sort_by(Axis.Y)[0].edges() + p.faces().sort_by(Axis.Y)[-1].edges()
    p = chamfer(side_edges, EDGE_CH)
    # M5 insert from inside the jaw (top of lower jaw), clearance through the rest.
    # Holes are horizontal when printed on the side -> teardrops pointing model +Y (print up).
    p -= Pos(BOLT_X, 0, Z1 - INSERT_DEPTH) * z_teardrop(METRIC["M5"]["insert_d"], INSERT_DEPTH + 1)
    p -= Pos(BOLT_X, 0, -1) * z_teardrop(hole_d(5.5), Z1 + 2)
    return p


def knob() -> Part:
    k = Cylinder(KNOB_D / 2, KNOB_H, align=ON_BED)
    for i in range(8):
        k -= Rot(0, 0, i * 45) * Pos(KNOB_D / 2 + 1.5, 0, 0) * Cylinder(3.5, KNOB_H, align=ON_BED)
    k = chamfer(k.edges().group_by(Axis.Z)[0], 0.4)
    k = chamfer(k.edges().group_by(Axis.Z)[-1], 1.0)
    # printed pocket-up (no overhang); flip when assembling: bolt head in pocket, shank up
    k -= Pos(0, 0, KNOB_H) * nut_trap("M5", HEX_POCKET)
    k -= Pos(0, 0, KNOB_H) * Cylinder(hole_d(5.5) / 2, KNOB_H, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return k


def pad() -> Part:
    d = Cylinder(PAD_D / 2, PAD_T, align=ON_BED)
    d = chamfer(d.edges().group_by(Axis.Z)[0], 0.4)
    d = chamfer(d.edges().group_by(Axis.Z)[-1], 1.0)
    # printed desk-face down, bolt-tip socket up (no overhang)
    d -= Pos(0, 0, PAD_T) * Cylinder(hole_d(5.2) / 2, 4.0, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return d


def build():
    # knob/pad: local +Z -> model +Y, bases on the y = -BODY_W/2 plane (the print bed)
    lay = Rot(-90, 0, 0)
    y0 = -BODY_W / 2
    k = Pos(-JAW_LEN - KNOB_D / 2 - 8, y0, Z3 / 2) * lay * knob()
    d = Pos(-JAW_LEN - KNOB_D - PAD_D / 2 - 14, y0, Z3 / 2) * lay * pad()
    return [body(), k, d]
