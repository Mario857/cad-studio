# bill-due-board — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 287.53 cm3, bbox 268x16x237.5 mm, 11 body, 92964 tris — 11 separate bodies (intended?) |
| walls | OK | thinnest ~0.88 mm (p2), median 5.0 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (-90, 0, 0): support 1.7 cm2, overhang 3.1 cm2, contact 563.0 cm2, h 16 mm |
| support | WARN | supports off, brim on; 1.7 cm2 needs support but supports=off |
| slice | OK | 4h09m, 138.7 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `bill-due-board.stl`
- **step**: `bill-due-board.step`
- **print**: `bill-due-board.3mf`
- **preview**: `preview.png`
