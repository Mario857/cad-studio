"""headlamp-lantern-diffuser: clip-on diffuser dome that turns a headlamp into a hanging tent lantern.

Spec / use:
- The headlamp body drops lens-DOWN into a rectangular sleeve on top of a thin-walled diffuser
  "bulb" (rounded-rect lantern). It rests on a 4 mm ledge around the light opening; two flex tabs
  per long side with 45-degree snap lips catch the back of the body so it cannot jump out.
- The strap stays attached and simply wraps over/around the sleeve and bail.
- A pointed (gothic) bail over the sleeve hangs from the tent-ceiling loop / a mini carabiner.
  The bail clears the body height so the headlamp can slide in under it and drop into the sleeve.
- Print in WHITE (or natural) filament for diffusion.

INTENTIONAL WALL-RULE EXCEPTION: the diffuser panels are DIFFUSER_WALL = 1.0 mm (allowed
0.8-1.2 mm) so light passes through evenly. They carry no load (only their own ~15 g).
Load path (headlamp ~100 g) runs ledge -> 2 mm sleeve -> 3.5 x 6 mm bail, all >= 2 mm.

Print: in-use orientation, flat diffuser bottom on the bed. All slopes <= ~40 deg, bail peak
is a 45-degree gothic arch, snap lips are 45-degree; zero supports.

Assumptions:
- Headlamp body 60 x 35 x 30 mm (W x H x depth along the beam), lens on the 60 x 35 face,
  roughly box-shaped with corners <= 4 mm radius. Change BODY_* params for other lamps.
- Lens/emitter fits inside the 53 x 28 mm light opening (typical lens <= 25 mm).
- Headlamp mass ~100 g.
- Material per job spec: AzureFilm ABS PLUS (use the white spool).
"""

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",  # print in white for diffusion
    quality="standard",
    standing=False,            # hangs from the tent ceiling
    loads=[dict(at=(0, 0, 100), grams=100)],  # headlamp in the sleeve
    print_orientation=(0, 0, 0),  # as used: flat diffuser bottom on bed, no supports
    supports="off",
    brim="auto",
    notes="Diffuser walls 1.0 mm on purpose (light diffusion, non-structural) - thin-wall "
          "warnings on the bulb are accepted; loaded parts (ledge, sleeve, bail) are >= 2 mm.",
)

# --- Headlamp body (fit) ---
BODY_W = 60.0        # X
BODY_H = 35.0        # Y
BODY_D = 30.0        # Z (depth along beam)
CLEAR = 0.5          # per-side clearance around body in the sleeve
CLEAR_Z = 0.5        # vertical play under the snap lips
BODY_CORNER_R = 4.0

# --- Diffuser bulb ---
DIFFUSER_WALL = 1.0  # intentional thin wall (0.8-1.2) for light diffusion
BOTTOM = (50.0, 30.0, 10.0)   # bottom panel L, W, corner r (on bed)
BULB = (80.0, 60.0, 20.0)     # max section L, W, corner r
Z_FLARE = 20.0       # bottom panel -> max section height
Z_BULB_TOP = 60.0    # top of straight part
SHOULDER_H = 20.0    # shoulder narrowing to sleeve

# --- Sleeve / ledge / snaps ---
SLEEVE_WALL = 2.0
LEDGE_W = 4.0        # rest ledge width around the light opening
LEDGE_T = 2.0
LIP = 1.2            # snap lip inward depth
TAB_W = 12.0
TAB_X = 18.0         # tab centre |x|
TAB_L = 24.0         # free length of flex tab
SLOT_W = 1.5

# --- Bail (hanging loop) ---
BAIL_T = 3.5         # radial thickness (loaded >= 2 mm)
BAIL_WIDTH = 6.0     # along X
BAIL_EXTRA = 1.0     # extra clearance above body when sliding under the bail

# Derived
SL_IN_L = BODY_W + 2 * CLEAR
SL_IN_W = BODY_H + 2 * CLEAR
SL_OUT_L = SL_IN_L + 2 * SLEEVE_WALL
SL_OUT_W = SL_IN_W + 2 * SLEEVE_WALL
OPEN_L = SL_IN_L - 2 * LEDGE_W
OPEN_W = SL_IN_W - 2 * LEDGE_W
Z_LEDGE = Z_BULB_TOP + SHOULDER_H
SLEEVE_H = BODY_D + CLEAR_Z + LIP + 0.4 + 2.0
Z_SLEEVE_TOP = Z_LEDGE + SLEEVE_H


