# phone-card-holder — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 6.92 cm3, bbox 87.8x58x3.9 mm, 1 body, 4338 tris |
| walls | WARN | thinnest ~0.83 mm (p2), median 2.95 mm; 78.6% of surface < 1.2 mm near [-13.6, -8.3, 1.0] |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.0 cm2, overhang 0.3 cm2, contact 49.7 cm2, h 4 mm |
| support | OK | supports off, brim on |
| slice | OK | 26m, 7.6 g (0.12mm High Quality @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `phone-card-holder.stl`
- **step**: `phone-card-holder.step`
- **print**: `phone-card-holder.3mf`
- **preview**: `preview.png`
