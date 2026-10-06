"""receipt-wall-clip: wall-mounted spring-flex receipt clip, set of 3 (TO PAY / PAID / FILE).

Spec: back plate screwed to the wall through a keyhole slot (hang on a pan/round-head screw, slide
down). A flexible tongue springs up from a U-bend at the bottom and presses against the back plate
near its top; the tip flares outward as a lead-in. Push receipts down between tongue and plate:
holds from a single slip up to a 15 mm stack (tongue deflects ~15 mm, ~1.6 % strain in ABS).
The category name is raised on the tongue front. Printed on its side (print_orientation) so the
U-bend and tongue flex along the layers.

Assumptions: wall screw Ø3.5-4 mm with head <= 8.5 mm (e.g. 4 x 30 pan head + wall plug).
MEASURE BEFORE PRINTING: screw head diameter (must pass KH_HEAD_D, not KH_SLOT_W).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[],
    print_orientation=(0, 90, 0),   # on its side: the bend/tongue lie in the layer plane
    supports="off",                 # only the 10 mm keyhole-slot bridge + raised-letter undersides
    brim="on",                      # ABS, 60 mm tall on a narrow edge
)

LABELS = ["TO PAY", "PAID", "FILE"]

# Clip
WIDTH = 60.0           # along the wall (X)
PLATE_T = 5.0
PLATE_H = 100.0
TONGUE_T = 2.6
BEND_GAP = 17.0        # gap at the U-bend (> MAX_STACK)
MAX_STACK = 15.0
PRELOAD_GAP = 0.6      # tongue-to-plate gap at rest (contact line)
CONTACT_Z = 70.0       # height of the contact line
TONGUE_TOP = 80.0      # top of the flared lead-in
FLARE = 6.0            # lead-in opening at the top
TEXT_SIZE = 6.0
TEXT_DEPTH = 0.6

# Keyhole (fits)
KH_HEAD_D = 9.0        # screw head passes here
KH_SLOT_W = 4.6        # screw shank slot
KH_SLOT_L = 10.0       # slide distance
KH_RECESS = 2.5        # head channel depth from the wall side
KH_Z = 88.0            # entry-hole centre height


def profile():
    """2D side profile in (Y, Z); wall at y = 0, clip extends to -Y."""
    t, g = PLATE_T, BEND_GAP
    r_in, r_out = g / 2, g / 2 + TONGUE_T
    zb = r_out
    yc = -t - g / 2
    plate = Pos(-t / 2, PLATE_H / 2) * Rectangle(t, PLATE_H)
    ring = Pos(yc, zb) * (Circle(r_out) - Circle(r_in))
    ring = ring & Pos(yc, zb / 2) * Rectangle(2 * r_out + 2, zb)
    y_in_b = -t - g
    tongue = Polygon(
        (y_in_b, zb - 1.0), (-t - PRELOAD_GAP, CONTACT_Z), (-t - FLARE, TONGUE_TOP),
        (-t - FLARE - TONGUE_T, TONGUE_TOP), (-t - PRELOAD_GAP - TONGUE_T, CONTACT_Z),
        (y_in_b - TONGUE_T, zb - 1.0), align=None)
    return plate + ring + tongue


def make_clip(text: str) -> Part:
    clip = extrude(Plane.YZ * profile(), WIDTH / 2, both=True)

    # keyhole: teardrop entry (point toward -X = up when printed), shank slot, 45 deg head channel
    entry = Rot(0, -90, 0) * teardrop_hole(KH_HEAD_D, PLATE_T * 3, along="Y")
    slot_top = KH_Z + KH_SLOT_L
    slot = Pos(0, -PLATE_T / 2, (KH_Z + slot_top) / 2) * Box(KH_SLOT_W, PLATE_T * 3, KH_SLOT_L)
    slot += Pos(0, 0, slot_top) * Rot(90, 0, 0) * Cylinder(KH_SLOT_W / 2, PLATE_T * 3)
    w0, w1 = KH_HEAD_D + 0.4, KH_HEAD_D + 0.4 + 2 * KH_RECESS
    chan = Polygon((-w1 / 2, 0.5), (w1 / 2, 0.5), (w0 / 2, -KH_RECESS), (-w0 / 2, -KH_RECESS), align=None)
    chan = Pos(0, 0, KH_Z) * extrude(Plane.XY * chan, KH_SLOT_L + KH_HEAD_D / 2)
    clip -= Pos(0, 0, KH_Z) * entry + slot + chan

    # label on the tongue's outer face
    zm = (2 * BEND_GAP / 2 + CONTACT_Z) / 2 + 4
    dy, dz = BEND_GAP - PRELOAD_GAP, CONTACT_Z - (BEND_GAP / 2 + TONGUE_T)
    a = math.degrees(math.atan2(dy, dz))
    frac = (zm - (BEND_GAP / 2 + TONGUE_T)) / dz
    y_face = -PLATE_T - BEND_GAP - TONGUE_T + frac * dy
    txt = label(text, size=TEXT_SIZE, depth=TEXT_DEPTH + 0.4)
    clip += Pos(0, y_face + 0.4, zm) * Rot(90 - a, 0, 0) * Rot(0, 0, 0) * txt
    return clip


def build():
    return [Pos(0, -i * 45.0, 0) * make_clip(t) for i, t in enumerate(LABELS)]
