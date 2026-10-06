# bug-catcher-cup — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 98.04 cm3, bbox 211.2x103.9x90 mm, 2 body, 1282 tris — 2 separate bodies (intended?) |
| walls | OK | thinnest ~1.03 mm (p2), median 3.2 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (180, 0, 0): support 0.0 cm2, overhang 17.4 cm2, contact 116.4 cm2, h 90 mm |
| support | OK | supports off, brim off |
| slice | OK | 2h37m, 70.5 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `bug-catcher-cup.stl`
- **step**: `bug-catcher-cup.step`
- **print**: `bug-catcher-cup.3mf`
- **preview**: `preview.png`
