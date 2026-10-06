"""rain-gauge: Ø100 funnel rain gauge with a scaled holder for a clear tube, spike or post mount.

Spec (3 printed parts + a clear tube):
- Funnel: Ø100 mm catch rim (sharp inner edge, 15 mm splash wall), 50° cone to a spout that
  drops into the measuring tube, and a skirt that slips over the holder collar.
- Holder: base socket that the clear tube is sealed into, 4 rails up to a top collar, the front
  rail carries the scale; a back flange with 2 countersunk holes for post mounting; a square
  mortise underneath for the spike.
- Spike: 200 mm ground spike (T-section blade) with a square tenon, bolted into the base.

Area-ratio maths: rain depth h_rain falls on the catch area A_f = π (D_f/2)²; all of it ends
up in the tube of inner area A_t = π (D_t/2)², so the water column is
    h_col = h_rain · A_f / A_t = h_rain · (D_f / D_t)².
With D_f = 100 and D_t = 44.72 mm, (D_f / D_t)² = 5.00: every 1 mm of rain raises the column
5 mm. The scale therefore has a raised mark every 5 mm of height (= 1 mm of rain) and a number
every 10 mm of height (= every 2 mm of rain: 2, 4 ... 40). Marks are placed at
z = Z_ZERO + n · (FUNNEL_D / TUBE_ID)², so a different tube only needs TUBE_ID changed.
Zero is the floor of the base bore, which has the tube's inner diameter below the ledge the tube
sits on, so the column area is constant from zero up.

Printed in print poses (holder upright, funnel rim-down, spike lying flat for strength), so model
coordinates are print poses. No supports.
Material: AzureFilm ABS PLUS. ABS+ yellows/embrittles after a season or two in full sun; the
user's "AzureFilm ASA @BBL H2C 0.4 nozzle" preset is the long-life swap (same geometry).

Assumptions:
- Clear tube (acrylic/PC/PETG) OD 48 x ID 44.7 mm, 210 mm long, open both ends; its bottom is
  sealed onto the base ledge with silicone (that seal is the gauge floor).
- Funnel spout and skirt are slide fits (0.25 mm); tube socket/collar slide fit + sealant.
- Spike: M4 x 30 bolt + nut through base and tenon. Post mount: 2 x 4 mm countersunk wood
  screws through the back flange (leave the spike off).
- Capacity ≈ 40 mm of rain; empty after reading.
- Audit notes: 3 bodies (holder, funnel, spike) is intended; the ~0.8 cm² "needs support" is the
  0.65 mm undersides of the raised scale numbers on the vertical rail (~4 mm² each), which
  print fine as tiny overhangs. Tick marks have 45° undersides.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),   # parts already in print poses
    supports="off",
    brim="auto",
    copies=1,
)

# Optics / scale
FUNNEL_D = 100.0
TUBE_OD = 48.0
TUBE_ID = 44.72
TUBE_LEN = 210.0
RATIO = (FUNNEL_D / TUBE_ID) ** 2
MARK_EVERY = 1         # rain mm per mark
NUMBER_EVERY = 2       # rain mm per number
MAX_RAIN = 40
LABEL_SIZE = 7.5       # digit height ~5.3 mm
FIT_SLIDE = FIT["slide"]

# Holder
PLINTH_D = 60.0
PLINTH_H = 25.0
LEDGE_H = 3.0
SOCKET_DEPTH = 12.0
SOCKET_WALL = 3.0
RAIL_T = 5.0
RAIL_W = 12.0
SCALE_RAIL_W = 18.0
COLLAR_H = 8.0
FLANGE_W = 92.0
FLANGE_T = 5.0
POST_SCREW_D = 4.0
TENON = 15.0
TENON_LEN = 15.0
BOLT = "M4"

# Funnel
FUNNEL_WALL = 2.4
FUNNEL_PITCH = 50.0
SPLASH_WALL_H = 15.0
SPOUT_OD = 20.0
SPOUT_ID = 14.0
SPOUT_LEN = 15.0
SKIRT_LEN = 8.0

# Spike
SPIKE_LEN = 200.0
BLADE_W = 30.0
BLADE_T = 6.0
SPIKE_RIB = 6.0

Z_ZERO = PLINTH_H
SOCK_R = TUBE_OD / 2 + FIT_SLIDE
OUT_R = SOCK_R + SOCKET_WALL
Z_TUBE = Z_ZERO + LEDGE_H
Z_TOP = Z_TUBE + TUBE_LEN


def holder() -> Part:
    part = Cylinder(PLINTH_D / 2, PLINTH_H, align=ON_BED)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    part += Pos(0, 0, PLINTH_H - 1) * Cylinder(OUT_R, LEDGE_H + SOCKET_DEPTH + 1, align=ON_BED)
    zc = Z_TOP - COLLAR_H
    collar = Polygon((SOCK_R - 0.5, zc - SOCKET_WALL - 0.5), (OUT_R, zc), (OUT_R, Z_TOP), (SOCK_R - 0.5, Z_TOP),
                     align=None)                      # 45° underside
    part += revolve(Plane.XZ * collar, Axis.Z)
    # rails (back, two sides, front scale rail)
    z0 = Z_TUBE + SOCKET_DEPTH - 2
    h = Z_TOP - COLLAR_H + 2 - z0
    for a, w in ((90, RAIL_W), (210, RAIL_W), (330, RAIL_W), (270, SCALE_RAIL_W)):
        zs = PLINTH_H - 1                                 # rails stand on the plinth (no overhang)
        part += Rot(0, 0, a) * Pos(SOCK_R - 0.3 + RAIL_T / 2, 0, zs) * Box(RAIL_T, w, h + z0 - zs, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # bores: tube-ID bore below the ledge, tube socket above, collar bore
    part -= Pos(0, 0, Z_ZERO) * Cylinder(TUBE_ID / 2, LEDGE_H + 0.01, align=ON_BED)
    part -= Pos(0, 0, Z_TUBE) * Cylinder(SOCK_R, Z_TOP, align=ON_BED)
    # scale on the front rail face (y = -(SOCK_R - 0.3 + RAIL_T)), raised 0.6, 45° tick undersides
    yf = -(SOCK_R - 0.3 + RAIL_T)
    for n in range(MARK_EVERY, MAX_RAIN + 1, MARK_EVERY):
        z = Z_ZERO + n * RATIO
        if z > Z_TOP - COLLAR_H - 2:
            break
        major = n % NUMBER_EVERY == 0
        tw = 7.0 if major else 4.5
        tick = Polygon((yf + 0.05, z - 0.65), (yf - 0.6, z), (yf - 0.6, z + 0.6), (yf + 0.05, z + 0.6), align=None)
        part += Pos(-SCALE_RAIL_W / 2 + 0.6, 0, 0) * extrude(Plane.YZ * tick, tw, dir=(1, 0, 0))
        if major:
            txt = label(str(n), size=LABEL_SIZE * 0.85, depth=0.65)
            part += Pos(SCALE_RAIL_W / 2 - 5.2, yf + 0.05, z - 0.4 * LABEL_SIZE * 0.85) * Rot(90, 0, 0) * txt
    # spike mortise + cross bolt (along X), teardrop
    mort = TENON + 2 * FIT_SLIDE
    part -= Pos(0, 0, -0.01) * Box(mort, mort, TENON_LEN + 0.5, align=ON_BED)
    roof = Pos(0, 0, TENON_LEN + 0.49) * loft([Rectangle(mort, mort), Plane.XY.offset(mort / 2 - 0.5) * Rectangle(1, 1)])
    part -= roof                                      # 45° pyramid roof instead of a 15 mm bridge
    part -= Pos(0, 0, TENON_LEN / 2) * teardrop_hole(clearance(4.0, "loose"), PLINTH_D + 2, along="X")
    # post-mount flange behind the plinth with 2 countersunk holes (screw from the front)
    fl = Pos(0, PLINTH_D / 2 - FLANGE_T / 2, 0) * Box(FLANGE_W, FLANGE_T, PLINTH_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    part += chamfer(fl.edges().group_by(Axis.Z)[0], 0.4)
    for sx in (-1, 1):
        x = sx * (FLANGE_W / 2 - 8)
        yfr = PLINTH_D / 2 - FLANGE_T
        part -= Pos(x, yfr, PLINTH_H / 2) * teardrop_hole(clearance(POST_SCREW_D, "loose"), 3 * FLANGE_T, along="Y")
        part -= Pos(x, yfr - 0.01, PLINTH_H / 2) * Rot(-90, 0, 0) * Cone(4.4, clearance(POST_SCREW_D, "loose") / 2, 2.0,
                                                                          align=(Align.CENTER, Align.CENTER, Align.MIN))
    return part


def funnel_in_use() -> Part:
    """Funnel with z = 0 at the holder collar top."""
    k = math.tan(math.radians(FUNNEL_PITCH))
    tv = FUNNEL_WALL / math.cos(math.radians(FUNNEL_PITCH))
    r_in0 = SPOUT_ID / 2
    zc0 = 2.0
    R = FUNNEL_D / 2
    z_rim = zc0 + (R - r_in0) * k
    skirt_ri = OUT_R + FIT_SLIDE
    skirt_ro = skirt_ri + FUNNEL_WALL
    prof = Polygon(
        (r_in0, -SPOUT_LEN), (SPOUT_OD / 2, -SPOUT_LEN), (SPOUT_OD / 2, zc0 - tv + (SPOUT_OD / 2 - r_in0) * k),
        (skirt_ri, zc0 - tv + (skirt_ri - r_in0) * k), (skirt_ri, -SKIRT_LEN), (skirt_ro, -SKIRT_LEN),
        (skirt_ro, zc0 - tv + (skirt_ro - r_in0) * k),
        (R + FUNNEL_WALL, zc0 - tv + (R + FUNNEL_WALL - r_in0) * k), (R + FUNNEL_WALL, z_rim + SPLASH_WALL_H - 1.2),
        (R + 1.2, z_rim + SPLASH_WALL_H), (R, z_rim + SPLASH_WALL_H), (R, z_rim), (r_in0, zc0), align=None,
    )
    return revolve(Plane.XZ * prof, Axis.Z)


def spike() -> Part:
    """Spike in its print pose: lying along +X, blade flat on the bed, tenon at x = 0."""
    blade = Polygon((0, -BLADE_W / 2), (SPIKE_LEN - 30, -BLADE_W / 2), (SPIKE_LEN, -1), (SPIKE_LEN, 1),
                    (SPIKE_LEN - 30, BLADE_W / 2), (0, BLADE_W / 2), align=None)
    part = extrude(blade, BLADE_T)
    rib = Polygon((0, -SPIKE_RIB / 2), (SPIKE_LEN - 15, -SPIKE_RIB / 2), (SPIKE_LEN - 2, 0),
                  (SPIKE_LEN - 15, SPIKE_RIB / 2), (0, SPIKE_RIB / 2), align=None)
    part += extrude(rib, BLADE_T + SPIKE_RIB)
    tenon = Pos(-TENON_LEN, 0, 0) * Box(TENON_LEN + 1, TENON, TENON, align=(Align.MIN, Align.CENTER, Align.MIN))
    part += tenon
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    part -= Pos(-TENON_LEN / 2, 0, TENON + 1) * pin_hole(clearance(4.0, "loose"), TENON + 2)
    return part


def build():
    fun = Rot(180, 0, 0) * funnel_in_use()
    fun = Pos(FLANGE_W / 2 + FUNNEL_D / 2 + 12, 10, -fun.bounding_box().min.Z) * fun
    sp = Pos(-PLINTH_D / 2 + TENON_LEN - 10, -FLANGE_W / 2 - 40, 0) * spike()
    return [holder(), fun, sp]
