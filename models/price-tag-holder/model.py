"""price-tag-holder: shelf-edge clip-on holder for a 60x40 mm price tag, 18-20 mm shelves, set of 10.

Spec: C-clip whose two 25 mm legs taper from a 20.6 mm root gap to a 17.6 mm tip gap (with
flared lead-ins) so they spring onto any 18-20 mm shelf edge. The front plate carries a tag
pocket: 0.8 mm gap behind 3 mm top/bottom lips, tag slides in from the left and stops at a
right-hand end stop. Printed on its side (profile on the bed) so the legs flex along the layers
and the pocket lips print without overhangs. copies=10.

MEASURE BEFORE PRINTING: shelf thickness (18-20 mm; else change GAP_ROOT/GAP_TIP), tag size
TAG_W x TAG_H (60x40) and thickness (<= 0.6 mm paper/card).
Assumptions: shelf front edge square; tag centred on the shelf edge height.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],
    print_orientation=(0, 90, 0),   # on its side: X (width) vertical
    supports="off",
    brim="on",                      # 63 mm tall on a 3.3 cm2 footprint
    copies=10,
)

# Parameters
TAG_W = 60.0
TAG_H = 40.0
TAG_CLEAR = 1.0          # total, height of the pocket
TAG_GAP = 0.8            # pocket thickness
LIP_OVER = 3.0           # lip overlap on the tag face
LIP_T = 1.5
PLATE_T = 2.5
END_STOP = 2.0
GAP_ROOT = 20.6          # leg gap at the plate
GAP_TIP = 17.6           # leg gap at the tips -> grips 18-20 mm
LEG_L = 25.0
LEG_T = 2.4
FLARE = 1.5              # lead-in at the leg tips
FLARE_L = 3.0


def build() -> Part:
    width = TAG_W + END_STOP + 1.0
    pocket_h = TAG_H + TAG_CLEAR
    zc = GAP_ROOT / 2
    zb, zt = zc - pocket_h / 2 - LIP_T, zc + pocket_h / 2 + LIP_T
    yf = -PLATE_T - TAG_GAP - LIP_T          # front face of the lips

    d = (GAP_ROOT - GAP_TIP) / 2
    lt = LEG_L - FLARE_L
    zl = d * lt / LEG_L                      # inner leg rise at flare start
    bottom_leg = Polygon((0, -LEG_T), (lt, zl - LEG_T), (LEG_L, zl - LEG_T - FLARE),
                         (LEG_L, zl - FLARE + 0.8), (lt, zl), (0, 0), align=None)
    top_leg = Polygon((0, GAP_ROOT + LEG_T), (lt, GAP_ROOT - zl + LEG_T), (LEG_L, GAP_ROOT - zl + LEG_T + FLARE),
                      (LEG_L, GAP_ROOT - zl + FLARE - 0.8), (lt, GAP_ROOT - zl), (0, GAP_ROOT), align=None)
    plate = Polygon((-PLATE_T, zb), (0.01, zb), (0.01, zt), (-PLATE_T, zt), align=None)
    lip_b = Polygon((yf, zb), (-PLATE_T + 0.01, zb), (-PLATE_T + 0.01, zb + LIP_T),
                    (yf + LIP_T, zb + LIP_T), (yf + LIP_T, zb + LIP_T + LIP_OVER), (yf, zb + LIP_T + LIP_OVER), align=None)
    lip_t = Polygon((yf, zt), (-PLATE_T + 0.01, zt), (-PLATE_T + 0.01, zt - LIP_T),
                    (yf + LIP_T, zt - LIP_T), (yf + LIP_T, zt - LIP_T - LIP_OVER), (yf, zt - LIP_T - LIP_OVER), align=None)
    prof = bottom_leg + top_leg + plate + lip_b + lip_t
    part = extrude(Plane.YZ * prof, width / 2, both=True)
    # end stop closing the pocket on the right
    stop = Pos(width / 2 - END_STOP / 2, (yf - PLATE_T) / 2, zc) * Box(END_STOP, -yf - PLATE_T + 0.02, pocket_h + 0.02)
    part += stop
    return part
