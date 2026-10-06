"""tambourine: 200 mm headless ring tambourine, 8 jingle slots (16 jingles), finger-window grip.

Spec
- Ring frame OD 200 mm, radial wall 10 mm, height ~50 mm; printed flat (as in use, ring axis Z).
- 8 radial jingle slots spread over 270°; the remaining 90° is the grip with 4 pointed-arch
  finger windows (fingers through, thumb on the top rim).
- Each slot: straight width SLOT_L = jingle Ø + 2x3 mm clearance, straight height = 2 jingles
  + travel, then a 45° gable ceiling (no bridge > 15 mm when printed flat).
- One vertical M3 pin per slot at mid-wall: counterbore for the socket head on top, hex nut
  trap underneath. A pair of jingles (40 mm discs) rides on each pin.

TUNING
| item | target | computed dimension |
|------|--------|--------------------|
| brass jingle Ø40 x 0.8 | ring ~1.8 kHz | free circular plate (2,0) mode f = λ²/(2πR²)·√(D/ρh), λ² = 5.253, D = E·h³/(12(1−ν²)) -> f = 0.2413·(h/R²)·√(E/(ρ(1−ν²))) = 1760 Hz (E 100 GPa, ρ 8500, ν 0.34) |
| flattened steel cap Ø32 x 0.25 | ~1 kHz | same formula, E 200 GPa, ρ 7850, ν 0.30 -> ~1.2 kHz (R 16 mm) |
| jingle travel | 10 mm | slot straight height = 2·t + TRAVEL = 11.6 mm |
| slot length | Ø40 + 6 | 46 mm (jingle never touches the slot ends) |
| pin spacing | 270°/8 | 33.75° pitch, 6 mm webs at the inner face |
Real jingles are slightly domed/hammered (raises and spreads the partials); the formula gives
the flat-disc fundamental. More travel -> louder, longer "shake"; less -> tighter, drier.

Fine-tune after printing: drier sound -> add a thin rubber washer between the jingle pair or
under one jingle; brighter -> use thinner/smaller discs or tighten nothing (jingles must spin
freely on the pin, so never clamp them).

Hardware to buy: 16 jingles Ø40 mm (centre hole ≥ 3.5 mm) or 16 flattened bottle caps with a
4 mm hole punched in the centre; 8x M3x45 socket-head screws; 8x M3 hex nuts.

Assembly
1. Drop a nut into each bottom nut trap (a dab of CA glue keeps it there).
2. Hold two jingles (domes facing outward, back to back) in a slot, push an M3x45 down
   from the top counterbore through both jingles, and screw into the nut until the head
   seats. Repeat for all 8 slots.
3. Check every jingle spins and slides freely along its pin.

Assumptions
- WARN "1.6 cm2 needs support" = the 8 hex nut-trap ceilings: 5.5 mm bridges (rule ≤ 15 mm),
  kept flat so the nut seats properly; bridges print fine without support.
- Headless frame (no drum head) as requested; 40 mm jingles chosen so 8 slots + a 90° grip
  fit on a 200 mm ring (50 mm jingles would leave no grip). Change JINGLE_D to re-derive.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="Guitar Core ABS+ 0.20mm @BBL H2C",   # pinned/jingle (tension-free but impact) part
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",            # only flagged area = 5.5 mm nut-trap bridges (see docstring)
    brim="auto",
)

# Jingles (physics)
JINGLE_D = 40.0
JINGLE_T = 0.8
E_BRASS, RHO_BRASS, NU_BRASS = 100e9, 8500.0, 0.34
LAMBDA2 = 5.253           # free circular plate, mode (2,0)

# Frame
OD = 200.0
WALL = 10.0
N_SLOTS = 8
SLOT_ARC = 270.0          # deg used by slots; rest is grip
CLEAR = 3.0
TRAVEL = 10.0
BOT_RIM = 8.0
TOP_RIM = 7.0
CBORE_D, CBORE_DEPTH = 6.2, 5.0
PIN_D = 3.4
GRIP_CENTER = 270.0
N_FINGERS = 4
FINGER_W = 20.0
FINGER_H = 22.0
FINGER_WEB = 6.0

SLOT_L = JINGLE_D + 2 * CLEAR
SLOT_H = 2 * JINGLE_T + TRAVEL
GABLE = SLOT_L / 2
H = BOT_RIM + SLOT_H + GABLE + TOP_RIM
R_MID = OD / 2 - WALL / 2
F_JINGLE = (LAMBDA2 / (2 * math.pi * (JINGLE_D / 2000) ** 2) * (JINGLE_T / 1000)
            * math.sqrt(E_BRASS / (12 * RHO_BRASS * (1 - NU_BRASS ** 2))))
SCREW_L = H - CBORE_DEPTH


def arch_cutter(w, h, z0):
    """Pointed-arch window: flat bottom at z0, vertical sides h, 45° gable; through along Y."""
    pts = [(-w / 2, z0), (w / 2, z0), (w / 2, z0 + h), (0, z0 + h + w / 2), (-w / 2, z0 + h)]
    return extrude(Plane.XZ * Polygon(*pts, align=None), WALL * 3, both=True)


def build() -> Part:
    ring = Cylinder(OD / 2, H, align=ON_BED) - Pos(0, 0, -1) * Cylinder(OD / 2 - WALL, H + 2, align=ON_BED)
    ring = chamfer(ring.edges().group_by(Axis.Z)[0], 0.4)
    ring = fillet(ring.edges().group_by(Axis.Z)[-1], 2.0)

    step = SLOT_ARC / N_SLOTS
    start = GRIP_CENTER + (360 - SLOT_ARC) / 2
    for k in range(N_SLOTS):
        ang = start + (k + 0.5) * step
        cut = Pos(0, R_MID, 0) * arch_cutter(SLOT_L, SLOT_H, BOT_RIM)
        cut += Pos(0, R_MID, -1) * Cylinder(PIN_D / 2, H + 2, align=ON_BED)
        cut += Pos(0, R_MID, H) * Cylinder(CBORE_D / 2, CBORE_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MAX))
        cut += Pos(0, R_MID, 0) * Rot(180, 0, 0) * nut_trap("M3", 3.0)
        ring -= Rot(0, 0, ang - 90) * cut

    dang = math.degrees((FINGER_W + FINGER_WEB) / R_MID)
    for k in range(N_FINGERS):
        ang = GRIP_CENTER + (k - (N_FINGERS - 1) / 2) * dang
        ring -= Rot(0, 0, ang - 90) * Pos(0, R_MID, 0) * arch_cutter(FINGER_W, FINGER_H, BOT_RIM)
    return ring


if __name__ == "__main__":
    print(f"H={H:.1f} slot={SLOT_L}x{SLOT_H} f_jingle={F_JINGLE:.0f} screw~{SCREW_L:.1f}")
