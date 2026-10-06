# bug-crank-eater — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 423.77 cm3, bbox 264x247.3x136 mm, 5 body, 4700 tris — 5 separate bodies (intended?) |
| walls | OK | thinnest ~1.67 mm (p2), median 6.0 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.1 cm2, overhang 6.1 cm2, contact 309.9 cm2, h 136 mm |
| support | OK | supports off, brim off |
| slice | OK | 6h44m, 209.8 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `bug-crank-eater.stl`
- **step**: `bug-crank-eater.step`
- **print**: `bug-crank-eater.3mf`
- **preview**: `preview.png`
