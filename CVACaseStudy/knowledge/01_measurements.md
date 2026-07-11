# CVACaseStudy process variables

Source: Table 1 and facility description in Ruiz-Carcel et al. (2015).

All variables are sampled at 1 Hz. Variables 1-23 are used for Fault Cases 1-5. Variable 24 is added for Fault Case 6.

| Variable | Tag | Description | Unit | Diagnostic notes |
| --- | --- | --- | --- | --- |
| x1 | PT312 | Air delivery pressure | MPa | Air supply pressure before mixing point. Relevant for air-line restrictions and upstream supply changes. |
| x2 | PT401 | Pressure at bottom of riser | MPa | Key riser pressure. Important for slugging, bypass/leakage, and top separator blockage residual effects. |
| x3 | PT408 | Pressure at top of riser | MPa | Top riser pressure. Used in pressure-drop relationships around riser and VC404. |
| x4 | PT403 | Pressure in top separator | MPa | Top separator pressure. Combines with PT408 to indicate pressure drop over VC404. |
| x5 | PT501 | Pressure in three-phase separator | MPa | Separator pressure; the benchmark keeps the three-phase separator around 0.1 MPa. |
| x6 | PT408 derived | Differential pressure PT401-PT408 | MPa | Pressure drop between bottom and top of riser. Important for slugging and flow restriction diagnosis. |
| x7 | PT403 derived | Differential pressure over VC404, PT408-PT403 | MPa | Strong diagnostic variable for Fault Case 3 top separator input blockage. |
| x8 | FT305 | Air input flow rate | Sm3/s | Air feed flow. Reduced setpoints can intentionally create slugging in Fault Case 5. |
| x9 | FT104 | Water input flow rate | kg/s | Water feed flow. Reduced setpoints can intentionally create slugging in Fault Case 5. |
| x10 | FT407 | Flow rate at top of riser | kg/s | Important for slugging diagnosis and changes in riser transport. |
| x11 | LI405 | Top separator level | m | Level in the top separator. Can respond to restrictions and separator disturbances. |
| x12 | FT406 | Top separator output flow rate | kg/s | Downstream separator output flow. |
| x13 | FT407 | Density at top of riser | kg/m3 | Key slugging variable in data set 5.2 contribution plots. |
| x14 | FT406 | Density at top separator output | kg/m3 | Downstream density response. |
| x15 | FT104 | Density of water input | kg/m3 | Input water density. |
| x16 | FT407 | Temperature at top of riser | deg C | Riser temperature. |
| x17 | FT406 | Temperature at top separator output | deg C | Separator outlet temperature. |
| x18 | FT104 | Temperature of water input | deg C | Input water temperature. |
| x19 | LI504 | Gas-liquid level in three-phase separator | % | Significant secondary contributor in Fault Case 3 top separator input blockage. |
| x20 | VC501 | Position of valve VC501 | % | Three-phase separator pressure-control valve position. |
| x21 | VC302 | Position of valve VC302 | % | Air flow-control valve position. |
| x22 | VC101 | Position of valve VC101 | % | Water flow-control valve position. |
| x23 | PO1 | Water pump current | A | Water pump operating signal. |
| x24 | PT417 | Pressure in mixture zone of 2 inch line | MPa | Only included for Fault Case 6. Main direct evidence for pressurization of isolated 2 inch line. |

## Measurement relationships

- PT401 and PT408 describe bottom-to-top riser pressure behavior.
- PT408 and PT403 describe pressure drop across the top separator input valve VC404.
- FT407 provides top riser flow rate, density and temperature; its flow and density channels are important for slugging.
- LI504 and PT501 describe three-phase separator behavior.
- VC302 and VC101 are manipulated air and water flow-control valves; air and water setpoints vary during normal and faulty tests.
