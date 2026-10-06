# cane-connector — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 176.32 cm3, bbox 269.6x194x70.7 mm, 6 body, 24896 tris — 6 separate bodies (intended?) |
| walls | OK | thinnest ~0.58 mm (p2), median 3.85 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 1.4 cm2, overhang 68.9 cm2, contact 58.9 cm2, h 71 mm |
| support | WARN | supports off, brim off; 1.4 cm2 needs support but supports=off |
| slice | OK | 6h14m, 148.2 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `cane-connector.stl`
- **step**: `cane-connector.step`
- **print**: `cane-connector.3mf`
- **preview**: `preview.png`
