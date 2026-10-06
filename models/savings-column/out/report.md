# savings-column — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 961.88 cm3, bbox 150x202.4x300 mm, 5 body, 203344 tris — 5 separate bodies (intended?) |
| walls | OK | thinnest ~2.09 mm (p2), median 6.89 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | as modeled: support 6.0 cm2, overhang 30.4 cm2, contact 203.0 cm2, h 300 mm [next: top down 1961.5; stable face 2265.2] |
| support | WARN | supports off, brim on; 6.0 cm2 needs support but supports=off |
| slice | OK | 13h44m, 418.6 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `savings-column.stl`
- **step**: `savings-column.step`
- **print**: `savings-column.3mf`
- **preview**: `preview.png`
