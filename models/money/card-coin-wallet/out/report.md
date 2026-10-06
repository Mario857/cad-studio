# card-coin-wallet — PASS (3 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 25.42 cm3, bbox 87.4x119.9x11.5 mm, 2 body, 4694 tris — 2 separate bodies (intended?) |
| walls | WARN | thinnest ~1.20 mm (p2), median 1.54 mm; 95.0% of surface < 1.2 mm near [43.7, -8.9, 4.7] |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, -90, 0): support 4.0 cm2, overhang 4.2 cm2, contact 5.1 cm2, h 87 mm |
| support | WARN | supports off, brim on; 4.0 cm2 needs support but supports=off; wobbly on bed (tips at 5 deg) |
| slice | OK | 3h05m, 25.6 g (0.12mm High Quality @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `card-coin-wallet.stl`
- **step**: `card-coin-wallet.step`
- **print**: `card-coin-wallet.3mf`
- **preview**: `preview.png`
