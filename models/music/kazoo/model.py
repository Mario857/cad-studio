"""kazoo: playable kazoo with a snap-on cap that clamps a 25 mm membrane disc.

Spec
- Straight body tube (open-open pipe) with a teardrop-section bore (D 17 mm circle + 45 deg roof with a 0.2 mm tip flat,
  tube OD 27.0) so the horizontal airway prints with no overhang inside.
- Turret (OD 26, membrane seat ID 18) on top of the tube; the Ø25 mm membrane disc lies on the seat rim
  and is clamped by a snap cap (OD 30, 45 deg snap bead/groove, 4 relief slots, Ø18 sound opening).
- Body length is derived from the target body resonance F_BODY (open-open pipe):
      f1 = c / (2 (L + 2 * 0.61 r))  ->  L = c / (2 f1) - 1.22 r ,  c = 343 m/s, r = bore radius.
- You hum/sing "doo" into the mouth end; the voice sets the pitch, the membrane adds the buzz, and the
  tube resonances act as formants (they colour the buzz, they do not set the note).

Assumptions
- Mouth end treated as open (lips around the 27 mm tube end, nearly open while humming), far end open.
- Membrane: baking paper (~40 g/m2, ~0.05 mm) or 0.05 mm PE/PET film; tension ~ 20-60 N/m when clamped.
- 2 bodies (body + cap) intended. Printed in use orientation (turret up) on the flat 45 deg keel; cap printed flange-down beside it.
- ABS is not food-safe — personal use, rinse after playing.

TUNING (formants; c = 343 m/s)
| item | target Hz | computed dimension |
|------|-----------|--------------------|
| tube f1 (open-open)            | 1400 | L = 343/(2*1400) - 1.22*8.5 = 112.1 mm |
| tube f2 = 2 f1                 | 2800 | (same tube)                             |
| tube f3 = 3 f1                 | 4200 | (same tube)                             |
| membrane f01 = 2.405/(2 pi a) sqrt(T/sigma), a = 9 mm, sigma = 0.04 kg/m2 | ~600-1050 | T = 20..60 N/m |
| turret neck (Helmholtz-like vent under membrane) | n/a | Ø18 x 8 mm, open via membrane |
Fine-tuning: a buzzier/brighter sound needs a slacker or thinner membrane (lower f01). A louder, purer
"trumpet" needs it tighter. Lower formant: lengthen L (F_BODY param) or tape a paper tube on the far end.
Raise the formant: sand the far end shorter (1 mm ~ +12 Hz on f1).

Hardware to buy: baking paper / 0.05 mm film, cut 1 disc Ø25 mm (spares advised). Optional: scissors,
compass-cutter or Ø25 punch.

Assembly: 1. Cut the Ø25 disc (smooth edge). 2. Lay it on the turret rim, keeping it flat with no wrinkles. 3. Press the cap
straight down until it snaps over the bead (slots flex). 4. Hum "doo" into the end farther from the turret.
5. To change the membrane, lever the cap off at a slot.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",            # mouth airway
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # turret up, bore horizontal teardrop
    supports="off",
    brim="auto",
)

# acoustics
C_SOUND = 343.0            # m/s
F_BODY = 1400.0            # target tube fundamental (formant), Hz
BORE_D = 17.0
END_CORR = 0.61            # x r per open end
# membrane (documentation + seat geometry)
MEMBRANE_D = 25.0
SEAT_ID = 18.0             # free membrane diameter
MEMBRANE_SIGMA = 0.04      # kg/m2 (baking paper)
# body
WALL = 1.6
ROOF_FLAT = 0.2           # width of the flat at the teardrop tip (bridge)
ROOF = BORE_D / 2 * (math.sqrt(2) - 1) - ROOF_FLAT / 2   # teardrop height above the bore circle
TURRET_FRAC = 0.58         # turret centre from mouth end (fraction of L)
TURRET_OD = 26.0
TURRET_H = 8.0             # above tube top
# snap cap
SNAP_Z = 3.0               # bead centre below turret top
BEAD = 0.5
CAP_WALL = 1.8
CAP_TOP = 1.6
SLOTS = 4
SLOT_W = 1.5
SLOT_D = 3.5


def tube_length():
    r = BORE_D / 2 / 1000
    return (C_SOUND / (2 * F_BODY) - 2 * END_CORR * r) * 1000


def membrane_f01(tension):
    a = SEAT_ID / 2 / 1000
    return 2.405 / (2 * math.pi * a) * math.sqrt(tension / MEMBRANE_SIGMA)


def build():
    L = tube_length()
    rb = BORE_D / 2
    ro = rb + ROOF + WALL
    zc = ro
    k = ro * math.sqrt(0.5)
    n = 72
    # outer section: circle arc + 45 deg keel down to a flat bottom (one polygon)
    arc = [(ro * math.cos(math.radians(a)), zc + ro * math.sin(math.radians(a)))
           for a in [-45 + 270 * i / n for i in range(n + 1)]]
    outer = Polygon(*arc, (-(k - (zc - k)), 0), (k - (zc - k), 0), align=None)
    # inner teardrop (roof 45 deg), truncated ROOF above the bore circle
    zt = zc + rb + ROOF
    hw = rb * math.sqrt(2) - (rb + ROOF)          # half width at the truncation
    arc_i = [(rb * math.cos(math.radians(a)), zc + rb * math.sin(math.radians(a)))
             for a in [135 + 270 * i / n for i in range(n + 1)]]
    tear = Polygon(*arc_i, (hw, zt), (-hw, zt), align=None)
    body = Pos(L / 2, 0, 0) * extrude(Plane.YZ * outer, L / 2, both=True)
    body = body - Pos(L / 2, 0, 0) * extrude(Plane.YZ * tear, L / 2 + 1, both=True)

    # turret with 45 deg flare underneath
    xt = TURRET_FRAC * L
    rt = TURRET_OD / 2
    z_tube_top = 2 * ro
    z_top = z_tube_top + TURRET_H
    flare = 6.0
    turret = revolve(Plane.XZ * Polygon((0, z_tube_top - flare), (rt - flare, z_tube_top - flare),
                                        (rt, z_tube_top), (rt, z_top), (0, z_top), align=None),
                     Axis.Z, 360)
    bead = revolve(Plane.XZ * Polygon((rt - 0.01, z_top - SNAP_Z - BEAD), (rt + BEAD, z_top - SNAP_Z),
                                      (rt - 0.01, z_top - SNAP_Z + BEAD), align=None), Axis.Z, 360)
    turret = Pos(xt, 0, 0) * (turret + bead)
    body = body + turret
    body = body - Pos(xt, 0, zc + 2) * Cylinder(SEAT_ID / 2, z_top - zc, align=ON_BED)
    body = body - Pos(xt, 0, zc) * Cylinder(SEAT_ID / 2 - 2, 3, align=ON_BED)

    # cap (in use: flange on top of the membrane)
    ri = clearance(TURRET_OD, "snug") / 2
    rco = ri + CAP_WALL
    skirt = SNAP_Z + BEAD + 1.5
    cap = revolve(Plane.XZ * Polygon((SEAT_ID / 2, z_top + CAP_TOP), (rco, z_top + CAP_TOP),
                                     (rco, z_top - skirt), (ri, z_top - skirt), (ri, z_top),
                                     (SEAT_ID / 2, z_top), align=None), Axis.Z, 360)
    g = BEAD + 0.1
    groove = revolve(Plane.XZ * Polygon((ri - 0.01, z_top - SNAP_Z - g - 0.2), (ri + g, z_top - SNAP_Z),
                                        (ri - 0.01, z_top - SNAP_Z + g + 0.2), align=None), Axis.Z, 360)
    cap = cap - groove
    for i in range(SLOTS):
        cap = cap - Rot(0, 0, i * 360 / SLOTS + 45) * Pos(rco - CAP_WALL / 2, 0, z_top - skirt - 0.5) * Box(
            CAP_WALL + 2, SLOT_W, SLOT_D + 0.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # print flange-down beside the body; 0.4 mm chamfer on the bed edge
    cap = Rot(180, 0, 0) * cap
    bb = cap.bounding_box()
    cap = Pos(xt, ro + rco + 6, -bb.min.Z) * cap
    cap = chamfer(cap.edges().group_by(Axis.Z)[0].sort_by(SortBy.RADIUS)[-1], 0.4)
    return [body, cap]


if __name__ == "__main__":
    L = tube_length()
    print(f"L = {L:.1f} mm, f1 {F_BODY}, f2 {2*F_BODY}, f3 {3*F_BODY}")
    for T in (20, 40, 60):
        print(f"membrane T={T} N/m -> f01 {membrane_f01(T):.0f} Hz")
