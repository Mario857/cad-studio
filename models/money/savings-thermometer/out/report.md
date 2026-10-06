# savings-thermometer — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 124.2 cm3, bbox 110x9x300 mm, 2 body, 19000 tris — 2 separate bodies (intended?) |
| walls | OK | thinnest ~0.69 mm (p2), median 5.0 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (-90, 0, 30): support 0.2 cm2, overhang 2.6 cm2, contact 206.9 cm2, h 9 mm |
| support | OK | supports off, brim on |
| slice | OK | 1h40m, 56.4 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `savings-thermometer.stl`
- **step**: `savings-thermometer.step`
- **print**: `savings-thermometer.3mf`
- **preview**: `preview.png`
