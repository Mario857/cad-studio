# emergency-info-tag — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 9.19 cm3, bbox 70x40x4.2 mm, 1 body, 16446 tris |
| walls | WARN | thinnest ~0.83 mm (p2), median 3.2 mm; 3.2% of surface < 1.2 mm near [8.6, -6.8, 3.8] |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (90, 0, 0): support 1.1 cm2, overhang 1.4 cm2, contact 2.0 cm2, h 40 mm |
| support | WARN | supports off, brim on; 1.1 cm2 needs support but supports=off; wobbly on bed (tips at 4 deg) |
| slice | OK | 46m, 6.7 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `emergency-info-tag.stl`
- **step**: `emergency-info-tag.step`
- **print**: `emergency-info-tag.3mf`
- **preview**: `preview.png`
