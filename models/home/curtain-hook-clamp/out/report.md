# curtain-hook-clamp — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 10.52 cm3, bbox 12x50.8x63 mm, 4 body, 6640 tris — 4 separate bodies (intended?) |
| walls | OK | thinnest ~1.22 mm (p2), median 4.0 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 90, 0): support 0.7 cm2, overhang 1.1 cm2, contact 9.0 cm2, h 12 mm |
| support | WARN | supports off, brim off; 0.7 cm2 needs support but supports=off |
| slice | OK | 21m, 6.7 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `curtain-hook-clamp.stl`
- **step**: `curtain-hook-clamp.step`
- **print**: `curtain-hook-clamp.3mf`
- **preview**: `preview.png`
