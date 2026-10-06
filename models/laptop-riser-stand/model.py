"""laptop-riser-stand: foldable, vented, tilting laptop riser for 13-16 in laptops.

Spec
- Vented platform 270 x 200 x 5 mm with a 10 mm front lip; laptop rests against the lip.
- Two legs, each 3 pinned links (side-frame triangle, in-use YZ plane):
    A  base bar on the desk (14 thick, 2 rubber-foot pockets, holes F, N_HIGH, N_LOW)
    C  top rail, hinged to A at the front pivot F; platform sits on its top edge,
       located by 2 tabs that drop into through-slots in the platform
    B  prop strut, hinged to C at P; its foot is pinned into A at N_HIGH or N_LOW
- Heights (rear top edge of platform above desk): 110 mm (tilt ~30 deg) / 60 mm (tilt ~13 deg).
- Lateral layer order per leg (from centre outward): C (x=+-100) | B | A.
- Folded pack: remove the A-B pins, fold B onto C and C onto A (all links horizontal,
  14 mm tall on edge), flip each leg over and drop the C tabs into the platform slots from
  the top side: pack = 5 mm platform + 14 mm legs = 19 mm (lip is only 10 mm, legs sit behind it).
- Tip angles with a 2 kg laptop (CoM mid-laptop, 250 mm deep, ~16 mm thick), computed in
  tip_angles(): 44 deg (110 mm) and 53 deg (60 mm) worst case (requirement >= 12 deg).
  Not run through the audit because build() returns the flat print layout, not the assembly.

Printed as one plate, flat (layout coords, not in-use coords): 7 separate bodies are intended
(platform + 2xA + 2xB + C + mirrored C).

Hardware (per stand): 2x M4x30 + nyloc (A-C front hinge, through C, C-boss, A);
  2x M4x14 + M4 nut in B's flush nut trap (B-C hinge, head on C's inner side);
  2x M4x25 + wing nut (removable A-B height pin); 4x 8 mm dia x 2 mm self-adhesive rubber bumpers.

Assumptions
- "Height" = rear top edge of the platform above the desk; the platform is tilted (typical riser).
- Laptop up to ~360 x 250 mm overhangs the 270 x 200 platform at the sides/rear (fine for a riser).
- PLA-TOUGH chosen for hinge toughness; legs print flat so link bending runs along the layers.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="PLA-TOUGH",
    quality="standard",
    standing=False,            # print layout; in-use tip angles computed analytically (see docstring)
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
)

# --- Parameters -------------------------------------------------------------
PLAT_W = 270.0        # platform width (X, across laptop)
PLAT_D = 200.0        # platform depth along slope
PLAT_T = 5.0          # platform thickness
LIP_H = 10.0          # front lip height above platform
LIP_T = 5.0
PLAT_FRONT = -15.0    # platform front edge, along-rail coordinate u (F pivot at u=0)

LINK_H = 14.0         # link depth (in-use vertical) = folded pack height of legs
PIVOT_Z = LINK_H / 2  # pivot axis height above desk / mid of link
T_C = 6.0             # rail thickness
T_B = 8.0             # strut thickness
T_A = 14.0            # base bar thickness (wide foot)
RAIL_X = 100.0        # rail centre |x|

P_U = 175.0           # B-C pivot distance along rail from F
A_LEN = 185.0         # base bar rear end (u)
HEIGHTS = (110.0, 60.0)

TAB_U = (40.0, 140.0) # C tabs (centres along u)
TAB_L = 15.0
TAB_H = 4.0
SLOT_CLR = 0.5

PIN_D = hole_d(clearance(4, "slide"))   # M4 pivot holes
FOOT_D = 8.0          # rubber bumper diameter
FOOT_DEPTH = 1.5
FOOT_U = (10.0, 176.0)

VENT_W = 6.0
VENT_PITCH = 12.0
VENT_X_MAX = 84.0
VENT_SPANS = ((30.0, 95.0), (110.0, 175.0))   # along u

GAP = 4.0             # gap between parts on the plate


# --- Geometry of the linkage -------------------------------------------------
def tilt_for(height):
    """Rail angle so the platform's rear top edge sits at `height`."""
    u_r = PLAT_FRONT + PLAT_D
    off = LINK_H / 2 + PLAT_T
    lo, hi = 0.0, math.pi / 3
    for _ in range(60):
        th = (lo + hi) / 2
        z = PIVOT_Z + u_r * math.sin(th) + off * math.cos(th)
        lo, hi = (th, hi) if z < height else (lo, th)
    return th


TH_HI, TH_LO = (tilt_for(h) for h in HEIGHTS)
B_LEN = P_U * math.sin(TH_HI)                      # strut vertical in high position
N_HI = P_U * math.cos(TH_HI)
N_LO = P_U * math.cos(TH_LO) - math.sqrt(B_LEN**2 - (P_U * math.sin(TH_LO)) ** 2)


def tip_angles(laptop_d=250.0, laptop_t=16.0):
    out = {}
    for h, th in zip(HEIGHTS, (TH_HI, TH_LO)):
        uc = PLAT_FRONT + LIP_T + laptop_d / 2
        off = LINK_H / 2 + PLAT_T + laptop_t / 2
        s = uc * math.cos(th) - off * math.sin(th)
        z = PIVOT_Z + uc * math.sin(th) + off * math.cos(th)
        x_foot = RAIL_X + T_C / 2 + T_B + T_A / 2
        front = math.degrees(math.atan2(s - FOOT_U[0], z))
        rear = math.degrees(math.atan2(FOOT_U[1] - s, z))
        side = math.degrees(math.atan2(x_foot, z))
        out[h] = round(min(front, rear, side), 1)
    return out


