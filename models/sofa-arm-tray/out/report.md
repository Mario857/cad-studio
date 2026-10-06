# sofa-arm-tray — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 734.48 cm3, bbox 112x180x129 mm, 1 body, 65966 tris |
| walls | OK | thinnest ~3.20 mm (p2), median 15.38 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 3.9 cm2, overhang 220.5 cm2, contact 11.5 cm2, h 129 mm |
| support | WARN | supports off, brim on; 3.9 cm2 needs support but supports=off |
| slice | OK | 6h28m, 218.8 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `sofa-arm-tray.stl`
- **step**: `sofa-arm-tray.step`
- **print**: `sofa-arm-tray.3mf`
- **preview**: `preview.png`
