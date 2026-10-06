# tambourine — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 184.72 cm3, bbox 200x200x49.6 mm, 1 body, 21324 tris |
| walls | OK | thinnest ~2.10 mm (p2), median 10.0 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 1.6 cm2, overhang 39.0 cm2, contact 52.5 cm2, h 50 mm |
| support | WARN | supports off, brim off; 1.6 cm2 needs support but supports=off |
| slice | OK | 4h52m, 123.7 g (Guitar Core ABS+ 0.20mm @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `tambourine.stl`
- **step**: `tambourine.step`
- **print**: `tambourine.3mf`
- **preview**: `preview.png`
