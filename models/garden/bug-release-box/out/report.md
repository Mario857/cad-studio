# bug-release-box — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 26.42 cm3, bbox 68x80.5x30 mm, 2 body, 1794 tris — 2 separate bodies (intended?) |
| walls | OK | thinnest ~0.56 mm (p2), median 4.1 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.0 cm2, overhang 0.1 cm2, contact 43.6 cm2, h 30 mm |
| support | OK | supports off, brim off |
| slice | OK | 48m, 19.0 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `bug-release-box.stl`
- **step**: `bug-release-box.step`
- **print**: `bug-release-box.3mf`
- **preview**: `preview.png`
