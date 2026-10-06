"""emergency-info-tag: ICE (in case of emergency) backpack tag with raised info text.

Spec: 70 x 40 x 3.6 mm tag, four lines of raised text (0.6 mm, ~5 mm cap height) from the NAME / PHONE /
BLOOD_TYPE / ALLERGIES params; a 27 x 4 mm slot at the left end for a 25 mm strap or zip ties;
a 52 x 32 x 0.4 mm recess on the back for a piece of reflective tape (e.g. 3M Scotchlite).
Edit the four text params (one-line changes); build() raises if a line is too long for the tag
(max ~12 characters at 5 mm text) - shorten it rather than shrinking the text.
Print: standing on its long bottom edge (rotated 90° about X): the back recess and raised letters
then only make tiny 0.4-0.6 mm overhangs instead of a 50 x 30 mm ceiling, and the strap pull along X
runs along the layers. Brim on (narrow footprint; the audit's 'wobbly' note is expected).
Thinnest walls reported are the bold letter strokes (~0.8 mm), not the tag body.
Hardware: 25 mm strap or 2 zip ties; reflective tape 50 x 30 mm.
Assumptions: placeholder personal data below - replace before printing.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(90, 0, 0),  # on the long bottom edge
    supports="off",                # only 0.6 mm letter-stroke undersides overhang (fine unsupported)
    brim="on",                     # on-edge print: narrow 3.6 mm footprint, brim keeps it upright
)

# --- personal info (edit these) ---
NAME = "J. DOE"
PHONE = "+1 555 0100"
BLOOD_TYPE = "0+"
ALLERGIES = "NONE"
LINES = [NAME, PHONE, f"BLOOD {BLOOD_TYPE}", f"ALLERGY {ALLERGIES}"]

TAG_L = 70.0
TAG_W = 40.0
THICK = 3.6
CORNER_R = 4.0
TEXT_SIZE = 7.0            # font size -> ~5 mm cap height
TEXT_H = 0.6               # raised height
LINE_PITCH = 8.5
TEXT_X0 = -24.0            # text area (right of the slot)
TEXT_X1 = TAG_L / 2 - 2.0
# strap / zip-tie slot
SLOT_X = -TAG_L / 2 + 5.5
SLOT_W = 4.0
SLOT_L = 27.0
# reflective tape recess (back)
TAPE_L = 52.0
TAPE_W = 32.0
TAPE_DEPTH = 0.4


def build() -> Part:
    tag = rounded_box(TAG_L, TAG_W, THICK, radius=CORNER_R)
    # slot with 45° pointed ends (prints without a ceiling when the tag stands on edge)
    h = SLOT_W / 2
    slot = Polygon((SLOT_X - h, -SLOT_L / 2 + h), (SLOT_X, -SLOT_L / 2), (SLOT_X + h, -SLOT_L / 2 + h),
                   (SLOT_X + h, SLOT_L / 2 - h), (SLOT_X, SLOT_L / 2), (SLOT_X - h, SLOT_L / 2 - h), align=None)
    tag -= extrude(Plane.XY.offset(-1) * slot, THICK + 2)
    # reflective tape recess in the back, centred on the text area
    cx = (TEXT_X0 + TEXT_X1) / 2
    tag -= Pos(cx, 0, -1) * Box(TAPE_L, TAPE_W, TAPE_DEPTH + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # raised text lines
    max_w = TEXT_X1 - TEXT_X0
    y0 = (len(LINES) - 1) / 2 * LINE_PITCH
    for i, t in enumerate(LINES):
        txt = label(t, size=TEXT_SIZE, depth=TEXT_H + 0.01)
        bb = txt.bounding_box()
        if bb.size.X > max_w:
            raise ValueError(f"text line {t!r} is {bb.size.X:.1f} mm wide, max {max_w:.1f} mm - shorten it")
        y = y0 - i * LINE_PITCH
        tag += Pos(cx - bb.center().X, y - bb.center().Y, THICK - 0.01) * txt
    return tag
