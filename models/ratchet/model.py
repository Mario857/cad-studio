"""ratchet: football-rattle noisemaker - 12-tooth gear on a handle, frame with a flexing tongue.

Spec
- Handle part: Ø30 x 84 mm grip, 45° cone up to a 12-tooth triangular gear (tip Ø60, root
  Ø52, 12 mm thick), Ø18 thrust boss, Ø12 axle with an M3 heat-set insert in its top.
- Frame part: 130 x 72 x 18 mm open box that spins on the axle (Ø12.5 bearing hole in a 24 mm
  top bar). A 1.8 mm thick, 60 mm long tongue runs radially from the far end wall to the gear;
  its rounded tip overlaps the tooth tips by ENGAGE = 1.0 mm, so each tooth bends it sideways and
  it snaps back onto the next flank -> click. Symmetric teeth: clicks in both directions.
- Cap: Ø24 x 3 mm washer, clamped to the axle top by an M3x8 screw (axle stands 0.3 mm proud of
  the frame, so the frame turns freely between cap and boss).
- Strength: the tongue is a vertical wall in print, so it bends WITHIN the layers (no layer
  peel). The frame is laid out upside-down (bar on the bed); parts are in print orientation.

TUNING
| item | target | computed |
|------|--------|----------|
| click rate | 36 /s at 3 rev/s | N_TEETH x rev/s |
| tongue natural freq | > click rate | f = 0.1615·(t/L²)·√(E/ρ) = 115 Hz (t 1.8, L 60 mm, ABS E 2.1 GPa, ρ 1040) |
| max clean click rate | ~115 /s | tongue must ring back within one tooth: rev/s < f/N ≈ 9.6 |
| clear-tooth deflection | – | tip foreshortening 0.6·y²/L = ENGAGE -> y = 10.0 mm |
| tongue preload force | – | F = 3EI·y/L³ = 2.6 N at y (I = h·t³/12, h 18 mm) |
| root strain | < 1 % | ε = 3·t·y/(2L²) = 0.75 % (ABS yield ~2-3 %) |

Fine-tune after printing: louder/harder clicks -> increase engagement by shimming the tip with
a strip of tape (or reprint with ENGAGE 1.3); softer/easier -> sand the tip back 0.3 mm. The open
frame box is the sound board: glue a 1 mm card or printed plate over the top to make it louder.

Hardware to buy: 1x M3 heat-set insert (M3 x 5.7 mm), 1x M3x8 screw (button/socket), a drop of
light oil or PTFE dry lube for the axle.

Assembly
1. Melt the M3 insert into the axle top with a soldering iron (~230 °C for ABS).
2. Slide the frame (bar side up) over the axle; the tongue tip lands between gear teeth.
3. Put the cap on and screw M3x8 into the insert until snug; frame must spin freely.
4. Hold the grip, whirl the hand in small circles: the frame trails and rattles.

Assumptions
- 1.8 mm ABS tongue at 0.75 % strain tolerates long use; if it whitens, reprint with longer
  TONGUE_L (strain falls with 1/L) - all values re-derive.
- Quality "strong" (rotating/flexing part, no tension strings).
- WARN "separate bodies" is intended (3-part kit).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # parts laid out in print orientation
    supports="off",
    brim="auto",
)

# Mechanics / physics
N_TEETH = 12
REV_S = 3.0
E_ABS = 2.1e9
RHO_ABS = 1040.0
ENGAGE = 1.0

# Handle / gear
GRIP_D = 30.0
GRIP_L = 84.0
R_TIP = 30.0
TOOTH_H = 4.0
GEAR_T = 12.0
BOSS_D, BOSS_H = 18.0, 0.5
AXLE_D = 12.0
AXLE_CLEAR = 0.5

# Frame / tongue
TONGUE_T = 1.8
TONGUE_L = 60.0
SIDE_WALL = 4.0
END_WALL = 5.0
BAR_T = 6.0
BAR_W = 24.0
CAP_D, CAP_T = 24.0, 3.0
PROUD = 0.3

R_WIN = R_TIP + 2.0
FRAME_LOW = GEAR_T + BOSS_H - 0.5        # lower layer height (gear zone)
FRAME_H = FRAME_LOW + BAR_T
X_TIP = R_TIP - ENGAGE
X_ROOT = X_TIP + TONGUE_L
F_TONGUE = 0.1615 * (TONGUE_T / 1000) / (TONGUE_L / 1000) ** 2 * math.sqrt(E_ABS / RHO_ABS)
Y_CLEAR = math.sqrt(ENGAGE * TONGUE_L / 0.6)
I_T = FRAME_H * TONGUE_T ** 3 / 12
F_PRELOAD = 3 * (E_ABS / 1e6) * I_T * Y_CLEAR / TONGUE_L ** 3
STRAIN = 3 * TONGUE_T * Y_CLEAR / (2 * TONGUE_L ** 2)


def handle():
    h = Cylinder(GRIP_D / 2, GRIP_L, align=ON_BED)
    h = chamfer(h.edges().group_by(Axis.Z)[0], 0.4)
    cone_h = R_TIP - GRIP_D / 2
    h += Pos(0, 0, GRIP_L) * Cone(GRIP_D / 2, R_TIP, cone_h, align=ON_BED)
    z = GRIP_L + cone_h
    pts = []
    for i in range(N_TEETH):
        a0 = 2 * math.pi * i / N_TEETH
        a1 = 2 * math.pi * (i + 0.5) / N_TEETH
        pts += [(R_TIP * math.cos(a0), R_TIP * math.sin(a0)),
                ((R_TIP - TOOTH_H) * math.cos(a1), (R_TIP - TOOTH_H) * math.sin(a1))]
    h += extrude(Plane.XY.offset(z) * Polygon(*pts, align=None), GEAR_T)
    z += GEAR_T
    h += Pos(0, 0, z) * Cylinder(BOSS_D / 2, BOSS_H, align=ON_BED)
    z += BOSS_H
    axle_len = BAR_T + PROUD
    h += Pos(0, 0, z) * Cylinder(AXLE_D / 2, axle_len, align=ON_BED)
    top = z + axle_len
    h -= Pos(0, 0, top) * insert_hole("M3")
    return h


def frame():
    """Built in PRINT orientation: z 0..BAR_T is the (in-use top) bar layer."""
    x0, x1 = -(R_WIN + SIDE_WALL), X_ROOT + END_WALL
    w = 2 * (R_WIN + SIDE_WALL)
    f = Pos((x0 + x1) / 2, 0, 0) * rounded_box(x1 - x0, w, FRAME_H, radius=6)
    win = Cylinder(R_WIN, FRAME_H + 2, align=ON_BED)
    win += Pos(X_ROOT / 2, 0, 0) * Box(X_ROOT, 2 * R_WIN, FRAME_H + 2, align=ON_BED)
    win = Pos(0, 0, -1) * win
    win -= Box(BAR_W, w + 2, BAR_T + 1, align=ON_BED)
    f -= win
    f -= Pos(0, 0, -1) * Cylinder((AXLE_D + AXLE_CLEAR) / 2, BAR_T + 2, align=ON_BED)
    f -= Pos(0, 0, -0.01) * Cone((AXLE_D + AXLE_CLEAR) / 2 + 0.5, (AXLE_D + AXLE_CLEAR) / 2, 0.5, align=ON_BED)
    tl = X_ROOT + 1 - (X_TIP + TONGUE_T / 2)
    f += Pos(X_TIP + TONGUE_T / 2 + tl / 2, 0, 0) * Box(tl, TONGUE_T, FRAME_H, align=ON_BED)
    f += Pos(X_TIP + TONGUE_T / 2, 0, 0) * Cylinder(TONGUE_T / 2, FRAME_H, align=ON_BED)
    return f


def cap():
    c = Cylinder(CAP_D / 2, CAP_T, align=ON_BED)
    c = chamfer(c.edges().group_by(Axis.Z)[0], 0.4)
    return c - Pos(0, 0, -1) * Cylinder(1.7, CAP_T + 2, align=ON_BED)


def build():
    return [Pos(-75, 0, 0) * handle(), Pos(20, 0, 0) * frame(), Pos(-75, 60, 0) * cap()]


if __name__ == "__main__":
    print(f"clicks={N_TEETH*REV_S:.0f}/s f_tongue={F_TONGUE:.0f}Hz y={Y_CLEAR:.1f} "
          f"F={F_PRELOAD:.2f}N strain={STRAIN*100:.2f}% frame={X_ROOT+END_WALL+R_WIN+SIDE_WALL:.0f}x{2*(R_WIN+SIDE_WALL):.0f}x{FRAME_H}")
