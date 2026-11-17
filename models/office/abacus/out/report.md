# abacus — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 274.42 cm3, bbox 288.2x224x12 mm, 104 body, 141368 tris |
| status | OK | draft |
| walls | OK | thinnest ~3.58 mm (p2), median 5.2 mm |
| spec | WARN | docstring lacks Risks (see CLAUDE.md waste prevention) |
| fit | OK | 104 parts print separately, closest pair 2.58 mm |
| use | SKIP | not free-standing (META standing=False) |
| orient | OK | fixed rot (0, 0, 0): support 0.0 cm2, overhang 29.8 cm2, contact 179.6 cm2, h 12 mm |
| support | OK | supports off, brim off |
| strength | SKIP | no META force/loads declared |
| slice | OK | 5h59m, 130.1 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |
| cost | WARN | cost: ~130 g, 359 min, ~EUR 3.25; first print risk: HIGH; print a small prototype coupon of the critical features first |

## Files

- **stl**: `abacus.stl`
- **step**: `abacus.step`
- **print**: `abacus.3mf`
- **preview**: `preview.png`
