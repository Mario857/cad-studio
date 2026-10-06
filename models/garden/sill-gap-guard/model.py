"""sill-gap-guard: 250 mm T-profile plug that presses into a 10-14 mm sliding-window track gap.

Spec: cap flange 20 mm wide x 2 mm; stem 12 mm wide x 14 mm deep; 3 flex fins per side
(fin tip span 17 mm, 45 deg barbs, 1.2 mm blades) that compress to fit 10 mm and bite at 14 mm.
Extruded along Y (250 mm). Printed on its side (cap vertical), zero supports.
Assumptions: fin tip corners are acute (45 deg) so the walls WARN there is intended (flex barb). PETG (TPU would be softer/better seal); fins flex ~3.5 mm per side in total range.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PETG",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 180, 0),  # cap flat on bed, stem up; length stays along Y
    supports="off",
    brim="auto",
)

LENGTH = 250.0
CAP_W = 20.0
CAP_T = 2.0
STEM_W = 12.0
STEM_D = 14.0
FIN_TIP_X = 8.5      # half span at fin tip (17 mm)
FIN_RISE = 2.5       # 45 deg barb: out == up
FIN_T = 1.8
FIN_ZS = (-13.0, -9.5, -6.0)  # fin root heights (blade bottom)


def build() -> Part:
    h = STEM_W / 2
    pts = [(-CAP_W / 2, 0), (CAP_W / 2, 0), (CAP_W / 2, -CAP_T), (h, -CAP_T),
           (h, -STEM_D + 1.0), (h - 1.0, -STEM_D), (-h + 1.0, -STEM_D), (-h, -STEM_D + 1.0),
           (-h, -CAP_T), (-CAP_W / 2, -CAP_T)]
    prof = Polygon(*pts, align=None)
    for z in FIN_ZS:
        for s in (1, -1):
            q = [(s * (h - 0.3), z), (s * FIN_TIP_X, z + FIN_RISE),
                 (s * FIN_TIP_X, z + FIN_RISE + FIN_T), (s * (h - 0.3), z + FIN_T)]
            prof += Polygon(*q, align=None)
    # profile in XZ (local y = +Z); extrude along -Y normal then centre on Y
    return extrude(Plane.XZ * prof, LENGTH / 2, both=True)
