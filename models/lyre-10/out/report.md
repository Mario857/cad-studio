# lyre-10 — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 865.5 cm3, bbox 270x84x270 mm, 1 body, 7708 tris |
| walls | OK | thinnest ~3.00 mm (p2), median 23.0 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (90, 0, 0): support 1.3 cm2, overhang 3.7 cm2, contact 574.3 cm2, h 84 mm |
| support | WARN | supports off, brim on; 1.3 cm2 needs support but supports=off |
| slice | OK | 16h46m, 502.1 g (Guitar Core ABS+ 0.20mm @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `lyre-10.stl`
- **step**: `lyre-10.step`
- **print**: `lyre-10.3mf`
- **preview**: `preview.png`
