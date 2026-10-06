# tv-cable-raceway — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 75.36 cm3, bbox 207.9x293.2x18.8 mm, 4 body, 2248 tris — 4 separate bodies (intended?) |
| walls | WARN | thinnest ~1.70 mm (p2), median 2.59 mm; 11.8% of surface < 1.2 mm near [-22.4, 44.8, 6.9] |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.0 cm2, overhang 17.6 cm2, contact 213.4 cm2, h 19 mm |
| support | OK | supports off, brim off |
| slice | OK | 2h04m, 68.1 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `tv-cable-raceway.stl`
- **step**: `tv-cable-raceway.step`
- **print**: `tv-cable-raceway.3mf`
- **preview**: `preview.png`
