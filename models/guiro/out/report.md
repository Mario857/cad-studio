# guiro — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 304.4 cm3, bbox 167.5x88x162 mm, 3 body, 12566 tris — 3 separate bodies (intended?) |
| walls | OK | thinnest ~2.50 mm (p2), median 4.7 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.4 cm2, overhang 1.8 cm2, contact 86.7 cm2, h 162 mm |
| support | OK | supports off, brim off |
| slice | OK | 6h07m, 170.8 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `guiro.stl`
- **step**: `guiro.step`
- **print**: `guiro.3mf`
- **preview**: `preview.png`
