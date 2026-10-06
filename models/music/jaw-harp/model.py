"""jaw-harp: printed jaw (mouth) harp, reed tuned to E2 (82.4 Hz), printed flat.

Spec
- Rigid U-frame (two 5 x 4 mm arms + root block + holding ring) with a free reed
  REED_W x REED_T (4 x 0.92 mm) running between the arms, separated by a GAP = 0.4 mm slit on
  each side, free end extending TAB_CLEAR past the arm tips into a small flat plucking tab.
- Play: press the arms lightly against slightly parted front teeth (reed side = flat bed side
  toward the teeth), lips around, pluck the tab out-of-plane; shape the mouth to pick overtones.

Print orientation decision
- Printed flat (reed lies on the bed). The reed vibrates out of the frame plane (Z) through
  the slit - the jaw-harp action needs that. Its bending strain runs along the reed length,
  i.e. along the extrusion lines inside every layer; layers are parallel to the neutral plane,
  so no load pulls layers apart (only small interlaminar shear). The 0.4 mm slit is cut in XY
  where the printer is most precise; the 0.4 mm bottom chamfer keeps elephant foot from
  welding the slit shut.

Physics (bare rectangular cantilever, ABS E = 2.0 GPa, rho = 1040 kg/m3)
    f0 = 0.1615 * (t / L^2) * sqrt(E / rho)
  tab mass M at distance a beyond the tip (Rayleigh, static tip-load shape):
    f = f0 * sqrt(0.2357 m / (0.2357 m + M (1 + 1.5 a / L)^2)),  m = reed mass
  L is solved numerically for TARGET_HZ.

TUNING
  note | target Hz | computed reed length L (root -> tab), t = 0.92 mm, w = 4 mm
  E2   | 82.41     | ~41 mm  (exact: `python model.py`, recomputed on every build)

Fine-tuning after printing
- Measure with a tuner app close to the mouth (jaw harps sound the fundamental weakly; read
  the drone). The slicer rounds REED_T to whole layers - pitch scales ~linearly with t.
- Too high -> add mass to the tab: a drop of CA glue / tiny blob of epoxy (each ~10 mg lowers
  a few %), or file the reed thinner near its ROOT.
- Too low -> file/sand the tab smaller (less mass), or thin the reed near the tip only.
- Reed rubbing the arms (buzzy) -> run a 0.3 mm feeler/blade through the slit; if the reed
  is warped, warm gently with a hair dryer and straighten.

Hardware: none.
Assembly: one piece. Remove brim if any, clear the slits with a blade, deburr the tab.
ABS is not food-safe — personal use, rinse after playing.

Assumptions
- ABS modulus 2.0 GPa (printed ABS+ is ~1.8-2.2: +-5 % pitch); air loading of the reed
  neglected; quality "fine" (0.12 mm layers) for a thin accurate reed.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],                  # walls WARN (<1.2 mm) is the 0.92 mm reed: thin by design, it must flex
    print_orientation=(0, 0, 0),  # flat: reed strain along layers, slit cut in XY
    supports="off",
    brim="auto",
)

# Tuning / material
TARGET_HZ = 82.41      # E2
E_MOD = 2.0e9
RHO = 1040.0

# Reed
REED_T = 0.92          # Z thickness (0.2 first layer + 6 x 0.12)
REED_W = 4.0
GAP = 0.4
TAB = (6.0, 6.0, 0.92)  # plucking tab x, y, z (beyond the reed)
TAB_CLEAR = 4.0        # reed sticks out past the arm tips by this

# Frame
FRAME_T = 4.0
ARM_W = 5.0
ROOT_LEN = 12.0
RING_OD, RING_ID = 30.0, 16.0
CHAMFER = 0.4


def reed_length(f=TARGET_HZ):
    """Solve cantilever length (mm) with tab mass for frequency f (Hz)."""
    c_l = math.sqrt(E_MOD / RHO)
    t, w = REED_T / 1000, REED_W / 1000
    m_tab = TAB[0] * TAB[1] * TAB[2] * 1e-9 * RHO
    a = TAB[0] / 2 / 1000
    lo, hi = 0.005, 0.3
    for _ in range(80):
        L = (lo + hi) / 2
        f0 = 0.1615 * t / L ** 2 * c_l
        m = L * w * t * RHO
        ff = f0 * math.sqrt(0.2357 * m / (0.2357 * m + m_tab * (1 + 1.5 * a / L) ** 2))
        lo, hi = (L, hi) if ff > f else (lo, L)
    return L * 1000


def build() -> Part:
    L = reed_length()
    inner = REED_W + 2 * GAP
    width = inner + 2 * ARM_W
    arm_len = L - TAB_CLEAR

    def bed_box(lx, ly, lz, x0, y, ch=CHAMFER):
        b = Box(lx, ly, lz, align=(Align.MIN, Align.CENTER, Align.MIN))
        b = chamfer(b.edges().group_by(Axis.Z)[0], ch)
        return Pos(x0, y, 0) * b

    frame = bed_box(ROOT_LEN + 1, width, FRAME_T, -ROOT_LEN, 0)
    for s in (-1, 1):
        frame += bed_box(arm_len + 1, ARM_W, FRAME_T, -1, s * (inner + ARM_W) / 2)
    ring = Cylinder(RING_OD / 2, FRAME_T, align=ON_BED)
    ring = chamfer(ring.edges().group_by(Axis.Z)[0], CHAMFER)
    ring -= Cylinder(RING_ID / 2, FRAME_T * 3)
    frame += Pos(-ROOT_LEN - RING_OD / 2 + 3, 0, 0) * ring

    reed = bed_box(L + 1, REED_W, REED_T, -1, 0, 0.3)
    reed += bed_box(TAB[0], TAB[1], TAB[2], L, 0, 0.3)
    return frame + reed


if __name__ == "__main__":
    print(f"E2 {TARGET_HZ} Hz -> reed L = {reed_length():.1f} mm")
