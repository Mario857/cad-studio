# castanets — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 59.8 cm3, bbox 130x140.5x14 mm, 4 body, 10280 tris — 4 separate bodies (intended?) |
| walls | OK | thinnest ~2.50 mm (p2), median 4.84 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.0 cm2, overhang 19.3 cm2, contact 64.5 cm2, h 14 mm |
| support | OK | supports off, brim off |
| slice | SKIP | --no-slice |

## Files

- **stl**: `castanets.stl`
- **step**: `castanets.step`
- **preview**: `preview.png`
