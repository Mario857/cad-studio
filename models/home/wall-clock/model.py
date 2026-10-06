"""wall-clock: 250 mm wall clock face for a standard quartz clock movement.

Spec: round dial Ø250 mm, plate 4 mm thick (<= 5 mm at the shaft hole so the movement's threaded
shaft reaches through for the washer + hex nut), 7.5 mm shaft hole. Raised hour markers (bars,
wider at 3/6/9) and a raised outer bezel ring for stiffness. The 12 o'clock marker is an enlarged
raised block that also houses a keyhole hanger on the back (entry Ø10 for the screw head, 5.5 mm
slot for the shank, head channel inside the block).
Movement: standard 56x56 mm quartz body mounts behind the dial (flat back, nothing to clear).
Prints face-up (back flat on the bed) -> no supports; keyhole head-channel ceiling is a 10 mm bridge.

ASSUMPTIONS:
- Shaft hole printed slightly oversize (HOLE_NOMINAL 7.7 mm) so the 7.5 mm threaded shaft slides in.
- Movement body is ~16 mm deep: drive the wall screw (#6-#8 / 3.5-4 mm wood screw, head <= 9 mm,
  head height <= 3 mm) so it protrudes ~MOVEMENT_DEPTH mm; the dial then hangs parallel to the wall
  with the movement body resting against it.
- Hands are not part of this model (use the hands supplied with the movement).
"""

from build123d import *

from cadlib import *

# Coordinates = in-use orientation: dial vertical in the XZ plane, back against the wall at y=0,
# face toward -Y, 12 o'clock up (+Z), bottom of the dial at z=0.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,              # hangs on a wall screw
    loads=[],
    print_orientation=(-90, 0, 0),  # back flat on bed, face up: zero supports
    supports="off",              # only "support" area is the 10 mm keyhole channel bridge (<= 15 mm)
    brim="on",                   # large flat ABS plate: brim against corner lift
)

# Parameters
DIAMETER = 250.0
PLATE_T = 4.0             # dial thickness (<= 5 at shaft hole)
HOLE_NOMINAL = 7.7        # shaft hole (7.5 mm shaft + clearance)
MOVEMENT_BODY = 56.0      # quartz movement body (reference only)
MOVEMENT_DEPTH = 16.0     # movement body depth -> wall screw protrusion (reference only)

BEZEL_W = 8.0             # raised outer ring width
BEZEL_H = 2.5             # raised outer ring height above plate

MARKER_R = 100.0          # radial centre of hour markers
MARKER_L = 18.0           # hour bar length (radial)
MARKER_W = 4.0            # hour bar width
MARKER_W_QUARTER = 7.0    # width at 3/6/9
MARKER_H = 2.0            # marker height above plate

TWELVE_W = 18.0           # 12 o'clock block (houses the keyhole)
TWELVE_L = 32.0
TWELVE_H = 3.5            # total at block = PLATE_T + TWELVE_H = 7.5

KEY_ENTRY_D = 10.0        # screw head entry hole
KEY_SLOT_W = 5.5          # shank slot
KEY_TRAVEL = 12.0         # slot length (entry centre -> top of slot)
KEY_LIP = 2.0             # material behind the screw head (back skin of the slot)
KEY_CHANNEL_H = 3.2       # head channel height above the lip
KEY_ENTRY_OFFSET = -6.0   # entry hole centre relative to 12-block centre (radial)


def _flat() -> Part:
    """Dial lying flat: back at z=0, face +Z, 12 o'clock toward +Y."""
    R = DIAMETER / 2
    dial = Cylinder(R, PLATE_T, align=ON_BED)
    dial = chamfer(dial.edges().group_by(Axis.Z)[0], 0.4)  # elephant foot

    bezel = Pos(0, 0, PLATE_T) * (
        Cylinder(R, BEZEL_H, align=ON_BED) - Cylinder(R - BEZEL_W, BEZEL_H, align=ON_BED)
    )
    part = dial + bezel

    # hour markers (skip 12, which is the keyhole block)
    for h in range(1, 12):
        w = MARKER_W_QUARTER if h % 3 == 0 else MARKER_W
        bar = Pos(0, MARKER_R, PLATE_T) * Box(w, MARKER_L, MARKER_H, align=ON_BED)
        part += Rot(0, 0, -30 * h) * bar
    twelve = Pos(0, MARKER_R, PLATE_T) * Box(TWELVE_W, TWELVE_L, TWELVE_H, align=ON_BED)
    twelve = fillet(twelve.edges().filter_by(Axis.Z), 2.0)
    part += twelve

    # shaft hole
    part -= Cylinder(hole_d(HOLE_NOMINAL) / 2, 3 * PLATE_T)

    # keyhole (from the back): entry hole, shank slot, head channel above the lip
    y0 = MARKER_R + KEY_ENTRY_OFFSET
    top_h = KEY_LIP + KEY_CHANNEL_H
    entry = Pos(0, y0, 0) * Cylinder(KEY_ENTRY_D / 2, top_h, align=ON_BED)
    slot_cut = Pos(0, y0 + KEY_TRAVEL / 2, 0) * Box(KEY_SLOT_W, KEY_TRAVEL, KEY_LIP, align=ON_BED)
    channel = Pos(0, y0 + KEY_TRAVEL / 2, KEY_LIP) * extrude(
        SlotOverall(KEY_TRAVEL + KEY_ENTRY_D, KEY_ENTRY_D, rotation=90), KEY_CHANNEL_H
    )
    part -= entry + slot_cut + channel
    return part


def build() -> Part:
    return Pos(0, 0, DIAMETER / 2) * Rot(90, 0, 0) * _flat()
