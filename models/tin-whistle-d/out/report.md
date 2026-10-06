# tin-whistle-d — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 40.49 cm3, bbox 51.3x23.3x232.7 mm, 2 body, 5308 tris — 2 separate bodies (intended?) |
| walls | OK | thinnest ~1.90 mm (p2), median 2.5 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.0 cm2, overhang 2.1 cm2, contact 2.3 cm2, h 233 mm |
| support | WARN | supports off, brim on; wobbly on bed (tips at 6 deg) |
| slice | OK | 6h52m, 32.0 g (0.12mm High Quality @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `tin-whistle-d.stl`
- **step**: `tin-whistle-d.step`
- **print**: `tin-whistle-d.3mf`
- **preview**: `preview.png`
