"""capo-screw: screw-adjust capo for 6-string guitars (C-frame + swivel pad + thumb-screw knob).

Spec
- C-frame wraps the bass-side edge of the neck. The top bar lies across the strings just behind a
  fret, the bottom arm sits under the neck. An M5 bolt goes through a hex nut trapped in the bottom
  arm and pushes a swivel pad against the back of the neck. Designed for 15 kg (147 N) clamping force.
- Fits necks NECK_W_MIN..NECK_W_MAX (43-56 mm) wide at the fret and NECK_D_MIN..NECK_D_MAX
  (20-25 mm) deep, fretboard included. Strings add STRING_H on top of that.
- Every surface that touches the guitar has fillets of at least 1 mm and a recess for a pad: one on
  the underside of the bar (BAR_PAD_*) and one on the concave face of the swivel pad (PAD_FELT_*).
  Use adhesive FELT or cork, 2.5-3 mm thick. Some silicone and rubber compounds react with
  nitrocellulose finishes and leave marks, so use felt on vintage or nitro guitars.
- Printing: the C is printed flat on its side (print_orientation rx=90, +Y up), so the bending of
  the C runs along the layers, not across them. Big gussets at both inner corners. The bolt hole
  and the nut trap are horizontal in the print, so they have 45-degree teardrop/roof tops (no supports).
- The swivel pad and knob are modelled in their PRINT pose (axis along +Y, next to the frame) so that
  the shared rx=90 orientation stands them upright. They are not drawn in their assembled positions.
- 3 separate bodies on purpose (frame, pad, knob), printed together.

Hardware: 1x M5x40 hex-head bolt (ISO 4017, fully threaded), 1x M5 hex nut (DIN 934),
self-adhesive felt 3 mm (bar strip about 60x12 mm, pad disc about 17 mm), optional drop of CA glue
to hold the bolt head in the knob.
Assembly: press the bolt head into the knob's hex pocket, drop the nut into the trap from inside the
C, thread the bolt up through the nut, then push the swivel pad onto the bolt tip. Its 4.9 mm bore
grips the threads but lets the bolt turn inside it.

Assumptions
- Neck depth 20-25 mm counts the fretboard but not the strings; strings are about 3 mm above the
  fretboard (STRING_H).
- Bolt tip sits at about the middle of a 50 mm neck (SCREW_X). The concave pad (R30) handles the offset.
- ABS+ in-plane E is about 2 GPa. At 15 kg the bar tilts about 1-2 degrees; the 3 mm felt takes that
  up. Fully threaded bolt so the nut engages over the whole travel.
- The edges of the C on the bed side get a 1 mm 45-degree chamfer instead of a fillet (fillets can't
  print on the bed). Only felt touches the strings and neck.
"""

from build123d import *

from cadlib import *

# Parameters ---------------------------------------------------------------- guitar
NECK_W_MIN = 43.0
NECK_W_MAX = 56.0
NECK_D_MIN = 20.0
NECK_D_MAX = 25.0
STRING_H = 3.0            # strings above fretboard
CLAMP_KG = 15.0

# C-frame
T = 16.0                  # frame thickness (along strings); vertical when printed
SPINE = 14.0              # spine thickness (X)
BAR_H = 14.0              # top bar thickness (Z)
ARM_H = 12.0              # bottom arm thickness (Z)
GUSSET = 10.0             # 45-degree gusset leg in both inner corners
NECK_OFFSET = GUSSET + 2  # neck edge distance from spine
BAR_OVERHANG = 4.0        # bar reaches past the widest neck
SCREW_X = NECK_OFFSET + 25.0
ARM_TIP = 11.0            # bottom arm length past the screw axis
EDGE_R = 2.0              # fillet on all edges parallel to Y
FACE_R = 1.5              # fillet on the top (+Y) face perimeter
BED_CHAMFER = 1.0         # bed (-Y) face perimeter chamfer

# Pads (felt recesses)
FELT_T = 3.0
BAR_PAD_DEPTH = 1.5
BAR_PAD_RIM = 2.0         # wall left at each Y side
PAD_FELT_DEPTH = 1.5
PAD_FELT_RIM = 1.5

# Swivel pad
PAD_D = 20.0
PAD_H = 7.0
PAD_CONCAVE_R = 30.0      # matches back-of-neck curvature
PAD_BORE_D = 4.9          # grips M5 threads, bolt turns inside
PAD_BORE_DEPTH = 5.0

# Hardware fits
BOLT = "M5"
BOLT_CLEAR_D = clearance(5.0, "slide")                     # 5.5 hole in arm
NUT_AF = clearance(METRIC[BOLT]["nut_af"], "snug")         # 8.3 nut trap
NUT_DEPTH = METRIC[BOLT]["nut_h"] + 0.4
HEAD_AF = clearance(8.0, "press")                          # M5 hex head, press fit
HEAD_DEPTH = 3.5 + 0.5
BOLT_LEN = 40.0

# Knob
KNOB_D = 30.0
KNOB_H = 14.0
KNOB_FLUTES = 10
KNOB_FLUTE_R = 2.5

# Derived
GAP = NECK_D_MAX + STRING_H + (FELT_T - BAR_PAD_DEPTH) + PAD_H + (FELT_T - PAD_FELT_DEPTH) + 1.0
Z_BAR = ARM_H + GAP           # underside of bar
Z_TOP = Z_BAR + BAR_H
BAR_END = NECK_OFFSET + NECK_W_MAX + BAR_OVERHANG
ARM_END = SCREW_X + ARM_TIP

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="Guitar Core ABS+ 0.20mm @BBL H2C",
    standing=False,
    # clamping reaction: 15 kg on the pad and on the bar
    loads=[dict(at=(SCREW_X, 0, ARM_H + 2), grams=CLAMP_KG * 1000),
           dict(at=(SCREW_X, 0, Z_BAR), grams=CLAMP_KG * 1000)],
    print_orientation=(90, 0, 0),   # C flat on its side: bending runs along the layers
    supports="off",
    brim="auto",
)


