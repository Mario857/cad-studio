# paper-towel-holder — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 207.71 cm3, bbox 28x174x297 mm, 3 body, 2260 tris — 3 separate bodies (intended?) |
| walls | OK | thinnest ~3.72 mm (p2), median 8.69 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 90, 0): support 0.9 cm2, overhang 68.4 cm2, contact 95.4 cm2, h 28 mm |
| support | WARN | supports off, brim on; 0.9 cm2 needs support but supports=off |
| slice | OK | 4h31m, 148.7 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `paper-towel-holder.stl`
- **step**: `paper-towel-holder.step`
- **print**: `paper-towel-holder.3mf`
- **preview**: `preview.png`
