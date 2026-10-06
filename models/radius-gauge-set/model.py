"""radius-gauge-set: understring fretboard radius gauges, 7.25" / 9.5" / 10" / 12" / 14" / 16".

Spec
- Six flat gauges, all printed together on one plate, lying flat (6 separate bodies = intended).
- Each gauge is a curved band GAUGE_W (70 mm) wide, BODY_H tall, THICKNESS thick:
  * Bottom edge: CONCAVE arc of radius R -> sits on the (convex) fretboard / fret tops.
    It is a comb: SLOT_N open slots (one per string) let the gauge drop over strung
    strings, so the legs between strings touch the board ("understring" style).
  * Top edge: matching CONVEX arc of the same radius, continuous (no slots) - for
    checking saddles, bridge inserts, sanding blocks, nut slot bottoms, etc.
  * Engraved on the face: nominal radius in inches (large) and in mm (small),
    TEXT_DEPTH deep, >= 5 mm cap height.
  * KEYRING_D hole at one end so the set can live on a split ring.
- Guitar contact / finish safety: all vertical plate corners, slot corners and leg tips are
  filleted (EDGE_FILLET >= 1 mm) and the bed edge has a 0.4 mm chamfer, so nothing sharp can
  scratch the finish. The gauging arcs themselves stay sharp in profile (the arc is the
  measuring reference and is never rounded or offset). There is deliberately NO felt or
  rubber pad on the gauging edges - they must contact the frets/board directly to read
  correctly. Note: some rubbers/plasticisers react with nitrocellulose finishes; if anything
  is added to rest on the guitar (e.g. a pad on a holder), use felt, not rubber.
- Accuracy: FDM parts hold roughly +/-0.1 mm in XY. Over the 70 mm chord the sagitta
  difference between 9.5" and 10" is only ~0.15 mm, so adjacent sizes are best judged by
  light gap / rocking, not by absolute fit. Fine for setup work, not a metrology standard.

Assumptions
- String pitch at the measuring position ~SLOT_PITCH (10 mm, mid neck / 12th fret); slots are
  SLOT_W wide (+/-2.5 mm tolerance per string) so they work from ~7th fret to the neck pocket.
- String height above the board at the measuring spot < SLOT_DEPTH - 2 mm (frets + action).
- Radius values are exact inch conversions (1" = 25.4 mm).
- Hardware: optional ~25 mm split key ring through the KEYRING_D holes.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # flat, face up: arcs are XY outlines -> best accuracy
    supports="off",
    brim="auto",
)

# Parameters
RADII_IN = [7.25, 9.5, 10.0, 12.0, 14.0, 16.0]   # nominal fretboard radii, inches
INCH = 25.4
GAUGE_W = 70.0          # chord width of each gauge (X)
BODY_H = 34.0           # band height between concave and convex arcs (Y)
THICKNESS = 3.0         # plate thickness (Z, as printed)
SLOT_N = 6              # one slot per string
SLOT_PITCH = 10.0       # slot centre spacing
SLOT_W = 5.0            # slot width (string passes through)
SLOT_DEPTH = 8.0        # slot depth from the concave edge at slot centre
EDGE_FILLET = 1.0       # vertical edge fillets (corners, slot corners, leg tips)
BOTTOM_CHAMFER = 0.4    # elephant-foot chamfer on bed edges
KEYRING_D = 5.0         # nominal keyring hole
KEYRING_X = 29.0        # hole centre from gauge centre (X)
KEYRING_Y = 22.0        # hole centre height above arc crest (Y)
TEXT_DEPTH = 0.6
TEXT_BIG = 8.0          # inch label size (~6 mm cap height)
TEXT_SMALL = 7.0        # mm label size (~5.3 mm cap height)
TEXT_BIG_Y = 23.0
TEXT_SMALL_Y = 13.5
LAYOUT_DX = 78.0        # plate layout: 2 columns x 3 rows
LAYOUT_DY = 42.0


def concave_y(r: float, x: float) -> float:
    """Height of the concave gauging edge at x (crest at x=0, y=0)."""
    return (r * r - x * x) ** 0.5 - r


def gauge(r_in: float) -> Part:
    r = r_in * INCH
    big = Rectangle(GAUGE_W, 4 * BODY_H)
    outline = (Pos(0, BODY_H - r) * Circle(r)) - (Pos(0, -r) * Circle(r))
    outline = outline & big
    for i in range(SLOT_N):
        x = (i - (SLOT_N - 1) / 2) * SLOT_PITCH
        outline -= Pos(x, concave_y(r, x)) * Rectangle(SLOT_W, 2 * SLOT_DEPTH)
    part = extrude(outline, THICKNESS)
    part = fillet(part.edges().filter_by(Axis.Z), EDGE_FILLET)
    part = chamfer(part.edges().group_by(Axis.Z)[0], BOTTOM_CHAMFER)
    part -= Pos(KEYRING_X, KEYRING_Y, 0) * Cylinder(KEYRING_D / 2, THICKNESS, align=ON_BED)
    inch_txt = f'{r_in:g}"'
    mm_txt = f"R{r:.1f} mm"
    part -= Pos(0, TEXT_BIG_Y, THICKNESS - TEXT_DEPTH) * label(inch_txt, size=TEXT_BIG, depth=TEXT_DEPTH + 0.01)
    part -= Pos(0, TEXT_SMALL_Y, THICKNESS - TEXT_DEPTH) * label(mm_txt, size=TEXT_SMALL, depth=TEXT_DEPTH + 0.01)
    return part


def build():
    parts = []
    for i, r_in in enumerate(RADII_IN):
        col, row = i % 2, i // 2
        parts.append(Pos((col - 0.5) * LAYOUT_DX, row * LAYOUT_DY, 0) * gauge(r_in))
    return parts
