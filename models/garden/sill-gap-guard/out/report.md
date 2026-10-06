# sill-gap-guard — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 52.47 cm3, bbox 20x250x14 mm, 1 body, 148 tris |
| walls | WARN | thinnest ~0.67 mm (p2), median 250.0 mm; 4.8% of surface < 1.2 mm near [-8.5, -41.7, -5.8] |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 180, 0): support 0.0 cm2, overhang 48.0 cm2, contact 50.0 cm2, h 14 mm |
| support | OK | supports off, brim off |
| slice | OK | 50m, 32.2 g (0.20mm Standard @BBL H2C + Bambu PETG HF @BBL H2C) |

## Files

- **stl**: `sill-gap-guard.stl`
- **step**: `sill-gap-guard.step`
- **print**: `sill-gap-guard.3mf`
- **preview**: `preview.png`
