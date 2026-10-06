"""luggage-tag: 90 x 55 mm luggage tag with hidden contact card under a dovetail slide cover.

Spec:
- Body 90 x 55 mm. A 15 mm strap / cable-tie slot at the -X end (3 mm loaded end wall).
- Front (+Z) has a dovetail channel open at the +X end. Under it, a recess holds a paper
  contact card (CARD_L x CARD_W). The separate slide cover (2nd part of the returned list)
  slides in along X, hides the card, and carries the raised name TEXT (7 mm tall, 0.8 mm).
- Cover locks with a flexing tongue at its trailing end: a through-hole in the tongue snaps over
  a 0.6 mm cone bump on the channel floor. To open: lift the tongue end with a fingernail, slide out.
- Two separate bodies (body + cover) are intended, laid out side by side (cover at +Y); both print flat,
  no supports. Dovetail: 0.6 mm vertical foot, 0.8 mm 45 deg undercut, 0.6 mm vertical lip (no knife edges).

Assumptions:
- Floor under card 1.4 mm (1.2 read as thin by the wall audit). Card: paper/cardstock cut to 60 x 40 mm, <= 0.5 mm thick (a business card cut down).
- Strap: up to 15 mm wide and <= 3 mm thick webbing, or a cable tie; slot 17 x 4 mm.
- Slide fit 0.20 mm per face (ABS PLUS shrinks a bit; loosen SLIDE_CLEAR if tight).
- Body is already thin (4.2 mm); the card recess is the main material removal. Lightening
  pockets on the back were skipped: they would be ceilings over the bed and weaken the tag.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # both parts flat, as laid out
    supports="off",
    brim="auto",
)

# Overall
TAG_L = 90.0
TAG_W = 55.0
CORNER_R = 4.0

# Card recess (paper contact card)
CARD_L = 60.0
CARD_W = 40.0
CARD_CLEAR = 0.5          # per side around the card
CARD_POCKET_D = 1.0       # recess depth (card <= 0.5 mm)
FLOOR_T = 1.4             # back floor under the card

# Slide cover / dovetail
COVER_T = 2.0             # cover thickness = dovetail channel depth
DOVE_LIP = 0.6            # vertical lip at top of channel (avoid knife edge)
DOVE_FOOT = 0.6           # vertical flat at channel bottom (blunt cover edge)
SIDE_WALL = 3.0           # body wall beside the channel at its widest (bottom)
SLIDE_CLEAR = 0.20        # clearance per face for the slide fit
END_CLEAR = 0.3           # cover to channel closed-end gap

# Strap slot
STRAP_W = 15.0
STRAP_SLOT_EXTRA = 2.0    # slot length = STRAP_W + this
STRAP_SLOT_W = 4.0
STRAP_END_WALL = 3.0      # loaded edge (>= 2 mm)
SLOT_TO_CHANNEL = 3.0

# Snap detent
TONGUE_L = 14.0
TONGUE_W = 8.0
TONGUE_GAP = 1.2
BUMP_R = 1.2
BUMP_H = 0.6
DETENT_HOLE_D = 2.6
DETENT_FROM_END = 6.0     # bump/hole center distance from the +X end

# Text
TEXT = "YOUR NAME"
TEXT_SIZE = 7.0
TEXT_H = 0.8
TEXT_MIN = 5.0

# Print layout
COVER_GAP = 6.0           # cover placed beside the body at +Y for printing

# Derived
Z_CH = FLOOR_T + CARD_POCKET_D           # channel floor
H = Z_CH + COVER_T                       # body thickness
WB = TAG_W - 2 * SIDE_WALL               # channel width at floor
UNDER = COVER_T - DOVE_LIP - DOVE_FOOT   # 45 deg undercut per side
WT = WB - 2 * UNDER                      # channel width at top opening
X0 = -TAG_L / 2 + STRAP_END_WALL + STRAP_SLOT_W + SLOT_TO_CHANNEL  # channel closed end
X1 = TAG_L / 2
X_DET = X1 - DETENT_FROM_END


def dovetail_profile(clear: float, z0: float, z1: float) -> Face:
    """Channel cross-section in the YZ plane (local x = Y, local y = Z), shrunk by clear.

    z0 < Z_CH and z1 > H extend the profile so it can be trimmed / cut through cleanly.
    Profile: vertical foot, 45 deg undercut flank, vertical lip.
    """
    zf = Z_CH + DOVE_FOOT
    zt = zf + UNDER
    pts = [(-WB / 2, z0), (WB / 2, z0), (WB / 2, zf), (WT / 2, zt), (WT / 2, z1),
           (-WT / 2, z1), (-WT / 2, zt), (-WB / 2, zf)]
    face = Polygon(*pts, align=None)
    if clear > 0:
        face = offset(face, -clear, kind=Kind.INTERSECTION)
    return face


def channel_solid(clear: float, x0: float, x1: float, z0: float, z1: float) -> Part:
    prof = dovetail_profile(clear, z0, z1)
    return extrude(Plane.YZ.offset(x0) * prof, amount=x1 - x0)


def build():
    body = rounded_box(TAG_L, TAG_W, H, radius=CORNER_R)

    # Dovetail channel, open at +X end
    body -= channel_solid(0.0, X0, X1 + 2, Z_CH, H + 1)

    # Card recess under the channel floor
    pocket_l = CARD_L + 2 * CARD_CLEAR
    pocket_w = CARD_W + 2 * CARD_CLEAR
    px = X0 + 1.0 + pocket_l / 2
    body -= Pos(px, 0, FLOOR_T) * Box(pocket_l, pocket_w, CARD_POCKET_D + 1, align=ON_BED)

    # Strap slot
    sx = -TAG_L / 2 + STRAP_END_WALL + STRAP_SLOT_W / 2
    body -= Pos(sx, 0, H + 1) * Rot(0, 0, 90) * slot(STRAP_W + STRAP_SLOT_EXTRA, STRAP_SLOT_W, H + 2)

    # Detent bump on channel floor
    body += Pos(X_DET, 0, Z_CH) * Cone(BUMP_R, BUMP_R * 0.4, BUMP_H, align=ON_BED)

    # ---- Slide cover (in-use position first) ----
    cx0 = X0 + END_CLEAR
    cover = channel_solid(SLIDE_CLEAR, cx0, X1, Z_CH - 1, H + 1)
    cover &= Pos((cx0 + X1) / 2, 0, Z_CH) * Box(X1 - cx0, TAG_W, COVER_T, align=ON_BED)

    # Flex tongue: two slots at the trailing (+X) end, root toward -X, free end at +X
    tx0 = X1 - TONGUE_L
    for y in (TONGUE_W / 2 + TONGUE_GAP / 2, -TONGUE_W / 2 - TONGUE_GAP / 2):
        cover -= Pos(tx0 + TONGUE_L / 2 + 1, y, Z_CH - 1) * Box(TONGUE_L + 2, TONGUE_GAP, COVER_T + 2, align=ON_BED)
    cover -= Pos(X_DET, 0, Z_CH - 1) * Cylinder(DETENT_HOLE_D / 2, COVER_T + 2, align=ON_BED)

    # Raised name text, centred on the cover area left of the tongue
    txt_cx = (cx0 + tx0 - TONGUE_GAP) / 2
    avail = (tx0 - TONGUE_GAP) - cx0 - 4
    t = label(TEXT, size=TEXT_SIZE, depth=TEXT_H)
    bb = t.bounding_box()
    if bb.size.X > avail:
        k = avail / bb.size.X
        assert TEXT_SIZE * k >= TEXT_MIN, "TEXT too long for >= 5 mm letters"
        t = scale(t, (k, k, 1))
        bb = t.bounding_box()
    t = Pos(txt_cx - bb.center().X, -bb.center().Y, H) * t
    cover += t

    # Move cover beside the body, resting on the bed
    cover = Pos(0, TAG_W / 2 + COVER_GAP + WB / 2, -Z_CH) * cover
    return [body, cover]
