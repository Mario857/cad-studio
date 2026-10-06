# bug-dustpan — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 53.02 cm3, bbox 192x210x12 mm, 2 body, 760 tris — 2 separate bodies (intended?) |
| walls | OK | thinnest ~2.00 mm (p2), median 7.01 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | as modeled: support 0.0 cm2, overhang 0.0 cm2, contact 209.4 cm2, h 12 mm [next: -Y down 105.6; -X down 119.9] |
| support | OK | supports off, brim off |
| slice | OK | 1h17m, 41.2 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `bug-dustpan.stl`
- **step**: `bug-dustpan.step`
- **print**: `bug-dustpan.3mf`
- **preview**: `preview.png`
