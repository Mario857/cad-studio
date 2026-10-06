"""gutter-light-clips: snap-in Christmas-light clips, gutter-lip hook + under-shingle tongue.

Spec:
- Two variants, both a constant 2D profile (XZ) extruded CLIP_W along Y:
  * GUTTER: inverted-U hook over the front lip of a gutter (gap GUTTER_GAP, inner leg with a
    small grip barb), cable snap ring on the outside of the outer leg.
  * SHINGLE: flat tapered tongue (TONGUE_L x TONGUE_T) that slides up under a shingle, with
    grip teeth on top and a stop step at the shingle butt edge; snap ring hangs in front.
- Snap ring: bore CABLE_BORE holds light-string cable dia 5-8 mm; mouth SNAP_GAP (< 5 mm) with a
  lead-in funnel, faces sideways (+X) so the cable's weight does not pull it out.
- Set of 20: build() returns one of each variant (2 separate bodies is intended), META copies=10.
- Printed lying flat on the profile (rotated 90 deg about X) so hook and snap arms bend
  in-plane, along the layers (strongest), with zero supports.
- Material: ABS+ is OK for one season outside; ASA lasts longer in UV (swap material for
  multi-year use).

Assumptions:
- Gutter front lip (incl. rolled bead) <= 5 mm thick, reachable 14 mm down inside the gutter.
- Shingle tongue 2 mm thick fits under a typical asphalt shingle; 35 mm insertion.
- Cable/wire bundle dia 5-8 mm; snap mouth 4.6 mm (5 mm cable clicks in, 8 mm needs firm push).
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(90, 0, 0),  # profile flat on bed: hook + snap bend along layers
    supports="off",
    brim="auto",
    copies=10,                    # 1 gutter + 1 shingle per set x10 = 20 clips
)

# Parameters
CLIP_W = 10.0          # extrusion width (Y) of both clips
WALL = 2.5             # hook/leg wall thickness
# snap ring
CABLE_MAX = 8.0        # largest cable dia
CABLE_CLEAR = 0.4      # bore clearance over largest cable
CABLE_BORE = CABLE_MAX + CABLE_CLEAR
RING_T = 1.8           # ring wall (flexes to admit cable)
SNAP_GAP = 4.6         # mouth width (< smallest 5 mm cable -> snaps)
LEAD_IN = 1.2          # funnel widening per side at mouth
# gutter hook
GUTTER_GAP = 5.0       # lip clearance inside the U
INNER_DROP = 14.0      # inner leg length below the top
OUTER_DROP = 22.0      # outer leg length below the top
BARB = 0.8             # grip barb on inner leg tip
# shingle tongue
TONGUE_L = 35.0
TONGUE_T = 2.0
TONGUE_TIP = 0.8       # tapered tip thickness
STOP_H = 3.0           # step at shingle butt edge
STOP_W = 3.0
TOOTH_H = 0.6
TOOTH_PITCH = 6.0
N_TEETH = 3
EDGE_CHAMFER = 0.4     # elephant-foot chamfer on bed face (print orientation)
SET_GAP_X = 55.0       # X offset of shingle clip on the plate (no overlap with gutter clip)

R_IN = CABLE_BORE / 2
R_OUT = R_IN + RING_T


def snap_ring(xc: float, zc: float) -> Face:
    """2D snap ring in XZ (local x=X, y=Z), mouth with lead-in facing +X."""
    ring = Pos(xc, zc) * Circle(R_OUT) - Pos(xc, zc) * Circle(R_IN)
    g = SNAP_GAP / 2
    mouth = Polygon(
        (xc, zc - g), (xc + R_IN, zc - g), (xc + R_OUT + 0.5, zc - g - LEAD_IN),
        (xc + R_OUT + 0.5, zc + g + LEAD_IN), (xc + R_IN, zc + g), (xc, zc + g),
        align=None,
    )
    return ring - mouth


def finish(profile: Face) -> Part:
    part = extrude(Plane.XZ * profile, CLIP_W / 2, both=True)
    for face in (part.faces().sort_by(Axis.Y)[0], part.faces().sort_by(Axis.Y)[-1]):
        try:
            part = chamfer(face.edges(), EDGE_CHAMFER)
        except Exception:
            pass
    return part


def gutter_clip() -> Part:
    top = INNER_DROP + 2 * R_OUT + 4  # keep everything above z=0
    g = GUTTER_GAP / 2
    bridge = Pos(0, top - WALL / 2) * Rectangle(GUTTER_GAP + 2 * WALL, WALL)
    inner = Pos(-g - WALL / 2, top - INNER_DROP / 2) * Rectangle(WALL, INNER_DROP)
    barb = Polygon(
        (-g, top - INNER_DROP), (-g + BARB, top - INNER_DROP + 1.0), (-g, top - INNER_DROP + 3.0),
        align=None,
    )
    outer_bot = top - OUTER_DROP
    outer = Pos(g + WALL / 2, top - OUTER_DROP / 2) * Rectangle(WALL, OUTER_DROP)
    xc = g + WALL + R_IN
    zc = outer_bot + R_OUT
    ring = snap_ring(xc, zc)
    prof = bridge + inner + barb + outer + ring
    return finish(prof)


def shingle_clip() -> Part:
    zt = 2 * R_OUT + 2.0  # tongue underside height
    tongue = Polygon(
        (-TONGUE_L, zt), (STOP_W, zt), (STOP_W, zt + TONGUE_T + STOP_H),
        (0, zt + TONGUE_T + STOP_H), (0, zt + TONGUE_T), (-TONGUE_L + 8, zt + TONGUE_T),
        (-TONGUE_L, zt + TONGUE_TIP),
        align=None,
    )
    teeth = None
    for i in range(N_TEETH):
        x0 = -6.0 - i * TOOTH_PITCH
        t = Polygon((x0 - 2.5, zt + TONGUE_T), (x0, zt + TONGUE_T),
                    (x0, zt + TONGUE_T + TOOTH_H), align=None)
        teeth = t if teeth is None else teeth + t
    # hanger web from tongue front down to the ring
    xc = STOP_W - R_OUT
    zc = R_OUT
    web = Polygon(
        (xc - R_OUT, zc), (xc - R_OUT + WALL, zc), (STOP_W, zt), (STOP_W - WALL - 2, zt),
        align=None,
    )
    ring = snap_ring(xc, zc)
    prof = tongue + teeth + web + ring
    return finish(prof)


def build():
    g = gutter_clip()
    s = Pos(SET_GAP_X, 0, 0) * shingle_clip()
    return [g, s]
