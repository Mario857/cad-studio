# first-aid-case — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 89.25 cm3, bbox 136.2x296.6x35.6 mm, 4 body, 7716 tris — 4 separate bodies (intended?) |
| walls | OK | thinnest ~1.20 mm (p2), median 2.3 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.6 cm2, overhang 5.2 cm2, contact 222.3 cm2, h 36 mm |
| support | WARN | supports off, brim off; 0.6 cm2 needs support but supports=off |
| slice | OK | 2h25m, 77.3 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `first-aid-case.stl`
- **step**: `first-aid-case.step`
- **print**: `first-aid-case.3mf`
- **preview**: `preview.png`
