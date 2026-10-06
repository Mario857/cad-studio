"""crate-bowl-holder: bowl ring that clamps to the inside of a wire dog crate.

Spec: a stainless steel bowl (rim Ø BOWL_RIM_D, default 150 mm) drops into a horizontal ring;
its rolled rim rests on the ring seat, inside a raised lip, so the dog cannot tip or slide it.
The ring hangs from a vertical back plate that sits against the INSIDE of the crate mesh.
Two M5 bolts go through the plate's vertical slots and through a mesh opening; on the outside a
printed clamp bar + printed knob (M5 nut trap) squeeze the wires against the plate.
The slots (SLOT_LEN long, SLOT_SPACING apart) let the bolts find a mesh opening on any
25-50 mm grid with Ø3-5 mm wire. Knobs sit outside the crate, out of the dog's reach.

Parts (printed together, no supports): holder (ring flat on bed, plate rising vertically),
2 clamp bars, 2 knobs.

Safety: ABS must not hold food/water directly - the stainless bowl holds the food/water,
the ABS only touches its outside. Not a chew toy; mount it so the knobs are outside the crate and
inspect for bite damage. All dog-facing edges are filleted.

Hardware: stainless bowl, 2x M5x35 socket head cap screw, 2x M5 hex nut (pressed into knobs),
optionally 2x M5 washers under the heads.

Assumptions: bowl body just below the rolled rim is <= RING_ID (138 mm) and the rim is ~150 mm;
wire crossings stack to <= 10 mm so M5x35 reaches; the ring keeps the bowl from tipping but a
dog could still lift a bowl straight out by the rim (lip resists sliding/tipping only).
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,            # hangs on the crate wall
    loads=[],
    print_orientation="auto",  # ring flat on bed, plate vertical
    supports="off",
    brim="auto",
)

# Parameters - bowl
BOWL_RIM_D = 150.0       # outer diameter of the bowl's rolled rim
RIM_CLEAR = 1.5          # radial clearance around the rim
RING_ID = 138.0          # through-hole for bowl body
FLANGE_T = 5.0           # seat thickness under the rim
LIP_H = 6.0              # raised lip around rim
LIP_W = 4.0              # lip wall thickness

# Parameters - back plate
PLATE_W = 120.0
PLATE_H = 95.0
PLATE_T = 7.0
WEB_W = 110.0            # width of the ring-to-plate web
GUSSET_L = 14.0
GUSSET_H = 45.0
GUSSET_T = 6.0
GUSSET_X = 46.0

# Parameters - clamp
BOLT = "M5"
BOLT_CLEAR_D = clearance(5.0, "loose")      # bolt slot / hole width
HEAD_SLOT_W = 9.5                           # counterbore slot for socket head (8.5 head)
HEAD_DEPTH = 3.0
SLOT_SPACING = 80.0                         # x distance between the two bolt slots
SLOT_Z0 = 25.0                              # lowest bolt centre
SLOT_LEN = 55.0                             # travel of the bolt centre (covers 25-50 grids)
BAR_L = 50.0
BAR_W = 20.0
BAR_T = 8.0
KNOB_D = 34.0
KNOB_H = 12.0
KNOB_LOBES = 6
NUT_DEPTH = 5.0

RIM_R = BOWL_RIM_D / 2 + RIM_CLEAR
RING_RO = RIM_R + LIP_W
TOP_Z = FLANGE_T + LIP_H
RING_CY = PLATE_T + RING_RO - 2.0           # ring overlaps the plate by 2 mm


def _ring() -> Part:
    ring = Cylinder(RING_RO, TOP_Z, align=ON_BED)
    web = Pos(0, -RING_CY / 2, 0) * Box(WEB_W, RING_CY, TOP_Z, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = ring + web
    body -= Pos(0, 0, FLANGE_T) * Cylinder(RIM_R, TOP_Z, align=ON_BED)
    body -= Pos(0, 0, -1) * Cylinder(RING_ID / 2, TOP_Z + 2, align=ON_BED)
    return Pos(0, RING_CY, 0) * body


def _vslot(width, length, y0, y1):
    """Vertical stadium cutter (long axis Z) spanning y0..y1."""
    cut = Pos(0, y0, 0) * Rot(-90, 0, 0) * Rot(0, 0, 90) * extrude(SlotOverall(length + width, width), y1 - y0)
    side = width  # teardrop point on the upper end -> no support in the slot
    tip = Pos(0, (y0 + y1) / 2, length / 2) * Rot(0, 45, 0) * Box(side, y1 - y0, side)
    return cut + tip


def _holder() -> Part:
    plate = Box(PLATE_W, PLATE_T, PLATE_H, align=(Align.CENTER, Align.MIN, Align.MIN))
    plate = fillet(plate.edges().filter_by(Axis.Y).group_by(Axis.Z)[-1], 4)
    part = plate + _ring()
    for sx in (-1, 1):
        part += Pos(sx * GUSSET_X, PLATE_T, TOP_Z) * Rot(0, 0, 90) * rib(GUSSET_L, GUSSET_H, GUSSET_T)
    zc = SLOT_Z0 + SLOT_LEN / 2
    for sx in (-1, 1):
        x = sx * SLOT_SPACING / 2
        part -= Pos(x, 0, zc) * _vslot(BOLT_CLEAR_D, SLOT_LEN, -1, PLATE_T + 1)
        part -= Pos(x, 0, zc) * _vslot(HEAD_SLOT_W, SLOT_LEN, PLATE_T - HEAD_DEPTH, PLATE_T + 1)
    try:
        part = fillet(part.edges().group_by(Axis.Z)[-1], 1.0)
    except Exception:
        pass
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    return part


def _bar() -> Part:
    bar = rounded_box(BAR_L, BAR_W, BAR_T, radius=4, top_radius=1.5)
    bar -= Pos(0, 0, BAR_T + 1) * Cylinder(BOLT_CLEAR_D / 2, BAR_T + 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return bar


def _knob() -> Part:
    knob = Cylinder(KNOB_D / 2, KNOB_H, align=ON_BED)
    knob -= PolarLocations(KNOB_D / 2 + 1.5, KNOB_LOBES) * Cylinder(3.5, KNOB_H + 2, align=ON_BED)
    knob = fillet(knob.edges().filter_by(Axis.Z), 1.5)
    knob = fillet(knob.edges().group_by(Axis.Z)[-1], 1.0)
    knob = chamfer(knob.edges().group_by(Axis.Z)[0], 0.4)
    knob -= Pos(0, 0, KNOB_H + 1) * Cylinder(BOLT_CLEAR_D / 2, KNOB_H + 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
    knob -= Pos(0, 0, KNOB_H) * nut_trap(BOLT, depth=NUT_DEPTH)
    return knob


def build():
    y_free = RING_CY + RING_RO + 12
    parts = [_holder()]
    for sx in (-1, 1):
        parts.append(Pos(sx * 75, y_free + BAR_W / 2, 0) * _bar())
        parts.append(Pos(sx * 30, y_free + KNOB_D / 2, 0) * _knob())
    return parts
