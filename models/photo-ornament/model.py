"""photo-ornament: Christmas tree ornament frame for a 50 mm round photo.

Spec: bauble-shaped frame (round body with a 45-degree pointed "finial" bottom), a
vertical photo pocket that is open at the top so a Ø50 photo slides in from above
and rests in the round bottom of the pocket. Front window (Ø43) with a 45-degree
pointed, clipped roof; raised decorative front rim with diamond studs; a
diamond-shaped hanging eye on top attached to the back plate only, so the photo
can pass in front of it when inserted.

Printed upright on its flat finial tip (in-use orientation): the pocket is a
vertical slot (no ceiling), the window roof is 45 degrees with a short flat
bridge (<= 15 mm), the outline bottom is a 45-degree V, the eye is a diamond
(45-degree faces) -> support-free. The only "support" area the audit counts
(~0.4 cm2) is the flat window/ring roof: a 13 mm bridge, within the 15 mm rule.
A 14 mm deep finial foot (45-degree taper into the body) keeps it from wobbling.

Assumptions:
- Photo is Ø50 printed paper/photo paper <= 0.3 mm thick (PHOTO_T); radial
  clearance 0.5 mm, 0.3 mm per side in thickness (pocket 0.9 mm).
- Window overlaps the photo edge by ~3.5 mm all round so it is retained.
- Hung by ribbon/hook through a 5 mm eye; ornament weighs only a few grams.
- Brim forced on: the part is 74 mm tall on a 20 x 14 mm finial foot.
- Eye is attached to the back plate only, so the ornament hangs tilted very
  slightly forward; acceptable for decoration.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,            # hangs on the tree
    loads=[],
    print_orientation=(0, 0, 0),  # upright on the flat finial tip: pocket = vertical slot
    supports="off",
    brim="on",                 # tall narrow part on a small footprint
)

# Photo + fits
PHOTO_D = 50.0          # photo diameter
PHOTO_T = 0.3           # photo thickness
CLEAR_R = 0.5           # radial clearance photo -> pocket
CLEAR_T = 0.3           # clearance per side in thickness
POCKET_R = PHOTO_D / 2 + CLEAR_R
POCKET_T = PHOTO_T + 2 * CLEAR_T

# Body
RIM_W = 4.5             # outer rim width beyond pocket
OUTER_R = POCKET_R + RIM_W
FRONT_T = 1.6           # front plate
BACK_T = 2.4            # back plate (also carries the eye)
FLAT_HALF = 10.0        # half width of the flat bed/finial tip
BOTTOM_CHAMFER = 0.4
FOOT_D = 14.0           # finial foot depth (Y) for a stable stand on the bed
FOOT_H = 2.0            # straight part of the foot before the 45-degree taper

# Window
WINDOW_R = 21.5         # overlaps photo by 3.5 mm
WINDOW_BRIDGE = 13.0    # max flat roof width (<= 15 mm bridge)

# Decorative front rim
RIM_RAISE = 1.0         # raised ring proud of the front plate
RIM_INSET = 0.8         # ring inset from the outer outline
RIM_GAP = 1.5           # ring inner edge offset from the window
STUD_N = 12             # diamond studs on the ring
STUD_SIZE = 2.6         # stud diagonal
STUD_H = 0.8            # stud height proud of the ring
STUD_RING_R = OUTER_R - 2.8

# Hanging eye
EYE_R = 5.5             # outer radius of diamond-ish eye
EYE_HOLE_R = 2.5
EYE_Z = OUTER_R + 4.0   # eye centre height above body centre


def droplet(r, roof=True, keel=False, clip_top=None, clip_bot=None):
    """Circle with optional 45-degree roof (pointing +local y) and keel (-y)."""
    s = Circle(r)
    t = r / math.sqrt(2)
    if roof:
        s += Polygon((t, t), (0, r * math.sqrt(2)), (-t, t), align=None)
    if keel:
        s += Polygon((-t, -t), (0, -r * math.sqrt(2)), (t, -t), align=None)
    big = 4 * r
    if clip_top is not None:
        s &= Pos(0, clip_top - big / 2) * Rectangle(big, big)
    if clip_bot is not None:
        s &= Pos(0, clip_bot + big / 2) * Rectangle(big, big)
    return s


def prism(sk, y0, y1):
    """Extrude an XZ-plane sketch (local x = X, local y = Z) between y0 < y1."""
    pl = Plane(origin=(0, y1, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    return extrude(pl * sk, amount=y1 - y0)


def build() -> Part:
    # Y layout: front face at y=0 side (-Y is the viewer), back face at +Y
    y_front = -(FRONT_T + POCKET_T / 2)
    y_pf, y_pb = -POCKET_T / 2, POCKET_T / 2
    y_back = POCKET_T / 2 + BACK_T

    bot_z = -math.sqrt(2) * OUTER_R + FLAT_HALF  # flat tip height (body coords)

    outline = droplet(OUTER_R, roof=False, keel=True, clip_bot=bot_z)
    body = prism(outline, y_front, y_back)

    # Finial foot: deeper in Y at the tip, 45-degree taper back to the body
    y_mid = (y_front + y_back) / 2
    hd, bd = FOOT_D / 2, (y_back - y_front) / 2
    taper = hd - bd
    foot_prof = Polygon((y_mid - hd, bot_z), (y_mid + hd, bot_z),
                        (y_mid + hd, bot_z + FOOT_H),
                        (y_mid + bd, bot_z + FOOT_H + taper),
                        (y_mid - bd, bot_z + FOOT_H + taper),
                        (y_mid - hd, bot_z + FOOT_H), align=None)
    foot = extrude(Plane.YZ.offset(-OUTER_R) * foot_prof, amount=2 * OUTER_R)
    body += foot & prism(outline, y_mid - hd - 1, y_mid + hd + 1)

    # Decorative raised front ring (inner edge follows the window shape)
    win_clip = WINDOW_R * math.sqrt(2) - WINDOW_BRIDGE / 2
    ring_outer = droplet(OUTER_R - RIM_INSET, roof=False, keel=True,
                         clip_bot=bot_z + RIM_INSET)
    ring_inner = droplet(WINDOW_R + RIM_GAP, roof=True,
                         clip_top=win_clip + RIM_GAP)
    body += prism(ring_outer - ring_inner, y_front - RIM_RAISE, y_front + 0.2)

    # Diamond studs on the ring (45-degree faces only)
    h = STUD_SIZE / 2
    diamond = Polygon((0, -h), (h, 0), (0, h), (-h, 0), align=None)
    studs = None
    for i in range(STUD_N):
        a = math.radians(90 + i * 360 / STUD_N)
        x, z = STUD_RING_R * math.cos(a), STUD_RING_R * math.sin(a)
        d = Pos(x, z) * diamond
        studs = d if studs is None else studs + d
    body += prism(studs, y_front - RIM_RAISE - STUD_H, y_front - RIM_RAISE + 0.2)

    # Hanging eye on the back plate only (photo passes in front of it)
    eye = Pos(0, EYE_Z) * (droplet(EYE_R, roof=True, keel=True)
                           - droplet(EYE_HOLE_R, roof=True))
    body += prism(eye, y_pb, y_back)

    # Photo pocket: round bottom + straight slot up and out through the top
    pocket = Circle(POCKET_R) + Pos(0, (EYE_Z + EYE_R * 2) / 2) * Rectangle(
        2 * POCKET_R, EYE_Z + EYE_R * 2)
    body -= prism(pocket, y_pf, y_pb)

    # Front window with 45-degree clipped roof
    window = droplet(WINDOW_R, roof=True, clip_top=win_clip)
    body -= prism(window, y_front - RIM_RAISE - 1, y_pf)

    # Rest on z=0
    body = Pos(0, 0, -bot_z) * body
    body = chamfer(body.edges().group_by(Axis.Z)[0], BOTTOM_CHAMFER)
    return body
