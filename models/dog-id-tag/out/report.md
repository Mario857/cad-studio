# dog-id-tag — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 5.14 cm3, bbox 91x39.2x3.3 mm, 2 body, 57760 tris — 2 separate bodies (intended?) |
| walls | WARN | thinnest ~0.74 mm (p2), median 2.72 mm; 4.1% of surface < 1.2 mm near [-24.9, -6.0, 2.8] |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.1 cm2, overhang 0.1 cm2, contact 18.6 cm2, h 3 mm |
| support | OK | supports off, brim off |
| slice | OK | 21m, 4.9 g (0.12mm High Quality @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `dog-id-tag.stl`
- **step**: `dog-id-tag.step`
- **print**: `dog-id-tag.3mf`
- **preview**: `preview.png`
