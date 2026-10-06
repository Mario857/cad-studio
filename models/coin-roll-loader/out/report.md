# coin-roll-loader — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 335.51 cm3, bbox 204x204x105.2 mm, 9 body, 33682 tris — 9 separate bodies (intended?) |
| walls | OK | thinnest ~2.00 mm (p2), median 5.27 mm |
| use | OK | tips at 65.0 deg toward -Y (COM margin 89.5 mm) |
| orient | OK | fixed rot (0, 0, 0): support 1.2 cm2, overhang 3.6 cm2, contact 70.2 cm2, h 105 mm |
| support | WARN | supports off, brim off; 1.2 cm2 needs support but supports=off |
| slice | OK | 5h49m, 163.0 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `coin-roll-loader.stl`
- **step**: `coin-roll-loader.step`
- **print**: `coin-roll-loader.3mf`