assert N_LO - 10 > 0 and N_HI - N_LO > 12
assert P_U - B_LEN > 20                            # folded B clears the F hub
# low-position A-B pin (nut on B inner side) must clear the rail above it
assert N_LO * math.tan(TH_LO) - (LINK_H / 2) / math.cos(TH_LO) > 5
assert min(tip_angles().values()) >= 12


# --- Parts (built directly in print layout: X = along link, Y = in-use Z) -----
def pin(x, y, h):
    return Pos(x, y, h) * Cylinder(PIN_D / 2, h + 2, align=(Align.CENTER, Align.CENTER, Align.MAX))


def stadium(x0, x1, t):
    """Bar with round ends centred on pivots x0, x1; bottom edge at y=0, depth LINK_H."""
    sk = Pos((x0 + x1) / 2, PIVOT_Z) * SlotCenterToCenter(x1 - x0, LINK_H)
    return extrude(sk, t)


def bevel_bottom(p):
    try:
        return chamfer(p.edges().group_by(Axis.Z)[0], 0.4)
    except Exception:
        return p


def part_a():
    sk = Pos(0, PIVOT_Z) * Circle(LINK_H / 2) + Pos(A_LEN / 2, PIVOT_Z) * Rectangle(A_LEN, LINK_H)
    p = bevel_bottom(extrude(sk, T_A))
    for u in (0.0, N_HI, N_LO):
        p -= pin(u, PIVOT_Z, T_A)
    for u in FOOT_U:   # rubber-foot pockets in the desk face (print y=0), teardrop for no support
        p -= Pos(u, 0, T_A / 2) * teardrop_hole(FOOT_D, 2 * FOOT_DEPTH, along="Y")
    return p


def part_b():
    p = bevel_bottom(stadium(0, B_LEN, T_B))
    p -= pin(0, PIVOT_Z, T_B) + pin(B_LEN, PIVOT_Z, T_B)
    p -= Pos(B_LEN, PIVOT_Z, T_B) * nut_trap("M4", METRIC["M4"]["nut_h"] + 0.2)
    return p


def part_c():
    p = stadium(0, P_U, T_C)
    for u in TAB_U:
        p += Pos(u, LINK_H, 0) * Box(TAB_L, TAB_H, T_C, align=(Align.CENTER, Align.MIN, Align.MIN))
    p = bevel_bottom(p)
    p += Pos(0, PIVOT_Z, T_C) * Cylinder(LINK_H / 2, T_B, align=(Align.CENTER, Align.CENTER, Align.MIN))
    p -= pin(0, PIVOT_Z, T_C + T_B) + pin(P_U, PIVOT_Z, T_C)
    return p


def platform():
    # print y = u - PLAT_FRONT, x centred
    p = Pos(0, PLAT_D / 2, 0) * Box(PLAT_W, PLAT_D, PLAT_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    p = fillet(p.edges().filter_by(Axis.Z), 6)
    p = bevel_bottom(p)
    p += Pos(0, LIP_T / 2, PLAT_T) * Box(PLAT_W - 12, LIP_T, LIP_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cut = None
    for sx in (-1, 1):
        for u in TAB_U:
            c = Pos(sx * RAIL_X, u - PLAT_FRONT, PLAT_T + 1) * Box(
                T_C + SLOT_CLR, TAB_L + SLOT_CLR, PLAT_T + 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
            cut = c if cut is None else cut + c
    n = int(2 * VENT_X_MAX // VENT_PITCH) + 1
    x0 = -(n - 1) * VENT_PITCH / 2
    for i in range(n):
        for u0, u1 in VENT_SPANS:
            c = Pos(x0 + i * VENT_PITCH, (u0 + u1) / 2 - PLAT_FRONT, PLAT_T + 1) * Rot(0, 0, 90) * slot(
                u1 - u0, VENT_W, PLAT_T + 2)
            cut += c
    return p - cut


def build():
    plat = platform()
    a, b, c = part_a(), part_b(), part_c()
    c_m = mirror(c, about=Plane.XZ)          # other-hand rail (tabs/boss mirrored)
    y = -160.0 + 8.0                          # plate front margin
    x_left = -PLAT_W / 2 + 10
    parts = []
    # rows of links, then platform behind them
    parts.append(Pos(x_left + LINK_H / 2, y, 0) * a); y += LINK_H + GAP
    parts.append(Pos(x_left + LINK_H / 2, y, 0) * a); y += LINK_H + GAP
    parts.append(Pos(x_left + LINK_H / 2, y, 0) * c); y += LINK_H + TAB_H + GAP
    parts.append(Pos(x_left + LINK_H / 2, y + LINK_H + TAB_H, 0) * c_m); y += LINK_H + TAB_H + GAP
    parts.append(Pos(x_left + LINK_H / 2, y, 0) * b)
    parts.append(Pos(x_left + LINK_H / 2 + B_LEN + LINK_H + GAP, y, 0) * b); y += LINK_H + GAP + 1
    parts.append(Pos(0, y, 0) * plat)
    return parts


if __name__ == "__main__":
    print(f"tilt hi {math.degrees(TH_HI):.1f} lo {math.degrees(TH_LO):.1f}  B {B_LEN:.1f} "
          f"N_HI {N_HI:.1f} N_LO {N_LO:.1f}  tip {tip_angles()}")
