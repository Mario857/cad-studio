# string-winder — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 35.94 cm3, bbox 120x63x40.1 mm, 3 body, 25990 tris — 3 separate bodies (intended?) |
| walls | OK | thinnest ~1.63 mm (p2), median 6.84 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (180, 0, 0): support 0.1 cm2, overhang 0.6 cm2, contact 28.5 cm2, h 40 mm |
| support | OK | supports off, brim off |
| slice | OK | 1h06m, 24.7 g (Guitar Core ABS+ 0.20mm @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `string-winder.stl`
- **step**: `string-winder.step`
- **print**: `string-winder.3mf`
- **preview**: `preview.png`
