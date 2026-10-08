"""curtain-hook-latch: screw-on J-hook for a Ø9 mm curtain rod with a hinged press-down latch.

HOW IT WORKS
  Profile lies in the XY plane and is extruded 20 mm along Z (= print Z, so layer lines never cross
  the load-bearing curve; the whole hook prints flat-profile, zero supports).  X = out from the frame
  face (base back at x=0), Y = up in use, rod axis at x=25 (25 mm out), cradle hole Ø10.5.
  Base 20 x 38 x 4 mm, 2 countersunk Ø3.8 holes (90 deg csk, Ø7.4 head) for 3.5 mm self-tapping
  screws, heads on the +X face.  Rod drops into the cradle through a 10 mm top opening; a latch
  arm on a print-in-place vertical pin hinge (pin Ø3, hole Ø3.6 = 0.3 mm radial clearance, 0.3 mm
  Z clearance) swings from ~90 deg open down over the opening.  Press it down: the finger on the
  latch tip rides over a 0.7 mm 45 deg bump on the post (interference 0.4 mm) and clicks shut.
  Hinge stops at 90 deg (tower wall), so it cannot flop over.  Latch (13.4 mm tall, on the bed layer) sits under a
  tower ear; the pin hangs from the ear and has a 45 deg flared foot that traps the latch, no supports.
  Screw depth: 12 mm max screw - 4 mm base (csk head sits flush inside it) = max 8 mm into the
  frame: it bites the 2.5-3 mm outer uPVC wall plus the first chamber, but stops short of the steel
  liner (typically >= 10 mm behind the surface in the screw-line); use screws NOT longer than 12 mm.
PROS/CONS
  + rod cannot jump out when the window is slammed/moved; tool-less; one printed set.
  - small moving part (ABS finger fatigues if clicked thousands of times); bump retention is a
    detent, not a lock; pull on the latch tip with a finger to open.
HOLD STRENGTH (estimate)
  Latch click-open force ~5-10 N (finger flex ~1.5 % strain); fine for a light rod (<0.5 kg).
  Load-bearing arm 5.25 mm thick x 20 mm, bending along layers: holds >10 kg before failing; real
  limit is the two screws in uPVC (~20-30 kg pull-out each wall) - far above the curtain load.
RECOMMENDED SLICER SETTINGS
  Orientation: as exported (profile flat on bed, 20 mm tall, Z = extrusion), 2 copies side by side.
  Layer 0.20 mm (0.16 gives cleaner 0.3 mm hinge gap), 4 walls, 40 % gyroid (or 100 % infill
  - parts are small), 4 top/bottom layers, supports OFF, brim OFF (add 3 mm brim if ABS warps),
  enclosed chamber, no fan.  After printing, flex the latch once to break any hinge fusing.
KNOWN WARNS: 2 bodies = hook + print-in-place latch (intended). 'needs support' 0.8 cm2 = the 6 mm
  ear roof over the latch cavity (z 13.7) and the 0.3 mm gap, a <=8 mm bridge: prints fine with bridge
  settings, no supports.  Latch is 13.4 mm of the 20 mm width; the rod is retained by it.
ASSUMPTIONS: copies=2 (identical hooks printed together); Ø9 rod, Ø10.5 hole; vertical window frame
  (Y = up); steel liner deeper than 8 mm behind the face.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),   # profile in XY on the bed, Z = extrusion
    supports="off",
    brim="off",
    copies=2,
)

# Parameters
W = 20.0                 # hook width (Z)
BASE_T = 4.0
BASE_L = 38.0
SCREW_Y = 14.0
SCREW_D = 3.8
CSK_D = 7.4
ROD_X = 25.0
HOLE_R = 10.5 / 2
WALL = 2.5
RING_R = HOLE_R + WALL
OPEN_X0, OPEN_X1 = 20.0, 30.0       # 10 mm entry opening for the 9 mm rod
TOWER_X0, TOWER_Y1 = 8.0, 13.5
POST_X0, POST_X1, POST_Y1 = 30.0, 33.5, 5.6
PIN = (14.5, 7.5)
PIN_R = 1.5
CL = 0.3                 # hinge clearance
SLOT_Z0, SLOT_Z1 = 0.0, 13.7   # latch lives on the bed layer (z 0..13.4)
KNUCKLE_R = 4.0
ARM_Y0, ARM_Y1 = 6.0, 9.0
ARM_X1 = 35.8
BUMP = 0.7
RIM = 0.6               # vertical rim of the pin foot (avoids a knife edge)
HEAD = 0.9              # pin retaining-cone flare (45 deg)


def prism(x0, x1, y0, y1, z0=0.0, z1=W):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, z0) * Box(
        x1 - x0, y1 - y0, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def cyl(cx, cy, r, z0, z1):
    return Pos(cx, cy, z0) * Cylinder(r, z1 - z0, align=ON_BED)


def latch_blank(grow=0.0):
    z0, z1 = SLOT_Z0 - grow, SLOT_Z1 - CL + grow
    s = cyl(*PIN, KNUCKLE_R + grow, z0, z1)
    s = s + prism(PIN[0], ARM_X1 + grow, ARM_Y0 - grow, ARM_Y1 + grow, z0, z1)
    return s


def build():
    hook = prism(0, BASE_T, -BASE_L / 2, BASE_L / 2)
    hook += prism(BASE_T - 0.1, ROD_X, -RING_R, -2.5)
    hook += cyl(ROD_X, 0, RING_R, 0, W)
    hook += prism(TOWER_X0, OPEN_X0, -RING_R, TOWER_Y1)
    hook += prism(POST_X0, POST_X1, 0, POST_Y1)
    # detent bump on the post's outer face
    bump = extrude(Polygon((POST_X1 - 0.1, 2.0), (POST_X1 + BUMP, 3.0), (POST_X1 - 0.1, 4.0),
                           align=None), amount=W)
    hook += bump
    hook -= cyl(ROD_X, 0, HOLE_R, -1, W + 1)
    hook -= prism(OPEN_X0, OPEN_X1, 0, 30, -1, W + 1)
    hook -= prism(OPEN_X1, 40, POST_Y1, 30, -1, W + 1)   # trim ring crown flush with post top
    # countersunk screw holes (heads on +X face)
    for y in (-SCREW_Y, SCREW_Y):
        hook -= Pos(-0.5, y, W / 2) * Rot(0, 90, 0) * Cylinder(SCREW_D / 2, BASE_T + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
        hook -= Pos(BASE_T - 1.8, y, W / 2) * Rot(0, 90, 0) * Cone(SCREW_D / 2, CSK_D / 2, 1.8, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # latch swing clearance in the slot layer (0..90 deg), then the pin
    sweep_h = 1.5 + CL
    hook -= cyl(*PIN, KNUCKLE_R + CL, SLOT_Z0 - 1, SLOT_Z1)
    hook -= prism(PIN[0] - sweep_h, PIN[0] + 25, PIN[1] - sweep_h, PIN[1] + 30, SLOT_Z0 - 1, SLOT_Z1)
    hook += cyl(*PIN, PIN_R, 0, W)
    hook += cyl(*PIN, PIN_R + HEAD, 0, RIM)
    hook += Pos(*PIN, RIM) * Cone(PIN_R + HEAD, PIN_R, HEAD, align=ON_BED)

    # latch
    z0, z1 = SLOT_Z0, SLOT_Z1 - CL
    latch = latch_blank()
    finger = extrude(Polygon((ARM_X1 - 2.0, 1.3), (ARM_X1 - 1.2, 0.5), (ARM_X1, 0.5),
                             (ARM_X1, ARM_Y1), (ARM_X1 - 2.0, ARM_Y1), align=None),
                     amount=z1 - z0)
    latch += Pos(0, 0, z0) * finger
    latch -= cyl(*PIN, PIN_R + CL, z0 - 1, z1 + 1)
    # conical retaining head: latch hole flares to the bed (45 deg), pin flares to match
    latch -= cyl(*PIN, PIN_R + CL + HEAD, -1, RIM)
    latch -= Pos(*PIN, RIM) * Cone(PIN_R + CL + HEAD, PIN_R + CL, HEAD, align=ON_BED)
    return [hook, latch]
