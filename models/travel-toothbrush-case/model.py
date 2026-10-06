"""travel-toothbrush-case: 2-part press-fit travel case for a toothbrush + mini toothpaste tube.

Spec: closed case holds a BRUSH_LENGTH (190 mm) toothbrush with a ~20 ml travel toothpaste
tube lying alongside it. Base (long part, holds the tube) + cap join with a stepped press-fit
seam: an inner sleeve (lip) rises LIP_H above the base rim and slides into a counterbore in the
cap with FIT_CLR radial clearance. Slotted vents in both end walls let the brush dry.
Both halves are returned side by side, standing open-end up (the print orientation); they are
printed together without supports (2 separate bodies is intended).

Assumptions:
- Brush: head + bristles fit in BRUSH_W x BRUSH_D (20 x 24 mm) cross-section; handle smaller.
- Tube: ~20 ml travel tube, round body TUBE_D 24 mm, crimp end TUBE_CRIMP_W 30 mm wide,
  length TUBE_LEN 110 mm (sits in the base cavity, crimp across the width).
- Seam fit "snug" (FIT_CLR 0.15 mm per side) for a friction press fit; raise to 0.2-0.25
  if the cap is too tight on your printer.
- Inner cross-section narrows by LIP_T per side only over the 2*LIP_H seam zone; still clears
  the brush head and the tube body.
- Walls 1.6 mm (1.45 mm at the cap counterbore), end walls 1.6 mm: non-structural, kept light.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation="auto",
    supports="off",
    brim="auto",
)

# Parameters -- contents
BRUSH_LENGTH = 190.0
BRUSH_W = 20.0          # brush head width incl. margin (X)
BRUSH_D = 24.0          # head + bristles depth (Y)
TUBE_D = 24.0           # toothpaste tube body diameter
TUBE_CRIMP_W = 30.0     # crimped end width
TUBE_LEN = 110.0
END_CLR = 3.0           # length clearance at each end

# Parameters -- shell
WALL = 1.6
END_WALL = 1.6
CORNER_R = 9.0          # inner corner radius of the cavity profile
LIP_T = 1.6             # seam sleeve thickness
LIP_H = 10.0            # sleeve height above the base rim (= engagement)
FIT_CLR = 0.15          # radial press-fit clearance (snug)
SEAM_GAP = 0.3          # axial gap so the rims meet before the lip bottoms out
BASE_IN = 130.0         # base cavity depth (rim to floor)
GAP_XY = 10.0           # spacing between the two printed halves

# Parameters -- vents
VENT_L = 18.0
VENT_W = 3.0
VENT_PITCH = 6.0
VENT_N = 3

# Derived
INNER_LEN = BRUSH_LENGTH + 2 * END_CLR
CAP_IN = INNER_LEN - BASE_IN                      # cap cavity depth (rim to floor)
IN_W = BRUSH_W + TUBE_CRIMP_W + 1.0 + 2 * LIP_T       # cavity X
IN_D = max(BRUSH_D, TUBE_D + 1.0) + 2 * LIP_T          # cavity Y
OUT_W = IN_W + 2 * WALL
OUT_D = IN_D + 2 * WALL


def _prism(w, d, r, z0, h):
    return Pos(0, 0, z0) * extrude(Plane.XY * RectangleRounded(w, d, r), h)


def _vents(z_top):
    cut = Part()
    for i in range(VENT_N):
        y = (i - (VENT_N - 1) / 2) * VENT_PITCH
        for x in (-(VENT_L / 2 + 3), VENT_L / 2 + 3):
            cut += Pos(x, y, z_top) * slot(VENT_L, VENT_W, END_WALL + 2)
    return cut


def _bottom_chamfer(p):
    return chamfer(p.edges().group_by(Axis.Z)[0], 0.4)


def build_base() -> Part:
    rim = END_WALL + BASE_IN
    body = _prism(OUT_W, OUT_D, CORNER_R + WALL, 0, rim)
    body = _bottom_chamfer(body)
    # seam sleeve: cavity-profile ring rising LIP_H above the rim, rooted LIP_H below it
    sleeve_bot = rim - LIP_H
    body += _prism(IN_W, IN_D, CORNER_R, rim - 1, LIP_H + 1)
    s_w, s_d, s_r = IN_W - 2 * LIP_T, IN_D - 2 * LIP_T, CORNER_R - LIP_T
    cav = _prism(IN_W, IN_D, CORNER_R, END_WALL, sleeve_bot - END_WALL + 0.05)
    lead = loft([  # 45 deg lead-in under the sleeve (no overhang)
        Plane.XY.offset(sleeve_bot) * RectangleRounded(IN_W, IN_D, CORNER_R),
        Plane.XY.offset(sleeve_bot + LIP_T) * RectangleRounded(s_w, s_d, s_r),
    ])
    bore = _prism(s_w, s_d, s_r, sleeve_bot + LIP_T - 0.05, 2 * LIP_H)
    body -= cav
    body -= lead
    body -= bore
    body -= _vents(END_WALL)
    return body


def build_cap() -> Part:
    rim = END_WALL + CAP_IN
    body = _prism(OUT_W, OUT_D, CORNER_R + WALL, 0, rim)
    body = _bottom_chamfer(body)
    body -= _prism(IN_W, IN_D, CORNER_R, END_WALL, rim)
    # counterbore receiving the sleeve
    cb = LIP_H + SEAM_GAP
    body -= _prism(IN_W + 2 * FIT_CLR, IN_D + 2 * FIT_CLR, CORNER_R + FIT_CLR, rim - cb, cb + 1)
    body -= _vents(END_WALL)
    return body


def build():
    off = (OUT_W + GAP_XY) / 2
    return [Pos(-off, 0, 0) * build_base(), Pos(off, 0, 0) * build_cap()]
