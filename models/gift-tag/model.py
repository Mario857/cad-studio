"""gift-tag: Christmas present name tags, a set of 6 printed together.

Spec: flat tag 60 x 35 x 2 mm with rounded corners, a vertical ribbon slot near the left
end, and the name raised 0.6 mm on the top face. NAMES holds the 6 names; build() returns
6 tags laid out 2 x 3 on the plate. The font size is chosen per name: as big as fits
(up to FONT_MAX), shrunk for long names, never below FONT_MIN (5 mm).
Assumptions:
- Placeholder names; edit NAMES. A name too long to fit even at FONT_MIN raises an error
  (shorten it or use a nickname) instead of printing below 5 mm.
- Ribbon up to ~10 mm wide: slot 4 x 12 mm, oriented across the tag (along Y).
- Font size = build123d font_size (em height); text is the default sans font, bold.
- Printed flat, text up; single-colour unless you add a filament change at z = 2 mm.
- Mesh WARN "6 separate bodies" is intended: 6 individual tags on one plate.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # flat, text up
    supports="off",
    brim="auto",
)

# Parameters
NAMES = ["Anna", "Max", "Grandma", "Sebastian", "Elisabeth", "Leo"]

TAG_L = 60.0          # X
TAG_W = 35.0          # Y
TAG_T = 2.0           # thickness
CORNER_R = 5.0

SLOT_LEN = 12.0       # ribbon slot length (along Y)
SLOT_W = 4.0          # ribbon slot width (along X)
SLOT_INSET = 7.0      # slot centre from the left edge

TEXT_RAISE = 0.6      # raised text height
FONT_MAX = 12.0
FONT_MIN = 5.0
TEXT_MARGIN = 3.0     # clearance from slot / edges to text

GRID_COLS = 2
GRID_ROWS = 3
GAP = 6.0             # spacing between tags on the plate


def _text_box():
    """Available text area (x0, x1, height) on the tag."""
    x0 = -TAG_L / 2 + SLOT_INSET + SLOT_W / 2 + TEXT_MARGIN
    x1 = TAG_L / 2 - TEXT_MARGIN
    return x0, x1, TAG_W - 2 * TEXT_MARGIN


def _name_solid(name: str) -> Part:
    x0, x1, avail_h = _text_box()
    avail_w = x1 - x0

    def make(size):
        return extrude(Text(name, font_size=size, font_style=FontStyle.BOLD), TEXT_RAISE)

    size = FONT_MAX
    txt = make(size)
    bb = txt.bounding_box()
    scale = min(avail_w / bb.size.X, avail_h / bb.size.Y, 1.0)
    if scale < 1.0:
        size = max(FONT_MIN, size * scale * 0.98)
        txt = make(size)
        bb = txt.bounding_box()
    if bb.size.X > avail_w + 1e-6:
        raise ValueError(f"name {name!r} does not fit at the {FONT_MIN} mm minimum font size")
    c = bb.center()
    return Pos((x0 + x1) / 2 - c.X, -c.Y, TAG_T) * txt


def tag(name: str) -> Part:
    body = rounded_box(TAG_L, TAG_W, TAG_T, radius=CORNER_R)
    slot_cut = Pos(-TAG_L / 2 + SLOT_INSET, 0, TAG_T) * Rot(0, 0, 90) * slot(SLOT_LEN, SLOT_W, TAG_T + 1)
    return body - slot_cut + _name_solid(name)


def build():
    parts = []
    pitch_x = TAG_L + GAP
    pitch_y = TAG_W + GAP
    for i, name in enumerate(NAMES):
        col, row = i % GRID_COLS, i // GRID_COLS
        x = (col - (GRID_COLS - 1) / 2) * pitch_x
        y = ((GRID_ROWS - 1) / 2 - row) * pitch_y
        parts.append(Pos(x, y, 0) * tag(name))
    return parts
