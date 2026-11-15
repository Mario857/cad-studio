# Material choice by environment (pick before designing; user's own presets: `./cad materials`)

Rules of thumb for FDM; temperatures are approximate softening points. When in doubt choose the more heat/UV-tolerant one.

| Need | Use | Avoid / why |
|---|---|---|
| Indoor, light duty, looks | PLA / PLA-MATTE | softens ~55-60 °C: not in cars, windowsills in sun, near heaters/kettles |
| Indoor, tougher, mild heat | PETG, PLA-TOUGH | PETG strings; PLA-TOUGH still ~60 °C |
| Heat 70-90 °C, bathroom steam, near hot air (hair dryer) | ABS / ABS+ | warps on big flat bases: corner brim, round corners, enclosure closed |
| Outdoors / UV / rain | ASA (best), PETG | PLA embrittles and softens; ABS yellows and cracks in UV |
| High strength + heat | PC | needs dry filament, warps strongly |
| Flexible, grips, gaskets, snap bumpers | TPU | not for rigid precision fits; print slow, no supports inside |
| Food contact | avoid FDM for repeated use | layer lines hold bacteria; if unavoidable: smooth, PETG, single-use |
| Snap-fits / thin flexing arms | PETG, ABS, PC, PLA-TOUGH | plain PLA: brittle, cracks after few cycles |

Always state the environment and why the material was chosen in the docstring.
