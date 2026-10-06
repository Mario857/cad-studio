"""emergency-whistle: pea-less triple-chamber safety whistle that threads onto a sternum strap.

Spec: Fox-40-style pea-less whistle with three parallel closed (stopped) chambers, side by side,
each fed by its own wall-formed windway from a shared mouthpiece. The jet leaves each windway,
crosses an open window in the top wall and splits on a bevelled labium edge. The three chambers
are slightly detuned so the combined tone beats (~150 Hz roughness), which carries further and is
easier to notice than one pure tone. A tunnel under the body (STRAP_W x STRAP_GAP) threads onto a
20-25 mm backpack sternum strap; the whistle lies along the strap with the mouthpiece pointing sideways.

Acoustics (quarter-wave closed pipe approximation):
    f = c / (4 * (L + e)),  c = 343 m/s
    L = distance from window centre to the closed chamber end
    e = 0.6 * a end correction at the window, a = sqrt(BORE_W * BORE_H / pi) (equivalent radius)
    BORE 6 x 7 mm -> a = 3.66 mm, e = 2.19 mm
    target 2500 / 2650 / 2800 Hz -> L + e = 34.30 / 32.36 / 30.63 mm
                                  -> L = 32.11 / 30.17 / 28.43 mm (computed in CHAMBER_L below)
    Real pitch depends on blowing pressure and print accuracy; expect +/-10 %, still in 2-3 kHz.

Print: mouthpiece up (model +X -> print -Z), closed chamber ends + strap tunnel on the bed.
The windways, chambers and strap tunnel are then vertical channels; the labium bevel faces up;
the block under each windway and the windway roof both end in 45 deg edges (no bridges). No supports anywhere (supports must stay off: they could not be removed from inside).

Assumptions:
- Webbing up to 25 mm wide and <= 2.5 mm thick (STRAP_W 26, STRAP_GAP 3.0); strap end is free to thread.
- Windway 1.2 mm high is a typical pea-less whistle value; labium edge at windway mid-height.
- Material: ABS is NOT food-safe; rinse before first use and after storage; personal use only.
- Fine quality is used so the 1.2 mm windway and labium edge come out clean; clear any stringing
  from the windways with a 1 mm card before use.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],
    print_orientation=(0, 90, 0),  # mouthpiece up, chamber ends on bed: windways/labium need no supports
    supports="off",
    brim="auto",
)

# Acoustics
C_SOUND = 343_000.0                  # mm/s
FREQS = (2500.0, 2650.0, 2800.0)     # Hz, detuned for beating

# Chamber / windway
BORE_W = 6.0          # chamber width (Y)
BORE_H = 7.0          # chamber height (Z)
WINDWAY_H = 1.2       # windway (air slot) height
WINDWAY_W = BORE_W    # windway width = chamber width
WINDOW_L = 4.0        # window length along the jet (windway exit -> labium edge)
LABIUM_ANGLE = 25.0   # labium bevel angle from horizontal (deg)
LABIUM_OFFSET = WINDWAY_H / 2  # labium edge sits this far below the windway roof (jet centre)
ROOF_BEVEL = True     # 45 deg bevel on the windway-roof end (window top) instead of a flat bridge
MOUTH_L = 16.0        # windway / mouthpiece length
MOUTH_TAPER_X = 7.0   # mouthpiece bottom starts tapering this far before the windway exit

# Walls
WALL = 1.6            # outer walls
INNER_WALL = 1.4      # between chambers
END_WALL = 1.6        # closed chamber end

# Strap tunnel (sternum strap 20-25 mm)
STRAP_W = 26.0        # tunnel width (webbing width + clearance)
STRAP_GAP = 3.0       # tunnel height (webbing thickness + clearance)
STRAP_PLATE = 2.0     # back plate thickness (loaded)
STRAP_POST = 2.0      # side post width
STRAP_START = 6.0     # tunnel/back plate starts at this x (after the window)
DIAMOND = 7.0         # lightening diamond diagonal in back plate

EQ_R = math.sqrt(BORE_W * BORE_H / math.pi)
END_CORR = 0.6 * EQ_R
CHAMBER_L = tuple(C_SOUND / (4 * f) - END_CORR for f in FREQS)  # from window centre

PITCH = BORE_W + INNER_WALL
BODY_W = 3 * BORE_W + 2 * INNER_WALL + 2 * WALL
LOOP_W = STRAP_W + 2 * STRAP_POST

# Z stack (in use)
Z_BODY = STRAP_PLATE + STRAP_GAP           # body bottom = tunnel roof
ZB = Z_BODY + WALL                         # bore bottom
ZT = ZB + BORE_H                           # bore top = labium edge height
ZF = ZT - LABIUM_OFFSET                    # windway floor
ZR = ZF + WINDWAY_H                        # windway roof
Z_TOP = ZR + WALL

X_END = WINDOW_L / 2 + max(CHAMBER_L) + END_WALL


def _xz_prism(pts, y0, y1):
    """Polygon in (x, z) extruded from y0 to y1."""
    face = Plane.XZ * Polygon(*pts, align=None)   # Plane.XZ: local y = +Z, normal -Y
    return Pos(0, y1, 0) * extrude(face, y1 - y0)


def build() -> Part:
    # body outline in XZ incl. tapered mouthpiece bottom
    body_pts = [(-MOUTH_L, ZF - WALL), (-MOUTH_TAPER_X, Z_BODY), (X_END, Z_BODY),
                (X_END, Z_TOP), (-MOUTH_L, Z_TOP)]
    part = _xz_prism(body_pts, -BODY_W / 2, BODY_W / 2)

    # strap loop block (tunnel roof flanges, posts, back plate)
    loop = Pos((STRAP_START + X_END) / 2, 0, 0) * Box(
        X_END - STRAP_START, LOOP_W, Z_BODY + WALL, align=(Align.CENTER, Align.CENTER, Align.MIN))
    part = part + loop

    cut = None
    for i, L in enumerate(CHAMBER_L):
        y = (i - 1) * PITCH
        y0, y1 = y - BORE_W / 2, y + BORE_W / 2
        x_close = WINDOW_L / 2 + L
        undercut = ZF - ZB
        # chamber incl. 45 deg undercut under the block (windway floor ends in a 90 deg edge)
        ch = _xz_prism([(0, ZT), (0, ZF), (-undercut, ZB), (x_close, ZB),
                        (x_close, ZT)], y0, y1)
        # windway
        ww = _xz_prism([(-MOUTH_L - 1, ZF), (0.01, ZF), (0.01, ZR), (-MOUTH_L - 1, ZR)],
                       y - WINDWAY_W / 2, y + WINDWAY_W / 2)
        # window + labium bevel (bevel rises from the labium edge toward +X)
        run = (Z_TOP - ZT) / math.tan(math.radians(LABIUM_ANGLE))
        win = _xz_prism([(0, ZT - 0.01), (WINDOW_L, ZT - 0.01), (WINDOW_L + run, Z_TOP + 0.01),
                         (-(Z_TOP - ZR) - 0.01, Z_TOP + 0.01), (0, ZR)], y0, y1)
        c = ch + ww + win
        cut = c if cut is None else cut + c

    # strap tunnel (through along X)
    tunnel = Pos((STRAP_START + X_END) / 2, 0, STRAP_PLATE) * Box(
        X_END - STRAP_START + 2, STRAP_W, STRAP_GAP, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cut = cut + tunnel

    # lightening diamonds in the back plate (45 deg sides -> support-free in print)
    plate_len = X_END - STRAP_START
    n = 2
    for k in range(n):
        xc = STRAP_START + plate_len * (k + 0.5) / n
        for yc in (-STRAP_W / 4, STRAP_W / 4):
            d = Pos(xc, yc, -0.5) * Rot(0, 0, 45) * Box(DIAMOND / math.sqrt(2), DIAMOND / math.sqrt(2),
                                                    STRAP_PLATE + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
            cut = cut + d

    part = part - cut

    # elephant-foot chamfer on the bed face (x = X_END)
    try:
        bed_edges = part.edges().group_by(Axis.X)[-1]
        part = chamfer(bed_edges, 0.4)
    except Exception:
        pass
    return part
