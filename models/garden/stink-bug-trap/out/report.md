# stink-bug-trap — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 165.54 cm3, bbox 252x240x65 mm, 3 body, 4906 tris — 3 separate bodies (intended?) |
| walls | OK | thinnest ~2.40 mm (p2), median 3.87 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 2.0 cm2, overhang 6.8 cm2, contact 168.4 cm2, h 65 mm |
| support | WARN | supports ON (tree), brim off for 2.0 cm2 — redesign (chamfers <=45 deg, teardrops) to avoid |
| slice | OK | 4h07m, 117.0 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `stink-bug-trap.stl`
- **step**: `stink-bug-trap.step`
- **print**: `stink-bug-trap.3mf`
- **preview**: `preview.png`
