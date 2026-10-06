"""cat-ball-track: 3-level circular ball-track tower for 40 mm ping-pong balls (cat toy).

Spec:
- Three identical stackable ring levels + a flat lid ring, printed together on one plate
  (2 x 2 layout, 4 separate bodies on purpose - the mesh WARN "4 separate bodies" is intended).
  OD 144 mm, each level 57 mm tall + 3 mm lock rim; stacked tower with lid ~174 mm.
- Each level is a circular channel 46 mm wide (40 mm ball + 6 mm) with 3 mm walls/floor.
  Both channel walls end in 45-degree inward lips (28 mm top slot): they carry the level above,
  print support-free and keep the ball in.
- Ball loading port: the lips are cut away over 54 deg (45 mm along the ball path, 42 mm
  radially) at 90 deg; drop the ball in there, then stack the next level (its floor closes the
  port). The lid closes the top level.
- Paw openings: 3 windows per level through the outer wall, PAW_W = 36 mm wide (< 40 mm ball
  so balls stay in; far below the 45 mm "no head" limit), sill 12 mm, radial sides, 45-degree
  pointed top (no bridge / no supports), all window edges rounded 1 mm.
- Stack + lock: the outer rim (3 mm high) of each level surrounds the inset bottom band
  (0.4 mm radial clearance) of the level above, so levels cannot slide off; three 4.4 mm pins
  on each level's inner lip engage 5.2 mm holes through the floor (or lid) above, locking
  rotation. Gravity holds the stack (no tools, no glue). The lid sits flush inside the top rim.
- Free-standing: COM low, wide base (tip angle >> 12 degrees even stacked).

Hardware: 3 x 40 mm ping-pong balls (one per level, dropped in through the loading port).

Pet safety: ABS must not hold food or water directly and this is NOT a chew toy - supervise
and retire it if chewed or cracked. Every edge a paw can reach is filleted (1 mm; a few tiny
edges at the port/rim corner inside the closed channel may stay sharp if OCC cannot fillet them),
bed edges have a 0.4 mm chamfer, every feature is >= 2.4 mm, windows are too narrow for a cat's
head, and the 40 mm centre column is open at the top so nothing can get trapped.

Assumptions: standard 40 mm table-tennis balls; 3 mm ABS walls are stiff enough for batting;
OD kept at 144 mm so all three levels + lid fit one H2C plate.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[],
    print_orientation="auto",
    supports="auto",
    brim="auto",
)

# Parameters
LEVELS = 3                # levels printed (the plate also gets one lid)
BALL_D = 40.0
CHANNEL_W = 46.0          # radial clear width (ball + 6 mm)
OD = 144.0                # outer diameter
WALL_T = 3.0              # wall / lip thickness
FLOOR_T = 3.0
WALL_H = 45.0             # height where the 45 deg lips start
LIP = 9.0                 # horizontal reach of each lip (45 deg)
TOP_T = 3.0               # vertical tip of lip -> top at WALL_H + LIP + TOP_T
PAW_N = 3
PAW_W = 36.0              # paw opening width (< BALL_D, <= 45 head limit)
PAW_A0 = 30.0             # angle of first opening (keeps revolve seam at 0 deg clear)
WIN_SIDE_TOP = 22.0       # height where the window's 45 deg pointed top starts
PAW_SILL = 12.0           # opening bottom height above level bottom
RIM_T = 3.0               # lock rim radial thickness
RIM_H = 3.0               # lock rim height
LOCK_CLR = 0.4            # radial clearance rim <-> inset band of level above
KEY_D = 4.4               # anti-rotation pin diameter
KEY_R_POS = 26.0          # pin radius (on the inner lip's flat top, clear of the port)
WIN_CORNER_R = 4.0        # window corner radius (elevation)
KEY_H = 2.4               # pin height (< FLOOR_T)
KEY_HOLE_D = 5.2          # matching through-hole in the floor (0.4 mm diametral clearance)
PORT_A = PAW_A0 + 180 / PAW_N    # port angle: midway between two windows
PORT_ANG = 54.0           # port angular width (>= 41 mm at the ball path radius)
PORT_IN = 4.0             # inner-lip stub kept at the port (from inner wall face)
LID_T = 3.0               # lid thickness (= RIM_H, flush)
FILLET_R = 1.0
BED_CH = 0.4
GAP = 4.0                 # plate spacing between levels

R_O = OD / 2
R_OW = R_O - WALL_T                  # outer wall inner face
R_IW = R_OW - CHANNEL_W              # inner wall outer face
R_II = R_IW - WALL_T                 # centre hole radius
H = WALL_H + LIP + TOP_T             # level height (without rim)
R_BAND = R_OW - LOCK_CLR             # inset bottom band radius


def _ring(points):
    return revolve(Plane.XZ * Polygon(*points, align=None), Axis.Z, 360)


def _near_paw(c) -> bool:
    ang = math.degrees(math.atan2(c.Y, c.X)) - PAW_A0
    d = (ang + 180 / PAW_N) % (360 / PAW_N) - 180 / PAW_N
    return abs(d) < math.degrees(PAW_W / 2 / R_OW) + 2


def level() -> Part:
    # whole U-shaped cross-section (floor, both walls, 45 deg lips, lock rim) in one profile
    body = _ring([
        (R_II, 0), (R_BAND, 0), (R_BAND, FLOOR_T),
        (R_O, FLOOR_T + (R_O - R_BAND)),        # 45 deg flare from inset band to full OD
        (R_O, H + RIM_H), (R_OW, H + RIM_H),
        (R_OW, H), (R_OW - LIP, H), (R_OW - LIP, H - TOP_T),
        (R_OW, WALL_H), (R_OW, FLOOR_T), (R_IW, FLOOR_T), (R_IW, WALL_H),
        (R_IW + LIP, WALL_H + LIP), (R_IW + LIP, H), (R_II, H),
    ])
    body = chamfer(body.edges().group_by(Axis.Z)[0], BED_CH)   # elephant-foot chamfer
    for i in range(PAW_N):
        a = PAW_A0 + i * 360 / PAW_N
        # anti-rotation: pin on the outer lip top engages a hole through the floor above
        body += Rot(0, 0, a) * Pos(KEY_R_POS, 0, H) * Cylinder(KEY_D / 2, KEY_H, align=ON_BED)
        body -= Rot(0, 0, a) * Pos(KEY_R_POS, 0, -1) * Cylinder(KEY_HOLE_D / 2, FLOOR_T + 2, align=ON_BED)

    # paw windows through the outer wall: flat sill, radial sides, 45 deg pointed top
    # (support-free, no bridge), corners rounded, entirely below the lip
    r1, r2 = R_OW - 3, R_O + 3
    for i in range(PAW_N):
        a = PAW_A0 + i * 360 / PAW_N
        cutter = loft([Plane.YZ.offset(r1) * _window(r1), Plane.YZ.offset(r2) * _window(r2)])
        body -= Rot(0, 0, a) * cutter

    # ball loading port: lips removed over PORT_ANG so a 40 mm ball drops in from the top;
    # closed by the floor of the level above (or by the lid on the top level)
    port = revolve(Plane.XZ * Polygon((R_IW + PORT_IN, WALL_H - 1), (R_OW, WALL_H - 1),
                                      (R_OW, H + 1), (R_IW + PORT_IN, H + 1), align=None),
                   Axis.Z, PORT_ANG)
    body -= Rot(0, 0, PORT_A - PORT_ANG / 2) * port

    # round every edge a paw can touch: lip/rim circles, pins, port, window outlines
    for r_face in (R_OW, R_O):   # window outlines: inside loops, then outside loops
        body = _round(body, _window_edges(body, r_face), FILLET_R)
    ends = (PORT_A - PORT_ANG / 2, PORT_A + PORT_ANG / 2)
    body = _round(body, [e for e in _top_edges(body) if min(abs(_ang(e) - a) for a in ends) > 1.0],
                  FILLET_R)
    for end in ends:   # port ends: edge by edge (OCC cannot do the whole end in one go)
        done = set()
        while True:
            todo = [e for e in _top_edges(body) if abs(_ang(e) - end) < 1.0
                    and not _is_tangent(body, e) and _key(e) not in done]
            if not todo:
                break
            e = todo[0]
            done.add(_key(e))
            for rr in (FILLET_R, FILLET_R * 0.6):
                try:
                    body = fillet([e], rr)
                    break
                except Exception:
                    pass
            else:
                print("note: port edge left sharp at", _key(e))
    return body


def _window(r):
    # window outline at radius r, widths scaled so the sides run radially
    w = PAW_W / 2 * r / ((R_OW + R_O) / 2)
    p = Polygon((-w, PAW_SILL), (w, PAW_SILL), (w, WIN_SIDE_TOP),
                (0, WIN_SIDE_TOP + PAW_W / 2), (-w, WIN_SIDE_TOP), align=None)
    return fillet(p.vertices().sort_by(Axis.Y)[:-1], WIN_CORNER_R)  # apex stays 45 deg (no flat ceiling)


def _window_edges(body, r_face):
    out = []
    for e in body.edges():
        p = e.position_at(0.5)
        if (PAW_SILL - 0.5 < p.Z < WIN_SIDE_TOP + PAW_W / 2 + 0.5 and _near_paw(p)
                and abs(math.hypot(p.X, p.Y) - r_face) < 0.3):
            out.append(e)
    return out


def _ang(e) -> float:
    p = e.position_at(0.5)
    return math.degrees(math.atan2(p.Y, p.X))


def _top_edges(body):
    return [e for e in body.edges().filter_by_position(Axis.Z, WALL_H - 1, H + RIM_H + 1)
            if not _is_seam(e)]


def _key(e):
    p = e.position_at(0.5)
    return (round(p.X, 1), round(p.Y, 1), round(p.Z, 1))


def _is_tangent(body, e) -> bool:
    fs = [f for f in body.faces() if any(e.is_same(x) for x in f.edges())]
    if len(fs) != 2:
        return True
    p = e.position_at(0.5)
    n0, n1 = fs[0].normal_at(p), fs[1].normal_at(p)
    return n0.dot(n1) > 0.98


def _is_seam(e) -> bool:
    # revolve seam (0 deg) and pin cylinder seams are not real edges - skip them
    if e.geom_type != GeomType.LINE or abs(e.tangent_at(0.5).Z) < 0.99:
        return False
    p = e.position_at(0.5)
    if abs(p.Y) < 0.01 and p.X > 0:
        return True
    for i in range(PAW_N):
        a = math.radians(PAW_A0 + i * 360 / PAW_N)
        if math.hypot(p.X - KEY_R_POS * math.cos(a), p.Y - KEY_R_POS * math.sin(a)) < KEY_D / 2 + 0.2:
            return True
    return False


def _round(body, edges, r):
    for rr in (r, r * 0.8, r * 0.6, r * 0.4):
        try:
            return fillet(edges, rr)
        except Exception:
            pass
    raise ValueError(f"could not round {len(edges)} edges")


def lid() -> Part:
    # flat ring that drops inside the top level's rim, flush with it, located by the 3 pins
    body = _ring([(R_II, 0), (R_BAND, 0), (R_BAND, LID_T), (R_II, LID_T)])
    body = chamfer(body.edges().group_by(Axis.Z)[0], BED_CH)
    for i in range(PAW_N):
        a = PAW_A0 + i * 360 / PAW_N
        body -= Rot(0, 0, a) * Pos(KEY_R_POS, 0, -1) * Cylinder(KEY_HOLE_D / 2, LID_T + 2, align=ON_BED)
    return fillet(body.edges().group_by(Axis.Z)[-1], FILLET_R)


def build():
    lv = level()
    # plate layout 2 x 2: three levels + lid (fits 300 x 320)
    p = (OD + GAP) / 2
    spots = [(-p, -p), (p, -p), (-p, p)][:LEVELS]
    return [Pos(x, y, 0) * lv for x, y in spots] + [Pos(p, p, 0) * lid()]
