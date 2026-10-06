# wall-clock — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 214.14 cm3, bbox 250x7.5x250 mm, 1 body, 2170 tris |
| walls | OK | thinnest ~2.00 mm (p2), median 7.5 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (-90, 0, 0): support 2.0 cm2, overhang 2.0 cm2, contact 485.6 cm2, h 8 mm |
| support | WARN | supports off, brim on; 2.0 cm2 needs support but supports=off |
| slice | OK | 3h09m, 113.8 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `wall-clock.stl`
- **step**: `wall-clock.step`
- **print**: `wall-clock.3mf`
- **preview**: `preview.png`
