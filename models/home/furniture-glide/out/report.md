# furniture-glide — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 5.45 cm3, bbox 35x35x16 mm, 1 body, 4868 tris |
| walls | OK | thinnest ~2.00 mm (p2), median 3.13 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | as modeled: support 6.3 cm2, overhang 6.3 cm2, contact 2.8 cm2, h 16 mm [next: +X down 98.0; +Y down 98.0] |
| support | WARN | supports off, brim on; 6.3 cm2 needs support but supports=off |
| slice | OK | 35m, 14.1 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `furniture-glide.stl`
- **step**: `furniture-glide.step`
- **print**: `furniture-glide.3mf`
- **preview**: `preview.png`