def _teardrop_z(d: float, z0: float, z1: float) -> Part:
    """Hole along Z with a 45-degree tip toward +Y (= print up)."""
    r = d / 2
    tip = Polygon((-r * 0.7071, r * 0.7071), (0, r * 1.4142), (r * 0.7071, r * 0.7071),
                  (0, 0), align=None)
    sk = Circle(r) + tip
    return Pos(0, 0, z0) * extrude(sk, z1 - z0)


def _hex_roof_z(af: float, depth: float) -> Part:
    """Hex pocket (vertex toward +Y) with a 45-degree roof, cutting down from z=0."""
    R = af / 3 ** 0.5
    c = R * 0.8660
    pts = [(c, -R / 2), (0, -R), (-c, -R / 2), (-c, R / 2), (0, R / 2 + c), (c, R / 2)]
    return extrude(Polygon(*pts, align=None), -depth)


def c_frame() -> Part:
    g = GUSSET
    prof = Polygon(
        (-SPINE, 0), (ARM_END, 0), (ARM_END, ARM_H), (g, ARM_H), (0, ARM_H + g),
        (0, Z_BAR - g), (g, Z_BAR), (BAR_END, Z_BAR), (BAR_END, Z_TOP), (-SPINE, Z_TOP),
        align=None)
    f = extrude(Plane.XZ * prof, T / 2, both=True)
    f = fillet(f.edges().filter_by(Axis.Y), EDGE_R)
    f = fillet(f.faces().sort_by(Axis.Y)[-1].edges(), FACE_R)
    f = chamfer(f.faces().sort_by(Axis.Y)[0].edges(), BED_CHAMFER)

    # felt recess under the bar: trapezoid cross-section (45-degree walls, no overhang in print)
    w0 = T - 2 * BAR_PAD_RIM
    tr = Polygon((-w0 / 2, 0), (w0 / 2, 0), (w0 / 2 - BAR_PAD_DEPTH, BAR_PAD_DEPTH),
                 (-w0 / 2 + BAR_PAD_DEPTH, BAR_PAD_DEPTH), align=None)
    x0, x1 = NECK_OFFSET - 4, BAR_END - 3
    rec = Pos(x0, 0, Z_BAR) * extrude(Plane.YZ * tr, x1 - x0)
    f -= rec

    # bolt hole + nut trap (nut sits on the trap floor; bolt push loads it into the plastic)
    f -= Pos(SCREW_X, 0, 0) * _teardrop_z(BOLT_CLEAR_D, -1, ARM_H + 1)
    f -= Pos(SCREW_X, 0, ARM_H) * _hex_roof_z(NUT_AF, NUT_DEPTH)
    return f


def swivel_pad() -> Part:
    """Modelled in print pose: axis +Y, flat base at y=0, concave felt face toward +Y."""
    p = Cylinder(PAD_D / 2, PAD_H, align=ON_BED)
    p = chamfer(p.edges().group_by(Axis.Z)[0], 0.4)
    # concave cylindrical face, cylinder axis along X (along the neck when fitted)
    zc = PAD_H + PAD_CONCAVE_R - 1.8
    cav = Pos(0, 0, zc) * Rot(0, 90, 0) * Cylinder(PAD_CONCAVE_R, PAD_D + 4)
    p -= cav
    p = fillet(p.edges().sort_by(Axis.Z)[-1:], 1.2)
    # felt recess: concave face pushed down PAD_FELT_DEPTH inside the rim
    cav2 = Pos(0, 0, zc) * Rot(0, 90, 0) * Cylinder(PAD_CONCAVE_R + PAD_FELT_DEPTH, PAD_D + 4)
    p -= cav2 & Cylinder(PAD_D / 2 - PAD_FELT_RIM, PAD_H * 3)
    # bore for the bolt tip, from the base
    p -= Pos(0, 0, PAD_BORE_DEPTH) * Cylinder(hole_d(PAD_BORE_D) / 2, PAD_BORE_DEPTH,
                                              align=(Align.CENTER, Align.CENTER, Align.MAX))
    return p


def knob() -> Part:
    """Modelled in print pose: axis +Y, hex head pocket on top (no bridges)."""
    k = Cylinder(KNOB_D / 2, KNOB_H, align=ON_BED)
    for i in range(KNOB_FLUTES):
        k -= Rot(0, 0, i * 360 / KNOB_FLUTES) * Pos(KNOB_D / 2 + 0.8, 0, KNOB_H / 2) * \
            Cylinder(KNOB_FLUTE_R, KNOB_H + 2)
    k = chamfer(k.edges().group_by(Axis.Z)[0], 0.4)
    k = fillet(k.edges().group_by(Axis.Z)[-1], 1.0)
    k -= Pos(0, 0, KNOB_H) * extrude(RegularPolygon(HEAD_AF / 3 ** 0.5, 6), -HEAD_DEPTH)
    k -= Pos(0, 0, -1) * Cylinder(hole_d(BOLT_CLEAR_D) / 2, KNOB_H + 2, align=ON_BED)
    return k


def build():
    frame = c_frame()
    # parts in print pose: rotate (-90 about X) so that the global rx=90 stands them upright
    y0 = -T / 2
    pad = Pos(BAR_END - 10, y0, ARM_H + 12) * Rot(-90, 0, 0) * swivel_pad()
    kn = Pos(BAR_END - 5, y0, ARM_H - 24) * Rot(-90, 0, 0) * knob()
    return [frame, pad, kn]
