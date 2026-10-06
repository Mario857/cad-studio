"""ball-launcher: tennis-ball thrower stick, 450 mm, flexing grip cup, 2-part bolted + glued joint.

Spec: holds a standard 65 mm tennis ball in a cup whose six fingers (5 slits) flex open: the lip
(LIP_D 62 mm) is smaller than the ball so it snaps in and is released by the throw. Shaft 20 x 26 mm
(flat 45-deg-chamfered underside, round top), ergonomic handle 28-31 wide x 32-36 tall with a palm
swell and a pommel flare. Overall 450 x 72 x 42 mm.
Split in two at a 60 mm side-by-side lap joint (split plane XZ) so each part is 250 mm long:
  part A = cup + front shaft, part B = rear shaft + handle (2 separate bodies on purpose,
  printed together on one plate).
Joint: 2x M5x16 socket head cap screws (heads recessed in part A) + 2x M5 nyloc nuts (hex traps in
part B), plus glue on the lap faces (ABS cement / acetone slurry or 2-part epoxy).
Strength: throw load ~3 kg at the cup -> ~12 N*m at the grip. Both parts print lying flat as used
(fixed orientation), so the shaft's bending stress runs along the layers; bolts are horizontal
(teardrop holes) and clamp the lap halves across Y; the lap halves keep the full 26 mm depth in the
bending plane.

Safety: ABS must not hold food/water directly and is not a chew toy - put the launcher away after
play; the dog should only touch the ball. Check the joint bolts and the cup fingers for cracks
before use; replace if cracked. Throw away from people/windows.
Assumptions: 65-67 mm ball; 0.1 mm gap on each lap face (filled by glue); hardware is standard
ISO 4762 M5x16 + ISO 10511 M5 nyloc (8 mm AF, 5 mm tall).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(36, 0, 36), grams=3000)],  # ball throw at the cup (bending along the shaft)
    print_orientation=(0, 0, 0),  # flat as used: shaft bending runs along the layers
    supports="off",
    brim="auto",
    hardware=["2x M5x16 socket head cap screw (ISO 4762)", "2x M5 nyloc nut (ISO 10511)",
              "ABS cement or 2-part epoxy for the lap faces"],
)

# Parameters
TOTAL_L = 450.0
BALL_D = 65.0
BOWL_R = 33.5            # ball pocket sphere radius (ball 32.5 + 1 mm)
LIP_D = 62.0             # snap lip < ball -> fingers flex
FLOOR_T = 3.0
CUP_R = 36.0             # cup outer radius
CUP_R_BOTTOM = 28.0
CUP_FLARE_H = 10.0
CUP_H = 42.0
SLITS = 6
SLIT_W = 3.0
SLIT_Z0 = 18.0           # slit bottom (finger root)
SLIT_FILLET = 1.0
RIM_FILLET = 0.8
POMMEL_FILLET = 3.0
LIP_RISE = 1.6            # lip cone height / radial step (>1 = steeper than 45 deg)

SHAFT_W = 20.0
SHAFT_H = 26.0
BOT_CHAMF = 3.0          # 45-deg underside chamfer (printable, no sharp bed corners)
GRIP_W, GRIP_H = 28.0, 32.0
SWELL_W, SWELL_H = 31.0, 35.0
POMMEL_W, POMMEL_H = 32.0, 38.0
GRIP_X0 = 300.0          # grip starts
SPLIT_X = 200.0          # lap joint start
LAP_L = 60.0
LAP_GAP = 0.1            # per face
END_GAP = 0.3

BOLT_D = 5.5             # M5 clearance
HEAD_D = 9.5             # M5 SHCS head 8.5 + clearance
HEAD_DEPTH = 4.0
NUT_AF = 8.3             # M5 nyloc 8 AF + clearance
NUT_DEPTH = 5.5
BOLT_Z = 11.0
BOLT_INSET = 15.0


def sec(w, h, n=16):
    """Flat-bottom section on Plane.YZ: 45deg bottom chamfers, straight sides, round top."""
    r = w / 2
    zc = h - r
    pts = [(-r + BOT_CHAMF, 0), (r - BOT_CHAMF, 0), (r, BOT_CHAMF), (r, zc)]
    for i in range(1, n):
        a = math.pi * i / n
        pts.append((r * math.cos(a), zc + r * math.sin(a)))
    pts += [(-r, zc), (-r, BOT_CHAMF)]
    return Polygon(*pts, align=None)


def cup() -> Part:
    prof = Polygon((0, 0), (CUP_R_BOTTOM, 0), (CUP_R, CUP_FLARE_H), (CUP_R, CUP_H), (0, CUP_H),
                   align=None)
    body = revolve(Plane.XZ * prof, Axis.Z, 360)
    # no 0.4 bed chamfer: the 39-deg flare already relieves the elephant foot
    return Pos(CUP_R, 0, 0) * body


def cup_cutter() -> Part:
    zc = FLOOR_T + BOWL_R
    lip_r = LIP_D / 2
    rise = LIP_RISE * (BOWL_R - lip_r)  # steeper than 45 deg in, then 45 deg lead-in out
    top = CUP_H + 4
    h45 = BOWL_R / math.sqrt(2)
    x0 = 3.0  # keep the revolve profile off the axis (clean mesh), core filled by a cylinder
    z0 = zc - math.sqrt(BOWL_R**2 - x0**2)
    arc = ThreePointArc((x0, z0), (h45, zc - h45), (BOWL_R, zc))
    pl = Polyline((BOWL_R, zc), (lip_r, zc + rise), (lip_r + top - zc - rise, top), (x0, top), (x0, z0))
    prof = make_face(Wire([arc] + pl.edges()))
    cut = revolve(Plane.XZ * prof, Axis.Z, 360)
    cut += Pos(0, 0, z0 + 0.3) * Cylinder(x0 + 0.5, top - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for k in range(SLITS):
        a = 30 + 60 * k
        s = Pos(CUP_R - 8, 0, SLIT_Z0) * Box(20, SLIT_W, CUP_H, align=(Align.MIN, Align.CENTER, Align.MIN))
        s += Pos(CUP_R - 8, 0, SLIT_Z0) * (Rot(0, 90, 0) * Cylinder(SLIT_W / 2, 20, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        cut += Rot(0, 0, a) * s
    return Pos(CUP_R, 0, 0) * cut


def hex_prism(af, length):
    """Hex prism along Y, centred, flats top/bottom, 45-deg roof over the top flat (no bridge)."""
    side = af / math.sqrt(3)
    hx = RegularPolygon(side, 6) + Polygon((-side / 2, af / 2 - 0.01), (side / 2, af / 2 - 0.01),
                                          (0, af / 2 + side / 2), align=None)
    return extrude(Plane.XZ * hx, length / 2, both=True)


def build():
    lap0, lap1 = SPLIT_X, SPLIT_X + LAP_L
    # ---- part A: cup + shaft up to end of lap
    shaft_a = extrude(Plane.YZ.offset(CUP_R) * sec(SHAFT_W, SHAFT_H), lap1 - END_GAP - CUP_R)
    a = cup() + shaft_a
    a -= cup_cutter()
    # round the lip rim and the finger (slit) edges the dog's mouth touches
    # (slit edges first, then the rim: one combined fillet meshes badly)
    near = [e for e in a.edges() if e.center().X < 2 * CUP_R + 1]
    a = fillet([e for e in near if e.bounding_box().min.Z < CUP_H - 1
                and e.bounding_box().max.Z > CUP_H - 0.5], SLIT_FILLET)
    a = fillet([e for e in a.edges() if e.center().X < 2 * CUP_R + 1
                and e.bounding_box().min.Z > CUP_H - 0.3], RIM_FILLET)
    a -= Pos(lap0 - END_GAP, LAP_GAP / 2 - 0, -1) * Box(LAP_L + 10, 20, 60,
                                                        align=(Align.MIN, Align.MIN, Align.MIN))
    # ---- part B: shaft from lap start + lofted ergonomic handle
    shaft_b = extrude(Plane.YZ.offset(lap0 + END_GAP) * sec(SHAFT_W, SHAFT_H), GRIP_X0 - lap0 - END_GAP)
    stations = [(GRIP_X0, SHAFT_W, SHAFT_H), (GRIP_X0 + 25, GRIP_W, GRIP_H),
                (GRIP_X0 + 75, SWELL_W, SWELL_H), (TOTAL_L - 30, GRIP_W, GRIP_H),
                (TOTAL_L - 8, POMMEL_W, POMMEL_H), (TOTAL_L, POMMEL_W - 6, POMMEL_H - 6)]
    handle = loft([Plane.YZ.offset(x) * sec(w, h) for x, w, h in stations])
    end = handle.faces().sort_by(Axis.X)[-1]
    handle = fillet([e for e in end.edges() if e.bounding_box().min.Z > 0.5], POMMEL_FILLET)
    b = shaft_b + handle
    b -= Pos(lap0 - 10, -LAP_GAP / 2, -1) * Box(LAP_L + 10, 20, 60,
                                                 align=(Align.MIN, Align.MAX, Align.MIN))
    # ---- joint bolts (horizontal along Y -> teardrops)
    for x in (lap0 + BOLT_INSET, lap1 - BOLT_INSET):
        a -= Pos(x, 0, BOLT_Z) * teardrop_hole(BOLT_D, 40, along="Y")
        b -= Pos(x, 0, BOLT_Z) * teardrop_hole(BOLT_D, 40, along="Y")
        a -= Pos(x, -SHAFT_W / 2 - 5 + HEAD_DEPTH, BOLT_Z) * teardrop_hole(HEAD_D, 10, along="Y")
        b -= Pos(x, SHAFT_W / 2 + 5 - NUT_DEPTH, BOLT_Z) * hex_prism(NUT_AF, 10)
    # B printed next to A on the plate
    return [a, Pos(-SPLIT_X, CUP_R + POMMEL_W / 2 + 6, 0) * b]
