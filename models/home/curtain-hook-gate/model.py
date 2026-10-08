"""curtain-hook-gate: screw-on closed-ring hook with removable dovetail gate, for a Ø9 mm curtain rod.

HOW IT WORKS
  Profile (ring + neck + base) lies in the XZ plane and is extruded 20 mm along Y (= rod axis), so
  the printed layer lines run ALONG the rod axis and never cross the load-carrying curve.
  The hook is a closed ring (bore Ø10.5, rod Ø9 -> 1.5 mm total slack) with a 45-degree dovetail
  slot across its top. A small gate (keystone, wider underneath) slides into that slot with 0.25 mm
  clearance and closes the ring. A half-round detent ridge (r0.6, 4 mm long, x2) on the slot floor snaps into a
  groove in the gate underside when the gate is fully seated. To fit/remove the rod: slide the gate
  out, drop the rod through the 10.5 mm top opening, slide the gate back in until it clicks.
  DEVIATION from brief: the gate slides along the rod axis (Y, toward the viewer), not straight up.
  A 45-degree dovetail only locks upward pull-out if the slide direction is perpendicular to the
  flanks; sliding it vertically would make the "dovetail" a plain wedge that pops out under load.
  The dovetail flanks (45 deg) take any upward rod push, the detent only stops the gate creeping
  along Y (blind 2 mm back wall stops it at the other end).

SCREWS: 2 x 3.5 mm self-tapping, countersunk, max length 12 mm. Countersunk head sits INSIDE the
  4 mm base, so a 12 mm screw only protrudes 12-4 = 8 mm into the frame (6 mm for 10 mm screws:
  recommended). uPVC outer wall ~2.5-3 mm, the steel liner sits behind the first chamber, so the
  8 mm tip ends in the chamber / at most reaches the inner skin; use <=10 mm screws if the profile
  is shallow. Never use screws longer than 12 mm.

PROS: rod cannot escape in any direction while the gate is in (full closed ring); gate is
  captive (dovetail), tiny, no springy parts; hook itself is a solid stiff ring.
CONS: rod can only be removed by sliding the gate out first (two-handed, 1 extra part per hook that
  can get lost); the detent is friction only; small gate prints standing on a 17 x 3 mm footprint
  (use a brim).
HOLD STRENGTH (estimate, ABS, layers along the rod axis): ring/neck cross-section 20 x 17 mm,
  walls 3.25 mm: > 15 kg static in bending on the ring; gate dovetail > 5 kg upward. Real limit is
  the two 3.5 mm screws in uPVC: ~ 0.5-1 kg per hook is the sane design load for a light rod.

SLICER SETTINGS: orientation as exported in the 3mf (profile flat in the XY plane, rod axis = Z,
  base plate standing on its 20 mm edge, slot opening facing the bed -> slot back wall is a floor);
  layer 0.2 mm; walls 4 (1.6 mm min, ~3 mm total at the ring); top/bottom layers 4; infill 25 %
  gyroid (ABS: enclosure/draft shield on, no part-cooling fan); supports OFF (all overhangs
  <= 45 deg, detent dimple is a tiny arch); brim 5 mm on (tall thin gates).
PRINT: 2 hooks + 2 gates = two complete sets in one print (copies=1, parts listed explicitly).

Assumptions: ring wall 3.25 mm (slot floor 3 mm above rod axis+, gate 5.5 mm tall, head 26 mm wide); countersink for Ø7.2 head; screws at X = +-13 mm; frame face at
z=0 (base underside), rod axis 25 mm above it, along Y.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(-90, 0, 0),
    supports="off",
    brim="on",
)

# Parameters
ROD_D = 9.0
BORE_D = 10.5
BASE_L = 38.0
BASE_W = 20.0
BASE_T = 4.0
ROD_H = 25.0            # rod axis height above frame face
RING_R = 8.5            # outer ring radius (wall 3.25)
HEAD_HW = 13.0          # head half width (side wall 2.25 at slot floor)
SCREW_X = 13.0
SCREW_D = 3.8
CSK_D = 7.2
GATE_CLR = 0.25
SLOT_TOP_HW = 5.25      # opening half width (10.5 > rod 9)
SLOT_BACK = 2.0         # blind back wall of slot
BUMP_R = 0.6
BUMP_Y = -6.0
BUMP_X = 7.5            # two detent bumps on the slot floor, outside the bore
GATE_SPACING = 33.0

ZC = ROD_H
ZT = ZC + RING_R                    # top of head
ZF = ZC + 3.0                       # slot floor (cuts into bore top: no tangency)
HW = BASE_W / 2


def _ex(poly, y0, y1):
    """extrude an XZ polygon between y0 and y1."""
    sk = Plane.XZ * Polygon(*poly, align=None)
    s = extrude(sk, amount=(y1 - y0) / 2, both=True)
    return Pos(0, (y0 + y1) / 2, 0) * s


def _w(z):
    return SLOT_TOP_HW + (ZT - z)


def hook() -> Part:
    c = RING_R
    outer = [(-c, 0), (c, 0), (c, ZC), (HEAD_HW, ZC + HEAD_HW - c), (HEAD_HW, ZT - 1),
             (HEAD_HW - 1, ZT), (-HEAD_HW + 1, ZT), (-HEAD_HW, ZT - 1),
             (-HEAD_HW, ZC + HEAD_HW - c), (-c, ZC)]
    body = _ex(outer, -HW, HW)
    body += Pos(0, 0, ZC) * (Rot(90, 0, 0) * Cylinder(RING_R, BASE_W))
    base = Pos(0, 0, 0) * Box(BASE_L, BASE_W, BASE_T, align=ON_BED)
    body += base
    # bore
    body -= Pos(0, 0, ZC) * (Rot(90, 0, 0) * Cylinder(BORE_D / 2, BASE_W + 2))
    # lightening diamond (45 deg top, prints without support)
    d, zd = 4.0, 10.2
    body -= _ex([(-d, zd), (0, zd - d), (d, zd), (0, zd + d)], -HW - 1, HW + 1)
    # dovetail slot (wider at the bottom), open at y=-HW, blind wall at +HW-SLOT_BACK
    ytop = ZT + 1.5
    slot_poly = [(-_w(ZF), ZF), (_w(ZF), ZF), (SLOT_TOP_HW, ZT), (SLOT_TOP_HW, ytop),
                 (-SLOT_TOP_HW, ytop), (-SLOT_TOP_HW, ZT)]
    body -= _ex(slot_poly, -HW - 1, HW - SLOT_BACK)
    # detent bump on slot floor
    for bx in (-BUMP_X, BUMP_X):
        body += Pos(bx, BUMP_Y, ZF) * (Rot(0, 90, 0) * Cylinder(BUMP_R, 4.0))
    # countersunk screw holes
    for sx in (-SCREW_X, SCREW_X):
        body -= Pos(sx, 0, 0) * Cylinder(SCREW_D / 2, BASE_T * 3)
        csk_h = (CSK_D - SCREW_D) / 2
        body -= Pos(sx, 0, BASE_T - csk_h) * Cone(SCREW_D / 2, CSK_D / 2 + 0.01, csk_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return body


def gate() -> Part:
    k = GATE_CLR * 2 ** 0.5
    zb = ZF + GATE_CLR
    poly = [(-(_w(zb) - k), zb), ((_w(zb) - k), zb), (_w(ZT) - k, ZT), (-(_w(ZT) - k), ZT)]
    y1 = HW - SLOT_BACK - GATE_CLR
    g = _ex(poly, -HW, y1)
    for bx in (-BUMP_X, BUMP_X):
        g -= Pos(bx, BUMP_Y, zb) * (Rot(0, 90, 0) * Cylinder(BUMP_R + 0.1, 4.4))
    return Pos(GATE_SPACING + 4, HW - y1, -zb) * g


def build():
    h1, g1 = hook(), gate()
    dx = 2 * GATE_SPACING + 4
    # second set, mirrored along X spacing so footprints do not overlap
    return [h1, g1, Pos(dx + 10, 0, 0) * hook(), Pos(dx + 10, 0, 0) * gate()]
