# curtain-hook-latch — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 8.66 cm3, bbox 34.5x36.6x20 mm, 2 body, 3482 tris |
| status | OK | draft |
| walls | OK | thinnest ~1.12 mm (p2), median 4.18 mm |
| spec | WARN | docstring lacks Assumptions + Risks (see CLAUDE.md waste prevention) |
| fit | OK | 2 parts print separately, closest pair 0.21 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.8 cm2, overhang 1.5 cm2, contact 4.7 cm2, h 20 mm |
| support | WARN | supports off, brim off; 0.8 cm2 needs support but supports=off |
| strength | SKIP | no META force/loads declared |
| slice | OK | 26m, 5.7 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |
| cost | OK | cost: ~6 g, 26 min, ~EUR 0.14; first print risk: MEDIUM |

## Files

- **stl**: `curtain-hook-latch.stl`
- **step**: `curtain-hook-latch.step`
- **print**: `curtain-hook-latch.3mf`
- **preview**: `preview.png`
