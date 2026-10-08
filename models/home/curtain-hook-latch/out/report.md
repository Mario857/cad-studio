# curtain-hook-latch — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 10.01 cm3, bbox 35.8x38x20 mm, 2 body, 4088 tris — 2 separate bodies (intended?) |
| walls | OK | thinnest ~1.30 mm (p2), median 4.0 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.8 cm2, overhang 0.9 cm2, contact 5.2 cm2, h 20 mm |
| support | WARN | supports off, brim off; 0.8 cm2 needs support but supports=off |
| slice | OK | 26m, 6.2 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `curtain-hook-latch.stl`
- **step**: `curtain-hook-latch.step`
- **print**: `curtain-hook-latch.3mf`
- **preview**: `preview.png`
