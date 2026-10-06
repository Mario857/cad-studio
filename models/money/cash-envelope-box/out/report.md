# cash-envelope-box — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 220.92 cm3, bbox 176.8x168.5x70.4 mm, 12 body, 21282 tris — 12 separate bodies (intended?) |
| walls | OK | thinnest ~0.79 mm (p2), median 2.0 mm |
| use | OK | tips at 68.1 deg toward -Y incl. 150 g load (COM margin 76.6 mm) |
| orient | OK | as modeled: support 1.4 cm2, overhang 3.3 cm2, contact 215.4 cm2, h 70 mm [next: stable face 291.6; +X down 1191.9] |
| support | WARN | supports off, brim on; 1.4 cm2 needs support but supports=off |
| slice | OK | 5h32m, 184.4 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `cash-envelope-box.stl`
- **step**: `cash-envelope-box.step`
- **print**: `cash-envelope-box.3mf`
- **preview**: `preview.png`
