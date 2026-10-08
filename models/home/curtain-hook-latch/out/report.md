# curtain-hook-latch — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 8.66 cm3, bbox 35.8x26.5x20 mm, 2 body, 3482 tris — 2 separate bodies (intended?) |
| walls | OK | thinnest ~1.12 mm (p2), median 4.18 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.8 cm2, overhang 1.5 cm2, contact 4.7 cm2, h 20 mm |
| support | WARN | supports off, brim off; 0.8 cm2 needs support but supports=off |
| slice | OK | 26m, 5.6 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `curtain-hook-latch.stl`
- **step**: `curtain-hook-latch.step`
- **print**: `curtain-hook-latch.3mf`
- **preview**: `preview.png`
