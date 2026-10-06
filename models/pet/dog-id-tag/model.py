"""dog-id-tag: set of two dog ID tags (round Ø32 + bone), raised NAME / PHONE text, reinforced ring hole.

Spec: 2.5 mm thick plates with 0.8 mm raised bold text (NAME on top line, PHONE below, both
TEXT_H >= 5 mm tall) and a raised, reinforced eyelet for a split ring (hardware: one split ring
per tag, ~20-25 mm, wire <= 1.5 mm). Round tag Ø32 mm (+ eyelet), bone tag ~51 x 29 mm. Both
tags are printed together, flat on the bed, text up, no supports.
Text is scaled to exactly TEXT_H tall; if a long string would not fit the face it is condensed
in X only (never below TEXT_MIN_XSCALE) so the height stays >= 5 mm.

Pet safety: ABS must not hold food/water directly and is not a chew toy - this tag hangs on a
collar; check it regularly and replace it if cracked or chewed. All touchable edges are filleted
(0.8 mm top perimeter, eyelet and hole rounded); bed edges carry the 0.4 mm elephant-foot
chamfer. Raised letters are strokes (< 2 mm wide by nature) but are fused full-length to the
plate, not protruding parts that can break off.

Assumptions: "2.5 mm thick" = plate thickness, text sits on top (total 3.3 mm). Default
font, bold. Eyelet hole Ø4.5 mm suits common split rings; eyelet wall 3 mm, raised like the
text for reinforcement. Defaults NAME="MAX", PHONE="555-0123" - edit the params.

Audit notes: WARN "2 separate bodies" is intended (round + bone tag printed together).
WARN thin walls (~0.7-1.2 mm) are the raised letter strokes only; plate and eyelet are >= 2.5 mm.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",               # small raised text
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # flat, text up
    supports="off",
    brim="auto",
)

# Parameters
NAME = "MAX"
PHONE = "555-0123"

PLATE_T = 2.5          # plate thickness
TEXT_RAISE = 0.8       # raised text height
TEXT_H = 5.2           # text height (>= 5)
TEXT_MIN_XSCALE = 0.6  # most condensing allowed for long strings
TOP_FILLET = 0.8       # top perimeter fillet
BED_CHAMFER = 0.4

ROUND_D = 32.0
ROUND_NAME_Y = 3.0     # text line centres
ROUND_PHONE_Y = -4.8
ROUND_NAME_W = 23.0    # max text widths
ROUND_PHONE_W = 22.0

BONE_BODY_L = 36.0
BONE_BODY_W = 16.0
BONE_LOBE_R = 7.5
BONE_LOBE_DY = 7.0
BONE_NAME_Y = 2.0
BONE_PHONE_Y = -4.6
BONE_TEXT_W = 34.0

HOLE_D = 4.5           # split-ring hole
EYE_WALL = 3.0         # eyelet wall around the hole
EYE_R = HOLE_D / 2 + EYE_WALL
EYE_BOSS_INSET = 0.6   # raised reinforcement ring sits inside the eyelet outline
ROUND_EYE_Y = ROUND_D / 2 + 2.0
BONE_EYE_Y = BONE_BODY_W / 2 + 2.5

NECK_R = 2.0           # concave neck rounding of the outline
GAP = 8.0              # spacing between the two tags on the bed


def text_line(s, y, max_w):
    t = Text(s, font_size=10, font_style=FontStyle.BOLD)
    bb = t.bounding_box()
    k = TEXT_H / bb.size.Y
    sx = max(min(k, max_w / bb.size.X), k * TEXT_MIN_XSCALE)
    t = scale(t, by=(sx, k, 1))
    c = t.bounding_box().center()
    t = Pos(-c.X, y - c.Y) * t
    return Pos(0, 0, PLATE_T) * extrude(t, TEXT_RAISE)


def hole_edges(part):
    return part.edges().filter_by(GeomType.CIRCLE).filter_by(
        lambda e: abs(e.radius - HOLE_D / 2) < 0.05)


def tag(outline, eye_y, lines):
    outline = offset(offset(outline, NECK_R), -NECK_R)  # round the concave necks
    plate = extrude(outline, PLATE_T)
    plate = chamfer(plate.edges().group_by(Axis.Z)[0], BED_CHAMFER)
    plate = fillet(plate.edges().group_by(Axis.Z)[-1], TOP_FILLET)
    boss = Pos(0, eye_y, PLATE_T) * Cylinder(EYE_R - EYE_BOSS_INSET, TEXT_RAISE, align=ON_BED)
    boss = fillet(boss.edges().group_by(Axis.Z)[-1], 0.5)
    part = plate + boss
    for s, y, w in lines:
        part += text_line(s, y, w)
    part -= Pos(0, eye_y, -1) * Cylinder(HOLE_D / 2, 10, align=ON_BED)
    part = fillet(hole_edges(part).group_by(Axis.Z)[-1], 0.5)
    part = chamfer(hole_edges(part).group_by(Axis.Z)[0], BED_CHAMFER)
    return part


def round_tag():
    outline = Circle(ROUND_D / 2) + Pos(0, ROUND_EYE_Y) * Circle(EYE_R)
    return tag(outline, ROUND_EYE_Y, [(NAME, ROUND_NAME_Y, ROUND_NAME_W),
                                      (PHONE, ROUND_PHONE_Y, ROUND_PHONE_W)])


def bone_tag():
    outline = Rectangle(BONE_BODY_L, BONE_BODY_W)
    for sx in (-1, 1):
        for sy in (-1, 1):
            outline += Pos(sx * BONE_BODY_L / 2, sy * BONE_LOBE_DY) * Circle(BONE_LOBE_R)
    outline += Pos(0, BONE_EYE_Y) * Circle(EYE_R)
    return tag(outline, BONE_EYE_Y, [(NAME, BONE_NAME_Y, BONE_TEXT_W),
                                     (PHONE, BONE_PHONE_Y, BONE_TEXT_W)])


def build():
    bone_w = BONE_BODY_L + 2 * BONE_LOBE_R
    return [Pos(-(ROUND_D / 2 + GAP / 2), 0) * round_tag(),
            Pos(bone_w / 2 + GAP / 2, 0) * bone_tag()]
