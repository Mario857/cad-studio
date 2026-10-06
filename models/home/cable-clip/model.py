"""cable-clip: desk-edge organizer with 5 snap-in slots for 4-6 mm charging cables.

Spec: 75 mm long block, 5 keyhole slots (pitch 14 mm) running along Y, open to +Z. Each slot is a
6.2 mm round channel with a 4.4 mm entry so a cable clicks in and stays; entries have a lead-in
chamfer. Back face (z=0) has a 0.5 mm deep flat pocket for a strip of double-sided foam tape, plus
one countersunk M3 screw hole between slots 3 and 4 (alternative mounting; punch the tape there).
Printed on its front face (cable axis vertical, auto orientation): channels are vertical so no
supports; tape pocket ends are sloped 45 deg so the recess needs none either.
Assumptions: cables 4-6 mm round, soft jacket (squeezes through the 4.4 mm entry); tape pocket
60 x 8 mm; screw is M3 countersunk (flat head) from the top.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PLA",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation="auto",  # resolves to cable axis vertical: lips/channels print support-free and flex in-layer
    supports="auto",
    brim="auto",
)

# Parameters
LENGTH = 75.0        # X
DEPTH = 14.0         # Y (cable direction)
HEIGHT = 11.0        # Z
N_SLOTS = 5
PITCH = 14.0
SLOT_D = 6.2         # round channel diameter
ENTRY_W = 4.4        # snap-in opening
SLOT_FLOOR = 2.5     # wall under the cable channel (above bed)
LEADIN = 1.0         # entry chamfer size
TAPE_L = 60.0
TAPE_W = 8.0
TAPE_DEPTH = 0.5
SCREW = "M3"
SCREW_X = PITCH / 2  # between slots 3 and 4


def build() -> Part:
    part = rounded_box(LENGTH, DEPTH, HEIGHT, radius=3, top_radius=1.2)

    zc = SLOT_FLOOR + SLOT_D / 2
    r = SLOT_D / 2
    cutter = None
    for i in range(N_SLOTS):
        x = (i - (N_SLOTS - 1) / 2) * PITCH
        round_ch = Pos(x, 0, zc) * (Rot(90, 0, 0) * Cylinder(r, DEPTH + 4))
        round_ch = round_ch & Pos(x, 0, zc / 2) * Box(2 * r + 1, DEPTH + 6, zc)  # lower half only
        # upper lip: steep taper (~40 deg from vertical) from channel equator to the entry
        zt = zc + (r - ENTRY_W / 2) * 1.2
        taper = extrude(
            Plane.XZ * Polygon(
                (x - r, zc), (x + r, zc), (x + ENTRY_W / 2, zt), (x + ENTRY_W / 2, HEIGHT + 1),
                (x - ENTRY_W / 2, HEIGHT + 1), (x - ENTRY_W / 2, zt),
                align=None,
            ),
            (DEPTH + 4) / 2, both=True,
        )
        entry = taper
        # lead-in: trapezoid in XZ widening toward the top, extruded along Y
        lead = extrude(
            Plane.XZ * Polygon(
                (x - ENTRY_W / 2, HEIGHT - LEADIN),
                (x + ENTRY_W / 2, HEIGHT - LEADIN),
                (x + ENTRY_W / 2 + LEADIN + 0.2, HEIGHT + 0.2),
                (x - ENTRY_W / 2 - LEADIN - 0.2, HEIGHT + 0.2),
                align=None,
            ),
            (DEPTH + 4) / 2, both=True,
        )
        s = round_ch + entry + lead
        cutter = s if cutter is None else cutter + s
    part = part - cutter

    # tape pocket on the back face
    # (ends sloped at 45 deg along Y so the recess prints support-free with the cable axis vertical)
    pocket = extrude(
        Plane.YZ * Polygon(
            (-TAPE_W / 2 - TAPE_DEPTH, -0.01), (TAPE_W / 2 + TAPE_DEPTH, -0.01),
            (TAPE_W / 2, TAPE_DEPTH), (-TAPE_W / 2, TAPE_DEPTH), align=None,
        ),
        TAPE_L / 2, both=True,
    )
    part = part - pocket

    # countersunk M3 screw hole from the top (cutter points down from z=0 -> place at top)
    part = part - Pos(SCREW_X, 0, HEIGHT) * bolt_hole(SCREW, HEIGHT, head="csk")
    return part
