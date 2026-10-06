# receipt-wall-clip — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 131.9 cm3, bbox 60x114.6x100 mm, 3 body, 5070 tris — 3 separate bodies (intended?) |
| walls | OK | thinnest ~0.75 mm (p2), median 5.0 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 90, 0): support 1.6 cm2, overhang 4.0 cm2, contact 22.4 cm2, h 60 mm |
| support | WARN | supports off, brim on; 1.6 cm2 needs support but supports=off |
| slice | OK | 3h44m, 119.2 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `receipt-wall-clip.stl`
- **step**: `receipt-wall-clip.step`
- **print**: `receipt-wall-clip.3mf`
- **preview**: `preview.png`
