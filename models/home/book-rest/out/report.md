# book-rest — PASS (2 warn)

| check | status | result |
|---|---|---|
| build | OK | B-rep valid |
| mesh | OK | 410.14 cm3, bbox 220x202x169.1 mm, 5 body, 2320 tris |
| status | OK | draft |
| walls | OK | thinnest ~1.60 mm (p2), median 7.94 mm |
| spec | WARN | docstring lacks Risks (see CLAUDE.md waste prevention) |
| fit | OK | 5 parts print separately, closest pair 0.60 mm |
| use | OK | tips at 45.6 deg toward -Y incl. 600 g load (COM margin 76.3 mm) |
| orient | OK | fixed rot (0, 0, 0): support 0.0 cm2, overhang 1.7 cm2, contact 365.0 cm2, h 169 mm |
| support | OK | supports off, brim off |
| strength | OK | ~0.4 MPa peak vs 25 MPa Z (across layers), safety factor ~64.2 near [-9.0, 139.6, 1.5] [rough beam estimate, solid section; no strength data for 'AzureFilm ABS PLUS @BBL H2C 0.4 nozzle', PLA values used] |
| slice | OK | 6h14m, 201.8 g (0.20mm Standard @BBL H2C + AzureFilm ABS PLUS @BBL H2C 0.4 nozzle) |
| cost | WARN | cost: ~202 g, 374 min, ~EUR 5.04; first print risk: HIGH; print a small prototype coupon of the critical features first |

## Files

- **stl**: `book-rest.stl`
- **step**: `book-rest.step`
- **print**: `book-rest.3mf`
- **preview**: `preview.png`
