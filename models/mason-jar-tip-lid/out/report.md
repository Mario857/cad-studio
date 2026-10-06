# mason-jar-tip-lid — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | WARN | 20.87 cm3, bbox 159.6x77x14 mm, 2 body, 6406 tris — 2 separate bodies (intended?) |
| walls | OK | thinnest ~0.56 mm (p2), median 2.6 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | as modeled: support 1.3 cm2, overhang 5.9 cm2, contact 48.9 cm2, h 14 mm [next: +X down 160.6; -X down 162.0] |
| support | WARN | supports off, brim off; 1.3 cm2 needs support but supports=off |
| slice | OK | 43m, 16.9 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |

## Files

- **stl**: `mason-jar-tip-lid.stl`
- **step**: `mason-jar-tip-lid.step`
- **print**: `mason-jar-tip-lid.3mf`
- **preview**: `preview.png`
