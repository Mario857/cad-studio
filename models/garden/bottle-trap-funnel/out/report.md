# bottle-trap-funnel — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 38.84 cm3, bbox 100x100x68.2 mm, 1 body, 3812 tris |
| walls | OK | thinnest ~1.60 mm (p2), median 3.94 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 1.1 cm2, overhang 21.0 cm2, contact 1.5 cm2, h 68 mm |
| support | WARN | supports off, brim on; 1.1 cm2 needs support but supports=off |
| slice | OK | 1h35m, 27.9 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `bottle-trap-funnel.stl`
- **step**: `bottle-trap-funnel.step`
- **print**: `bottle-trap-funnel.3mf`
- **preview**: `preview.png`
