# recorder-soprano — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 75.38 cm3, bbox 91.5x23x143.3 mm, 3 body, 13768 tris — 3 separate bodies (intended?) |
| walls | OK | thinnest ~1.96 mm (p2), median 4.58 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.1 cm2, overhang 3.1 cm2, contact 4.9 cm2, h 143 mm |
| support | WARN | supports off, brim on; wobbly on bed (tips at 10 deg) |
| slice | OK | 4h50m, 42.3 g (0.12mm High Quality @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `recorder-soprano.stl`
- **step**: `recorder-soprano.step`
- **print**: `recorder-soprano.3mf`
- **preview**: `preview.png`
