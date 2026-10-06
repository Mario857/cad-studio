# bottle-drip-spike — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 32.12 cm3, bbox 91.2x34.4x151.4 mm, 5 body, 13718 tris — 5 separate bodies (intended?) |
| walls | OK | thinnest ~1.20 mm (p2), median 4.76 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (180, 0, 0): support 0.1 cm2, overhang 1.6 cm2, contact 6.2 cm2, h 151 mm |
| support | OK | supports off, brim on |
| slice | OK | 3h34m, 47.7 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `bottle-drip-spike.stl`
- **step**: `bottle-drip-spike.step`
- **print**: `bottle-drip-spike.3mf`
- **preview**: `preview.png`
