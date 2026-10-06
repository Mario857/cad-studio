# soprano-ukulele — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 896.16 cm3, bbox 224x315.5x240 mm, 4 body, 10408 tris — 4 separate bodies (intended?) |
| walls | OK | thinnest ~2.96 mm (p2), median 13.0 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 1.1 cm2, overhang 55.5 cm2, contact 167.9 cm2, h 240 mm |
| support | WARN | supports off, brim on; 1.1 cm2 needs support but supports=off |
| slice | OK | 16h19m, 478.6 g (Guitar Core ABS+ 0.20mm @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `soprano-ukulele.stl`
- **step**: `soprano-ukulele.step`
- **print**: `soprano-ukulele.3mf`
- **preview**: `preview.png`
