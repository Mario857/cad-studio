"""curtain-hook-snap2: screw-on hook for a Ø9 mm curtain rod, symmetric C-clip with two snap fingers.

Spec: rod Ø9 in a Ø10.5 cradle (rod slides freely). Base 20 (Y) x 26 (X) x 4 mm with ONE
centered countersunk hole (Ø3.8, csk Ø7.0) for a 3.5 mm self-tapping screw, directly under the
cradle centre line (x=0) so the rod load acts through the screw. The screw is driven from above
through an access bore (Ø7.6, with 45 deg tips so it prints without supports) in the post, passing
the rod mouth (8 mm) BEFORE the rod is clicked in. Install: screw first, then press the rod in. Rod axis 25 mm out from the frame face
(frame face = z=0). Printed as a set of 2 identical hooks.

How it works: the cradle is a C-ring (OD 14.1, ID 10.5) whose opening is a symmetric mouth,
8.0 mm wide (rod is 9). Each side of the ring above the post is a curved cantilever finger.
Each finger ends in a 45 deg lead-in (mouth flares up and outward) and a retaining shoulder
(the underside of the tip, where the cavity curves back out). Press the rod in from the front:
both fingers flex apart ~0.5 mm each (1.0 mm total opening), the rod drops into the cradle and
the fingers click shut. Retention is redundant: either finger alone still blocks the mouth by 0.5 mm.

Strain (per finger): free arc length root->tip ~9 mm (mean R 6.1, ~88 deg), thickness t=1.8,
deflection d=0.5: eps ~ 1.5*t*d/L^2 = 1.5*1.8*0.5/9^2 ~ 1.7% (< 2%, ABS+ yield ~2.5-3%, keep
margin; curved-beam is a little more compliant, so real value is slightly lower).
Insertion force ~ 8-12 N, pull-out (rod straight out front) ~ 20-30 N by hand; the curtain
load is gravity pushing down into the closed bottom of the cradle, so the clip only keeps the
rod from lifting out/knocked off. Pro: no loose parts, 2 redundant fingers, symmetric.
Con: fingers at 1.8 mm are the weakest part (fatigue after many cycles; do not open/close
hundreds of times); rod diameter tolerance matters (a rod > 9.3 needs a larger mouth).

Screws: ONE 3.5 mm self-tapping, 10 mm recommended (max 12), csk head <= Ø7.0. Base is 4 mm, so
10 mm screw enters the frame ~6 mm (12 mm -> ~8 mm); do NOT exceed 12 mm (would break through
uPVC outer wall into the chamber/outside). Pre-drill 2.5 mm pilot in the uPVC.
One-screw rationale: load (gravity, down in the cradle) is along the post over the screw, so shear
goes into the screw; saves material. Prying: rod lever arm 25 mm; base extends 13 mm each side of
the screw (flat bearing face >= 6 mm needed, 13 given) and the post flares at >45 deg, so tipping
is resisted by bearing on the frame face, not by screw pull-out. Hold estimate: a 10 mm screw in
uPVC ~100-150 N pull-out, ~1-1.5 kg of curtain per hook is fine; keep < ~1 kg per hook.
Rotation caveat: one screw lets the hook swivel about the screw until tight. Tighten with the
hook aligned (rod along Y); if desired, press the base's flat long edge against the sash or add a
4 mm tall locating nub on the frame side. Not modelled.

Slicer settings (ABS+ H2C 0.4): 0.20 mm layers, 4 walls (all-wall, near 100% infill), 5 top/bottom,
no supports, brim off or small, enclosed chamber, 100% infill gives best finger fatigue.
Print orientation: profile lies flat in XY (extruded height 20 mm standing up), so layers run
around the curve and along the fingers, never across them.
Assumptions: frame face is flat; hooks are placed with the rod running along Y.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(90, 0, 0),   # extrusion axis (Y) becomes print Z; profile lies in XY
    supports="off",
    brim="off",
)

# Parameters
W = 20.0            # width along rod (Y)
BASE_L = 26.0
BASE_T = 4.0
ROD_Z = 25.0        # rod axis height above frame face
HOLE_D = 10.5       # cradle
RING_OD = 14.1      # 1.8 mm finger wall
MOUTH = 8.0         # opening between lips (rod 9 -> 0.5 mm per finger)
LIP_Z = 3.4         # lip height above axis: sqrt(5.25^2 - 4^2)
MOUTH_TOP = 4.0     # flat tip top above axis
LEADIN = 0.6        # 45 deg lead-in length
POST_W = 10.4       # post width at ring
POST_FLARE = 9.0    # half width at base
SCREW_D = 3.8
CSK_D = 7.0
BORE_D = 7.6        # driver/head access bore through post
COPY_DX = 30.0


def one() -> Part:
    base = Box(BASE_L, W, BASE_T, align=ON_BED)
    post_prof = Polygon((-POST_FLARE, BASE_T - 0.1), (POST_FLARE, BASE_T - 0.1),
                        (POST_W / 2, 14), (POST_W / 2, ROD_Z), (-POST_W / 2, ROD_Z),
                        (-POST_W / 2, 14), align=None)
    post = extrude(Plane.XZ * post_prof, W / 2, both=True)
    ring = Pos(0, 0, ROD_Z) * (Rot(90, 0, 0) * Cylinder(RING_OD / 2, W))
    part = base + post + ring
    # top cut: everything above tip level
    top_z = ROD_Z + MOUTH_TOP
    half = MOUTH / 2
    lip_z = ROD_Z + LIP_Z
    mouth = Polygon((-half, ROD_Z + 2), (half, ROD_Z + 2), (half, lip_z),
                    (half + LEADIN, top_z), (12, top_z), (12, top_z + 5),
                    (-12, top_z + 5), (-12, top_z), (-half - LEADIN, top_z), (-half, lip_z),
                    align=None)
    part = part - extrude(Plane.XZ * mouth, W, both=True)
    part = part - Pos(0, 0, ROD_Z) * (Rot(90, 0, 0) * Cylinder(HOLE_D / 2, W + 2))
    # elephant-foot chamfer on the print-bed face (min Y)
    part = chamfer(part.faces().sort_by(Axis.Y)[0].edges(), 0.4)
    # access bore (circle + 45 deg tips along +-Y so it prints support-free) from base top up to cradle
    r = BORE_D / 2
    t = r / 2 ** 0.5
    tip = r * 2 ** 0.5
    prof = Polygon((0, -tip), (t, -t), (t, t), (0, tip), (-t, t), (-t, -t), align=None)
    bore = extrude(Plane.XY.offset(BASE_T) * (prof + Circle(r)), ROD_Z - BASE_T)
    part = part - bore
    # single centered countersunk hole
    thru = Pos(0, 0, -BASE_T) * Cylinder(SCREW_D / 2, BASE_T * 3, align=ON_BED)
    csk = Pos(0, 0, BASE_T - 1.6) * Cone(SCREW_D / 2, CSK_D / 2, 1.6, align=ON_BED)
    part = part - thru - csk
    return part


def build():
    p = one()
    return [p, Pos(COPY_DX, 0, 0) * p]
