# card-wallet — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 12.45 cm3, bbox 87.4x58.8x9.1 mm, 1 body, 3556 tris |
| walls | WARN | thinnest ~1.11 mm (p2), median 1.42 mm; 94.6% of surface < 1.2 mm near [14.4, -8.9, 2.0] |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, -90, 0): support 0.2 cm2, overhang 0.7 cm2, contact 3.7 cm2, h 87 mm |
| support | WARN | supports off, brim on; wobbly on bed (tips at 4 deg) |
| slice | OK | 2h32m, 12.6 g (0.12mm High Quality @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `card-wallet.stl`
- **step**: `card-wallet.step`
- **print**: `card-wallet.3mf`
- **preview**: `preview.png`
