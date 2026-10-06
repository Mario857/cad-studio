"""tie-belt-rack: closet-rod hanger with 10 tie bars and 6 belt hooks.

Spec:
- Flat "hanger" profile in the XZ plane, THICK mm deep in Y. Hangs like a clothes hanger:
  the closet rod runs along Y through an inverted-J hook (ID HOOK_ID, fits 25-35 mm rods,
  side opening > 35 mm with a small anti-slip lip).
- Central spine with 5 levels of cantilevered tie arms on each side (10 tie bars),
  each with an upturned end lip so ties don't slide off; ties slide on from the free ends.
- Bottom belt bar with 6 J-cup hooks. The buckle's frame bar rests in the cup (throat
  BELT_THROAT) so the buckle hangs in the YZ plane; its width (up to 50 mm) runs along Y,
  clear of the 10 mm thick rack, so neighbouring hooks at BELT_PITCH never collide.
- Design load 2 kg total (ties + belts). Printed lying flat (Y down) so every arm, hook
  and the rod hook are loaded along the layers, not across them; no supports needed.

Assumptions:
- Rod diameter 25-35 mm; rod hook ID 40 mm gives clearance for 35 mm rods incl. wraps.
- Ties ~100 g each, belts ~170 g each, total ~2 kg.
- Buckle frame bar + strap thickness <= 10 mm (throat 12 mm); buckle opening admits
  a 6 x 10 mm prong.
- Footprint ~196 x 260 mm, kept inside the H2C single-nozzle printable area (a 224 x 300 version failed slicing as "unprintable area of multi-extruder printers").
Hardware: none.
"""

import math

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,            # hangs from a rod
    loads=[                    # ~2 kg total in use
        *[dict(at=(sx * 55, 0, z), grams=100) for sx in (-1, 1)
          for z in (186, 158, 130, 102, 74)],
        *[dict(at=(-85 + 34 * i, 0, 5), grams=170) for i in range(6)],
    ],
    print_orientation=(90, 0, 0),  # lie flat: hook/arm loads run along layers
    supports="off",
    brim="auto",
)

# Parameters
THICK = 10.0            # rack depth (Y), = layer stack when printed
TOTAL_H = 260.0

# rod hook
HOOK_ID = 40.0          # inner diameter, fits 25-35 mm rods
HOOK_WALL = 9.0         # radial wall
HOOK_LIP_DEG = 15.0     # tip extends this far below horizontal
HOOK_STEM_LEN = 20.0    # straight stem from hook circle down to the neck

# spine + tie arms
SPINE_W = 16.0
TOP_Z = 190.0           # top of uppermost tie arm / shoulder
ARM_N = 5               # levels (x2 sides = 10 tie bars)
ARM_PITCH = 28.0
ARM_LEN = 90.0          # from spine face
ARM_T = 8.0             # arm height (Z)
ARM_LIP_H = 8.0         # upturned end lip
ARM_LIP_W = 6.0
ARM_GUSSET = 14.0

# belt bar + hooks
BELT_N = 6
BELT_PITCH = 34.0
BELT_BAR_Z = 36.0       # bottom of belt bar
BELT_BAR_T = 10.0
BELT_STEM_W = 6.0
BELT_CUP_T = 6.0        # cup floor thickness
BELT_THROAT = 12.0      # gap between stem and lip
BELT_LIP_H = 12.0       # lip height above cup floor
BELT_LIP_W = 6.0
EDGE_CHAMFER = 0.5


def _rect(x0, z0, x1, z1):
    return Pos((x0 + x1) / 2, (z0 + z1) / 2) * Rectangle(abs(x1 - x0), abs(z1 - z0))


def profile() -> Sketch:
    r_in = HOOK_ID / 2
    r_out = r_in + HOOK_WALL
    r_mid = (r_in + r_out) / 2
    cz = TOTAL_H - r_out
    half_w = SPINE_W / 2 + ARM_LEN

    # rod hook: annulus keeping angles -LIP..180 deg, rounded tip
    ring = Pos(0, cz) * (Circle(r_out) - Circle(r_in))
    t = math.tan(math.radians(HOOK_LIP_DEG))
    wedge = Pos(0, cz) * Polygon((0, 0), (-50, 0), (-50, -50), (50, -50), (50, -50 * t), align=None)
    a = math.radians(-HOOK_LIP_DEG)
    tip = Pos(r_mid * math.cos(a), cz + r_mid * math.sin(a)) * Circle(HOOK_WALL / 2)
    s = ring - wedge + tip
    # stem + neck gusset down to the shoulder
    stem_bot = cz - HOOK_STEM_LEN
    s += _rect(-r_out, TOP_Z - ARM_T, -r_in, cz)
    s += Polygon((-r_in, stem_bot), (-r_in, TOP_Z), (SPINE_W / 2 + 4, TOP_Z), align=None)

    # spine
    s += _rect(-SPINE_W / 2, BELT_BAR_Z, SPINE_W / 2, TOP_Z)

    # tie arms
    for i in range(ARM_N):
        zt = TOP_Z - i * ARM_PITCH
        s += _rect(-half_w, zt - ARM_T, half_w, zt)
        for sx in (-1, 1):
            s += _rect(sx * half_w, zt, sx * (half_w - ARM_LIP_W), zt + ARM_LIP_H)
            x0 = sx * SPINE_W / 2
            zb = zt - ARM_T
            s += Polygon((x0, zb), (x0 + sx * ARM_GUSSET, zb), (x0, zb - ARM_GUSSET), align=None)

    # belt bar + J-cups
    span = (BELT_N - 1) * BELT_PITCH
    cup_w = BELT_STEM_W + BELT_THROAT + BELT_LIP_W
    x_l = -span / 2 - cup_w / 2
    x_r = span / 2 + cup_w / 2
    s += _rect(x_l, BELT_BAR_Z, x_r, BELT_BAR_Z + BELT_BAR_T)
    # gussets spine <-> belt bar
    for sx in (-1, 1):
        x0 = sx * SPINE_W / 2
        z0 = BELT_BAR_Z + BELT_BAR_T
        s += Polygon((x0, z0), (x0 + sx * ARM_GUSSET, z0), (x0, z0 + ARM_GUSSET), align=None)
    for i in range(BELT_N):
        xs = -span / 2 + i * BELT_PITCH - cup_w / 2   # stem left edge
        s += _rect(xs, 0, xs + BELT_STEM_W, BELT_BAR_Z)
        s += _rect(xs, 0, xs + cup_w, BELT_CUP_T)
        s += _rect(xs + cup_w - BELT_LIP_W, 0, xs + cup_w, BELT_CUP_T + BELT_LIP_H)
    return s


def build() -> Part:
    part = extrude(Plane.XZ * profile(), THICK / 2, both=True)
    try:
        faces = part.faces().filter_by(Axis.Y)
        part = chamfer(faces.edges(), EDGE_CHAMFER)
    except Exception:
        pass
    return part
