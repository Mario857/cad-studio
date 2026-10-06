# door-wall-bumper — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 45.31 cm3, bbox 156x60x20 mm, 3 body, 8154 tris — 3 separate bodies (intended?) |
| walls | OK | thinnest ~1.60 mm (p2), median 3.07 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | as modeled: support 0.0 cm2, overhang 11.4 cm2, contact 37.5 cm2, h 20 mm [next: +Y down 152.1; -Y down 152.1] |
| support | OK | supports off, brim off |
| slice | OK | 1h09m, 28.3 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `door-wall-bumper.stl`
- **step**: `door-wall-bumper.step`
- **print**: `door-wall-bumper.3mf`
- **preview**: `preview.png`
