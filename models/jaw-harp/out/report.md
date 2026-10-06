# jaw-harp — PASS (1 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 4.26 cm3, bbox 86.4x30x4 mm, 1 body, 868 tris |
| walls | WARN | thinnest ~1.02 mm (p2), median 5.32 mm; 11.0% of surface < 1.2 mm near [14.5, 0.7, 0.9] |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.0 cm2, overhang 0.3 cm2, contact 10.9 cm2, h 4 mm |
| support | OK | supports off, brim off |
| slice | OK | 17m, 3.4 g (0.12mm High Quality @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `jaw-harp.stl`
- **step**: `jaw-harp.step`
- **print**: `jaw-harp.3mf`
- **preview**: `preview.png`
