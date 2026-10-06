# sim-tool-card — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 9.03 cm3, bbox 85.6x54x2.2 mm, 1 body, 9488 tris |
| walls | WARN | thinnest ~0.65 mm (p2), median 2.24 mm; 8.0% of surface < 1.2 mm near [-10.0, -6.6, 0.0] |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.0 cm2, overhang 0.0 cm2, contact 42.1 cm2, h 2 mm |
| support | OK | supports off, brim off |
| slice | OK | 36m, 9.3 g (0.12mm High Quality @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `sim-tool-card.stl`
- **step**: `sim-tool-card.step`
- **print**: `sim-tool-card.3mf`
- **preview**: `preview.png`
