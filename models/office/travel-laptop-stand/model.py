"""travel-laptop-stand: Roost-style folding travel stand for a MacBook Pro 13" and 15" (BRIEF ONLY, gated).

STATUS: geometry not designed yet. Gate (CLAUDE.md waste prevention): the hook slot mates with an
UNVERIFIED laptop dimension and the first print would be HIGH cost, so the fit gauge
`travel-laptop-stand-fit-gauge` is printed first. build() raises until the gauge result is in.

Function: lifts the laptop screen to eye level on a desk (used with an external keyboard), folds to a
  bundle of bars for a bag. Indoor use, but it travels: bags, trains, a parked car -> PETG (PLA softens at
  ~55-60 C; PETG is also tougher for the hook fingers).
Concept (as the reference photo): two X side frames + two plug-in spreaders.
  - Bar A (rest arm): front foot on the desk, rises to the rear; the laptop underside rests on its top end.
  - Bar B (hook strut): rear foot on the desk, rises to the front; its top end carries the hook that holds
    the laptop's front edge. A and B cross at a pivot with a hard stop at the open angle.
  - Spreaders plug into square sockets at the feet and set the frame spacing; pulled out to fold.
  - All bars are flat profiles printed lying down, so every load runs along the layers.
Mechanism (docs/mechanisms.md): pivot = metal M5 bolt + nyloc nut (not a printed pin); stop = solid block,
  no flex parts; spreader tenons = slip fit via clearance(); hook root >= 3 mm with a rib.

Dimensions
  laptop 13": 304.1 x 212.4 x 15.6 closed, 1.40 kg   MEASURED (Apple spec, obj("macbook-pro-13"))
  laptop 15": 349.3 x 240.7 x 15.5 closed, 1.83 kg   MEASURED (Apple spec, obj("macbook-pro-15"))
  base front-edge thickness, lid open: ~11            UNVERIFIED -> fit gauge (slots 10..16)
  model years of the two laptops (Touch Bar era assumed) UNVERIFIED -> ask the user
  hook height above desk 110, laptop tilt ~18 deg, frame spacing 200 (inside both laptop widths): design
    targets, not mating dimensions
  pivot M5 clearance hole                              MEASURED (standard, cadlib METRIC)
Loads: 1.83 kg laptop (18 N) + ~20 N hand pressure while opening the lid or plugging a cable = 40 N,
  20 N per side frame, static; fold/unfold a few hundred times.

Assumptions
  - Two M5 x 20 bolts + nyloc nuts are acceptable hardware (else: printed Ø8 pin, weaker and looser).
  - The laptop is not typed on while on the stand.
  - Target mass <= 200 g, folded bundle <= 300 x 60 x 35 mm.
Risks
  - Side-to-side wobble from play in the spreader sockets (most likely complaint).
  - Hook finger cracks if the laptop is lifted by its rear with the edge still in the hook.
  - Feet slide on a smooth desk -> needs TPU or stick-on rubber pads.
  - PETG creeps at the stop in a hot car under load: store it folded.
Accept
  - Both laptops' front edges enter the hooks with no force and cannot lift out vertically.
  - 15" laptop sits 30 min: hook height stays within 110 +/- 5 mm, no creep at the stop.
  - 2 kg pressed on the laptop's rear edge: no collapse, feet stay down.
  - 5 N sideways push on the laptop: sway < 5 mm.
  - Folded bundle <= 300 x 60 x 35 mm, total <= 200 g.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PETG",
    quality="strong",
    status="draft",
    standing=True,
    loads=[dict(at=(0, 0, 150), grams=1830)],
    force=[dict(at=(0, 0, 150), newtons=40, dir=(0, 0, -1))],
)


def build() -> Part:
    raise NotImplementedError(
        "gated: print travel-laptop-stand-fit-gauge, report the slot that fits each laptop, then design the stand")