def rr(l, w, r, z):
    return Plane.XY.offset(z) * RectangleRounded(l, w, min(r, w / 2 - 0.5, l / 2 - 0.5))


def bulb() -> Part:
    top = (SL_OUT_L, SL_OUT_W, BODY_CORNER_R + SLEEVE_WALL)
    outer = loft([rr(*BOTTOM, 0), rr(*BULB, Z_FLARE), rr(*BULB, Z_BULB_TOP), rr(*top, Z_LEDGE)],
                 ruled=True)
    # inner cavity: horizontal offset slightly larger than the wall on slopes
    h = DIFFUSER_WALL * 1.2
    f = DIFFUSER_WALL / Z_FLARE
    b0 = (BOTTOM[0] + (BULB[0] - BOTTOM[0]) * f - 2 * h,
          BOTTOM[1] + (BULB[1] - BOTTOM[1]) * f - 2 * h, BOTTOM[2])
    bi = (BULB[0] - 2 * DIFFUSER_WALL, BULB[1] - 2 * DIFFUSER_WALL, BULB[2] - DIFFUSER_WALL)
    inner = loft([rr(*b0, DIFFUSER_WALL), rr(*bi, Z_FLARE), rr(*bi, Z_BULB_TOP),
                  rr(OPEN_L, OPEN_W, BODY_CORNER_R, Z_LEDGE - LEDGE_T)], ruled=True)
    part = outer - inner
    part -= Pos(0, 0, Z_LEDGE + 1) * extrude(rr(OPEN_L, OPEN_W, BODY_CORNER_R, 0), -LEDGE_T - 2)
    try:
        part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    except Exception:
        pass
    return part


def sleeve() -> Part:
    s = extrude(rr(SL_OUT_L, SL_OUT_W, BODY_CORNER_R + SLEEVE_WALL, Z_LEDGE), SLEEVE_H)
    s -= extrude(rr(SL_IN_L, SL_IN_W, BODY_CORNER_R, Z_LEDGE - 0.1), SLEEVE_H + 1)
    # flex-tab slots
    z0 = Z_SLEEVE_TOP - TAB_L
    for sx in (-1, 1):
        for dx in (-1, 1):
            x = sx * TAB_X + dx * (TAB_W / 2 + SLOT_W / 2)
            s -= Pos(x, 0, z0) * Box(SLOT_W, SL_OUT_W + 2, TAB_L + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # snap lips (45 deg underside, lead-in on top)
    zb = Z_LEDGE + BODY_D + CLEAR_Z
    yi = SL_IN_W / 2
    for sy in (-1, 1):
        prof = Polygon((yi + 0.3, zb - 0.3), (yi - LIP, zb + LIP), (yi - LIP, zb + LIP + 0.4),
                       (yi, Z_SLEEVE_TOP), (yi + 0.3, Z_SLEEVE_TOP), align=None)
        lip = extrude(Plane.YZ * prof, TAB_W / 2, both=True)
        if sy < 0:
            lip = mirror(lip, about=Plane.XZ)
        for sx in (-1, 1):
            s += Pos(sx * TAB_X, 0, 0) * lip
    return s


def bail() -> Part:
    ri = SL_OUT_W / 2 - 0.5
    ro = ri + BAIL_T
    z0 = Z_LEDGE - 7.0
    zl = Z_SLEEVE_TOP + BODY_D + BAIL_EXTRA
    outer = Polygon((-ro, z0), (ro, z0), (ro, zl), (0, zl + ro), (-ro, zl), align=None)
    inner = Polygon((-ri, z0 - 1), (ri, z0 - 1), (ri, zl), (0, zl + ri), (-ri, zl), align=None)
    b = extrude(Plane.YZ * outer, BAIL_WIDTH / 2, both=True) - extrude(Plane.YZ * inner, BAIL_WIDTH, both=True)
    # keep the sleeve cavity free
    b -= extrude(rr(SL_IN_L, SL_IN_W, BODY_CORNER_R, Z_LEDGE - 10), Z_SLEEVE_TOP - Z_LEDGE + 10)
    return b


def build() -> Part:
    return bulb() + sleeve() + bail()
