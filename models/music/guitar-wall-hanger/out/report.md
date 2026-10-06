# guitar-wall-hanger — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 196.76 cm3, bbox 80.1x91.5x130 mm, 1 body, 22084 tris |
| walls | OK | thinnest ~2.05 mm (p2), median 17.4 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 90, 0): support 11.3 cm2, overhang 13.8 cm2, contact 27.2 cm2, h 80 mm |
| support | WARN | supports ON (tree), brim off for 11.3 cm2 — redesign (chamfers <=45 deg, teardrops) to avoid |
| slice | OK | 4h07m, 108.7 g (Guitar Core ABS+ 0.20mm @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `guitar-wall-hanger.stl`
- **step**: `guitar-wall-hanger.step`
- **print**: `guitar-wall-hanger.3mf`
- **preview**: `preview.png`
