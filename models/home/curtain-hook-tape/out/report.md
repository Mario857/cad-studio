# curtain-hook-tape — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 19.1 cm3, bbox 31.8x21.6x83.2 mm, 2 body, 960 tris — 2 separate bodies (intended?) |
| walls | WARN | thinnest ~0.80 mm (p2), median 21.6 mm; 3.1% of surface < 1.2 mm near [0.4, -10.0, 57.1] |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (90, 0, 0): support 0.5 cm2, overhang 0.5 cm2, contact 9.3 cm2, h 22 mm |
| support | OK | supports off, brim off |
| slice | OK | 29m, 8.8 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `curtain-hook-tape.stl`
- **step**: `curtain-hook-tape.step`
- **print**: `curtain-hook-tape.3mf`
- **preview**: `preview.png`
