# reach-tongs — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 74.17 cm3, bbox 280.7x299.6x20 mm, 1 body, 940 tris |
| walls | OK | thinnest ~2.00 mm (p2), median 2.4 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 1.8 cm2, overhang 1.8 cm2, contact 47.4 cm2, h 20 mm |
| support | WARN | supports off, brim off; 1.8 cm2 needs support but supports=off |
| slice | OK | 1h26m, 38.7 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `reach-tongs.stl`
- **step**: `reach-tongs.step`
- **print**: `reach-tongs.3mf`
- **preview**: `preview.png`
