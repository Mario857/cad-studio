"""maracas: pair of maracas, onion-shaped hollow Ø70 heads with glued-in handles.

Spec
- Head: Ø70 mm sphere band (+-45 deg latitude), 45 deg cone on top (onion tip) and a 45 deg cone
  down to the neck, so the shell prints with the filling hole down and no supports inside or outside.
  Wall 1.8 mm. Neck socket Ø20 (slide fit) = filling hole, 14 mm deep.
- Handle: Ø26 grip with a Ø30 end knob, 110 mm + Ø20 x 14 mm spigot. The spigot is glued into the
  neck and seals the filling hole flush with the cavity floor.
- build() returns 2 heads + 2 handles (one plate, 4 separate bodies intended). Both printed upright as modelled.

Assumptions
- Glue: ABS cement (ABS dissolved in acetone) or CA. Spigot slide fit 0.25 mm/side for glue.
- Rice bulk density 0.80 g/cm3, 3 mm plastic beads ~0.65 g/cm3 bulk.
- Shaking load small (~10 N at 100 mm). The Ø20 spigot sees ~2.5 MPa bending, which is fine across layers,
  so the handle is printed upright for a round surface.

TUNING (c = 343 m/s; from the computed cavity volume V = 161.5 cm3, a_eq = 33.8 mm)
| item | target | computed |
|------|--------|----------|
| closed cavity, lowest mode (rigid sphere, ka = 2.0816): f = 2.0816 c / (2 pi a_eq) | ~3.4 kHz | 3364 Hz |
| optional vent Ø5 drilled in the tip: Helmholtz f = c/(2pi) sqrt(A/(V L_eff)), L_eff = t + 1.7 r | low "whoosh" | 245 Hz |
| fill 5 % of V  (bright, crisp "tick")   | 8.1 cm3  | rice 6.5 g  / beads 5.2 g  |
| fill 10 % of V (classic)                | 16.1 cm3 | rice 12.9 g / beads 10.5 g |
| fill 20 % of V (loud, dark "shhh")      | 32.3 cm3 | rice 25.8 g / beads 21.0 g |
Head: Ø70 x 98.7 mm high (onion tip flat Ø3), handle Ø26 (knob Ø30) x 124 mm incl. spigot.
For a contrasting pair, fill one head with rice at 8 % and the other with 3 mm beads at 12 %.
Fine-tuning: shake-test before gluing, and add or remove fill. Seeds/rice are softer and darker, beads are brighter.
A thinner shell (WALL param) rings more; at least 1.6 mm keeps it robust.

Hardware to buy: ~30 g dried rice, seeds or 3 mm plastic beads per pair. ABS cement or CA glue.

Assembly: 1. Remove any brim and check the spigot slides into the neck. 2. Pour the fill through the neck
(funnel). 3. Shake-test with the handle dry-fitted. 4. Apply glue to the spigot, push it fully home, wipe the excess,
and let it cure for 12 h with the head up. 5. Repeat for the second maraca.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # heads hole-down, handles knob-down
    supports="off",
    brim="auto",
)

C_SOUND = 343.0
HEAD_D = 70.0
WALL = 1.8
NECK_H = 14.0
SPIGOT_D = 20.0
SPIGOT_FIT = "slide"
NECK_WALL = 2.5
HANDLE_L = 110.0
GRIP_D = 26.0
KNOB_D = 30.0
VENT_D = 5.0               # optional vent (documentation only)
RICE_DENSITY = 0.80        # g/cm3 bulk
BEAD_DENSITY = 0.65
FILL_FRACTIONS = (0.05, 0.10, 0.20)
SPACING = 80.0
TIP_R = 1.5                # onion tip flat radius (avoids a degenerate apex)


ARC = "arc"  # marker: true circular arc between the neighbouring points (centre given)


def _arc(r, zc, a0, a1):
    p = lambda a: (r * math.cos(math.radians(a)), zc + r * math.sin(math.radians(a)))
    return [p(a0), (ARC, (0, zc)), p(a1)]


def head_profiles():
    R = HEAD_D / 2
    r_s = clearance(SPIGOT_D, SPIGOT_FIT) / 2
    r_no = r_s + NECK_WALL
    s2 = math.sqrt(2)
    zc = NECK_H + 2 * R / s2 - r_no                 # sphere centre (45 deg cone from neck top)
    outer = ([(0, 0), (r_no - 0.4, 0), (r_no, 0.4), (r_no, NECK_H)] + _arc(R, zc, -45, 45)
             + [(TIP_R, zc + R * s2 - TIP_R), (0, zc + R * s2 - TIP_R)])
    ri = R - WALL
    # inner bottom cone parallel to the outer one: x - z = (r_no - NECK_H) - WALL*sqrt2
    c = r_no - NECK_H - WALL * s2
    z_sock = r_s - c
    inner = ([(0, -1), (r_s, -1), (r_s, z_sock)] + _arc(ri, zc, -45, 45) + [(TIP_R, zc + ri * s2 - TIP_R), (0, zc + ri * s2 - TIP_R)])
    return outer, inner, zc


def _rev(pts):
    """Revolve an (r, z) profile; (ARC, centre) entries make a true arc between neighbours."""
    edges, i = [], 0
    pts = list(pts)
    n = len(pts)
    while i < n:
        a = pts[i]
        b = pts[(i + 1) % n]
        if b[0] == ARC:
            c = pts[(i + 2) % n]
            mid_ang = (math.atan2(a[1] - b[1][1], a[0]) + math.atan2(c[1] - b[1][1], c[0])) / 2
            r = math.hypot(a[0], a[1] - b[1][1])
            m = (r * math.cos(mid_ang), b[1][1] + r * math.sin(mid_ang))
            edges.append(ThreePointArc(a, m, c))
            i += 2
        else:
            edges.append(Line(a, b))
            i += 1
    face = Face(Wire(edges))
    return revolve(Plane.XZ * face, Axis.Z, 360)


def head():
    outer, inner, _ = head_profiles()
    return _rev(outer) - _rev(inner)


def cavity_volume_cm3():
    outer, inner, _ = head_profiles()
    v = _rev(inner) & Pos(0, 0, NECK_H) * Box(200, 200, 200, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return v.volume / 1000


def handle():
    rs = SPIGOT_D / 2
    rg = GRIP_D / 2
    rk = KNOB_D / 2
    H = HANDLE_L
    pts = [(0, 0), (rk - 0.4, 0), (rk, 0.4), (rk, 6), (rg, 6 + (rk - rg)), (rg, H),
           (rs, H), (rs, H + NECK_H - 0.8), (rs - 0.8, H + NECK_H), (0, H + NECK_H)]
    return _rev(pts)


def tuning():
    V = cavity_volume_cm3() * 1e-6
    a = (3 * V / (4 * math.pi)) ** (1 / 3)
    f_mode = 2.0816 * C_SOUND / (2 * math.pi * a)
    r = VENT_D / 2e3
    A = math.pi * r * r
    f_h = C_SOUND / (2 * math.pi) * math.sqrt(A / (V * (WALL * 1e-3 + 1.7 * r)))
    fills = [(fr, V * 1e6 * fr, V * 1e6 * fr * RICE_DENSITY, V * 1e6 * fr * BEAD_DENSITY) for fr in FILL_FRACTIONS]
    return V * 1e6, a * 1e3, f_mode, f_h, fills


def build():
    h, hd = head(), handle()
    s = SPACING / 2
    return [Pos(-s, s, 0) * h, Pos(s, s, 0) * h, Pos(-s, -s, 0) * hd, Pos(s, -s, 0) * hd]


if __name__ == "__main__":
    print(tuning())
