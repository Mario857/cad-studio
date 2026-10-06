# kalimba-17 — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 224.72 cm3, bbox 287.8x188x30 mm, 3 body, 10956 tris — 3 separate bodies (intended?) |
| walls | OK | thinnest ~1.50 mm (p2), median 3.0 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.6 cm2, overhang 2.6 cm2, contact 498.6 cm2, h 30 mm |
| support | WARN | supports off, brim off; 0.6 cm2 needs support but supports=off |
| slice | OK | 6h13m, 181.7 g (Guitar Core ABS+ 0.20mm @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `kalimba-17.stl`
- **step**: `kalimba-17.step`
- **print**: `kalimba-17.3mf`
- **preview**: `preview.png`
