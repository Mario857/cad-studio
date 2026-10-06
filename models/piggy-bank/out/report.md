# piggy-bank — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 141.47 cm3, bbox 144x156x94.1 mm, 2 body, 9154 tris — 2 separate bodies (intended?) |
| walls | OK | thinnest ~1.50 mm (p2), median 6.34 mm |
| use | OK | tips at 63.5 deg toward -Y incl. 600 g load (COM margin 42.3 mm) |
| orient | OK | as modeled: support 3.0 cm2, overhang 12.8 cm2, contact 68.3 cm2, h 94 mm [next: stable face 386.0; stable face 392.0] |
| support | WARN | supports off, brim off; 3.0 cm2 needs support but supports=off |
| slice | OK | 3h41m, 98.7 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `piggy-bank.stl`
- **step**: `piggy-bank.step`
- **print**: `piggy-bank.3mf`
- **preview**: `preview.png`
