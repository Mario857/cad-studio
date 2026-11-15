# calibration-coupon — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 7.68 cm3, bbox 72x64.5x5.2 mm, 1 body, 20958 tris |
| walls | WARN | thinnest ~0.80 mm (p2), median 1.2 mm; 79.6% of surface < 1.2 mm near [23.2, 0.4, 0.0] |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 3.0 cm2, overhang 3.6 cm2, contact 43.2 cm2, h 5 mm |
| support | WARN | supports off, brim off; 3.0 cm2 needs support but supports=off |
| slice | OK | 16m, 9.0 g (0.24mm Standard @BBL H2C + Bambu PLA Basic @BBL H2C) |

## Files

- **stl**: `calibration-coupon.stl`
- **step**: `calibration-coupon.step`
- **print**: `calibration-coupon.3mf`
- **preview**: `preview.png`
