# rain-gauge — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 240.32 cm3, bbox 221x163.4x238 mm, 3 body, 43306 tris — 3 separate bodies (intended?) |
| walls | OK | thinnest ~2.26 mm (p2), median 2.43 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.8 cm2, overhang 5.4 cm2, contact 87.9 cm2, h 238 mm |
| support | WARN | supports off, brim off; 0.8 cm2 needs support but supports=off |
| slice | OK | 6h59m, 131.5 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `rain-gauge.stl`
- **step**: `rain-gauge.step`
- **print**: `rain-gauge.3mf`
- **preview**: `preview.png`
