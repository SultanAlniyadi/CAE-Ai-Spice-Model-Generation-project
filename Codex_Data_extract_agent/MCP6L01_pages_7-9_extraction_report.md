# MCP6L01 datasheet extraction — pages 7–9

Workbook: [MCP6L01-1R-1U-2-4-1-MHz-85-uA-Op-Amps-DS20002140D_graph_data.xlsx](C:/AI_Spice_project/Codex_Data_extract_agent/MCP6L01-1R-1U-2-4-1-MHz-85-uA-Op-Amps-DS20002140D_graph_data.xlsx)

Source: [MCP6L01-1R-1U-2-4-1-MHz-85-uA-Op-Amps-DS20002140D.pdf](C:/AI_Spice_project/Codex_Data_extract_agent/MCP6L01-1R-1U-2-4-1-MHz-85-uA-Op-Amps-DS20002140D.pdf)

Extracted all 17 graphs (Figures 2-1 through 2-17), with 5,149 X positions and 12,870 numerical Y values across 48 series. Each worksheet contains only column headers and numerical data. Missing values are empty cells.

## Method, precision, and checks

- Extracted PDF vector line segments and Bezier paths, applying the active clipping rectangles and later opaque label boxes. The requested pages contain no embedded graph images.
- Calibrated axes from the drawn grid and tick labels, including log scales, signed current, and Figure 2-8's separate gain and phase axes. Boundary X ticks anchor the regular grid; other ticks check the fit. Maximum calibration mismatch is reported below in PDF points.
- Linear X axes use equal increments; logarithmic X axes use equal ratios. Minimum spacing is the larger of 0.24 PDF points (one pixel at a 300-DPI reference) and the series stroke width. Stroke widths on these graphs are approximately 0.484–0.557 PDF points, so they limit sampling.
- Per-graph Y values are rounded using stroke, calibration, and local slope uncertainty. Useful resolution is approximately one visible curve stroke, with greater uncertainty at steep transitions. Extra X digits preserve regular spacing and do not imply manufacturer accuracy.
- Figure 2-3 uses separate X/Y path pairs, retaining repeated X values at its near-vertical ends. Temperature plots are blank before the visible start near −40°C. Curves clipped at the top/bottom of a plot or ending before the axis limit remain blank beyond their visible extent.
- 438 additional candidate Y values were omitted because their individual curve colors could not be verified in the rendered graph, principally where later temperature/current curves cover them. No values were inferred to fill those gaps.
- All retained numeric points that fall inside the rendered crop were checked against the corresponding source-color stroke at 300 DPI; their separation is at most 3 pixels. Points exactly on a crop boundary were checked against the clipped vector geometry. This verifies agreement with the published curve, not accuracy against unpublished manufacturer measurements.
- Reopened the final workbook and checked all 17 sheet names/order, headers, units, numeric cell types, finite values, row counts, and blank gaps. No charts or images are in the workbook.

Time is exported in µs. Figure 2-14 voltage is exported in mV; its source tick values are in V and its visible scale is 20 mV/div. Figure 2-13 keeps the printed ratio unit mV/mA.

Unless a graph specifies otherwise, the source states TA=+25°C, VDD=5.0 V, VSS=GND, VCM=VSS, VOUT=VDD/2, VL=VDD/2, RL=10 kΩ to VL, and CL=60 pF. Figures 2-1 through 2-3 use a representative part; Figure 2-4 is labeled one wafer lot.

## Per-sheet extraction

| Page | Figure / worksheet | X scale | Y scale | Rows | Series | X interval | Grid spacing (PDF pt) | Max tick residual (PDF pt) | Blank Y cells |
|---|---|---|---|---:|---:|---|---:|---:|---:|
| 7 | 2-1 Offset vs VCM 1.8V | Linear | Linear | 336 | 4 | 0.007761194 V | 0.4840 | 0.1758 | 33 |
| 7 | 2-2 Offset vs VCM 5.5V | Linear | Linear | 295 | 4 | 0.02210884 V | 0.5550 | 0.0943 | 218 |
| 7 | 2-3 Offset vs Output | Linear | Linear | 236 | 2 | Path vertices; repeated X | Source path | 0.08 | Padding only |
| 7 | 2-4 Common-Mode Range | Linear | Linear | 336 | 2 | 0.5223881 °C | 0.4840 | 0.1374 | 40 |
| 7 | 2-5 CMRR PSRR vs Temp | Linear | Linear | 334 | 2 | 0.5255255 °C | 0.4850 | 0.1864 | 42 |
| 7 | 2-6 CMRR PSRR vs Frequency | Log | Linear | 281 | 3 | × 1.033441 | 0.5550 | 0.1188 | 47 |
| 8 | 2-7 Input Current | Linear | Log | 287 | 4 | 0.003496503 V | 0.5550 | 0.0600 | 474 |
| 8 | 2-8 Open-Loop Gain Phase | Log | Linear (two axes) | 243 | 2 | × 1.07909 | 0.5550 | 0.0856 | 0 |
| 8 | 2-9 Input Noise Density | Log | Log | 256 | 1 | × 1.055673 | 0.5570 | 0.0180 | 12 |
| 8 | 2-10 No Phase Reversal | Linear | Linear | 310 | 2 | 0.3236246 µs | 0.5550 | 0.0600 | 2 |
| 8 | 2-11 Quiescent Current | Linear | Linear | 309 | 4 | 0.01623377 V | 0.4850 | 0.2015 | 61 |
| 8 | 2-12 Short-Circuit Current | Linear | Linear | 295 | 8 | 0.01870748 V | 0.5550 | 0.0655 | 214 |
| 9 | 2-13 Output Headroom Ratio | Log | Linear | 274 | 2 | × 1.017012 | 0.5550 | 0.0841 | 0 |
| 9 | 2-14 Small-Signal Response | Linear | Linear | 320 | 1 | 0.03134796 µs | 0.5550 | 0.0840 | 1 |
| 9 | 2-15 Large-Signal Response | Linear | Linear | 296 | 1 | 0.3389831 µs | 0.5550 | 0.0764 | 0 |
| 9 | 2-16 Slew Rate | Linear | Linear | 285 | 4 | 0.6161972 °C | 0.5550 | 0.0720 | 68 |
| 9 | 2-17 Output Voltage Swing | Log | Log | 273 | 2 | × 1.025721 | 0.5550 | 0.0809 | 0 |

## Graph titles, columns, and unresolved ranges

Ranges below use the worksheet's X units. A single value identifies one missing sample; these boundaries describe the sampled grid, not an exact physical boundary.

### Page 7 — Figure 2-1: Input Offset Voltage vs. Common-Mode Input Voltage at VDD = 1.8V

Worksheet: 2-1 Offset vs VCM 1.8V. X column: Common-Mode Input Voltage (V).

Y columns:

- Input Offset Voltage - -40°C; VDD=1.8V (mV)
- Input Offset Voltage - +25°C; VDD=1.8V (mV)
- Input Offset Voltage - +85°C; VDD=1.8V (mV)
- Input Offset Voltage - +125°C; VDD=1.8V (mV)

Blank cells:

- **-40°C; VDD=1.8V**, individual series covered by another curve: -0.3223881.
- **+25°C; VDD=1.8V**, individual series covered by another curve: -0.2680597–-0.2525373, -0.2137313, -0.1749254–-0.159403, -0.120597–-0.1128358, -0.08179104–-0.01970149, 0.01134328–0.04238806, 0.06567164–0.08895522, 0.4459701–0.4614925, 2.153433–2.161194.

### Page 7 — Figure 2-2: Input Offset Voltage vs. Common-Mode Input Voltage at VDD = 5.5V

Worksheet: 2-2 Offset vs VCM 5.5V. X column: Common-Mode Input Voltage (V).

Y columns:

- Input Offset Voltage - -40°C; VDD=5.5V (mV)
- Input Offset Voltage - +25°C; VDD=5.5V (mV)
- Input Offset Voltage - +85°C; VDD=5.5V (mV)
- Input Offset Voltage - +125°C; VDD=5.5V (mV)

Blank cells:

- **-40°C; VDD=5.5V**, outside the visible curve or clipped/hidden: 6.
- **-40°C; VDD=5.5V**, individual series covered by another curve: -0.3673469–1.60034, 1.688776–1.79932, 1.954082–1.998299, 2.086735, 2.153061–2.197279, 2.285714–2.37415, 2.462585–3.059524, 3.12585–3.170068, 3.280612, 3.346939–3.369048.
- **+25°C; VDD=5.5V**, outside the visible curve or clipped/hidden: 6.
- **+25°C; VDD=5.5V**, individual series covered by another curve: 0.09693878, 2.440476–2.462585, 2.528912–2.794218, 2.860544–2.971088, 3.015306–3.236395, 3.302721, 3.391156–3.435374, 3.590136–3.634354, 4.872449–5.005102, 5.137755–5.22619, 5.292517–5.358844, 5.491497–5.602041, 5.845238–5.955782.
- **+85°C; VDD=5.5V**, outside the visible curve or clipped/hidden: 6.
- **+125°C; VDD=5.5V**, outside the visible curve or clipped/hidden: -0.5–-0.4336735, 6.

### Page 7 — Figure 2-3: Input Offset Voltage vs. Output Voltage

Worksheet: 2-3 Offset vs Output. This graph uses separate X/Y pairs to preserve its near-vertical ends and repeated X coordinates. Each pair follows the visible source path; it is not a common regular X grid.

Columns:

- Output Voltage - VDD=1.8V (V)
- Input Offset Voltage - VDD=1.8V (mV)
- Output Voltage - VDD=5.5V (V)
- Input Offset Voltage - VDD=5.5V (mV)

The VDD=1.8V curve contains 183 traced vertices and the VDD=5.5V curve contains 236. The shorter pair is padded with blank cells. All vertices are clipped to the visible plot. No continuation beyond the visible 1.8V or 5.5V curve is inferred.

### Page 7 — Figure 2-4: Input Common-Mode Range Voltage vs. Ambient Temperature

Worksheet: 2-4 Common-Mode Range. X column: Ambient Temperature (°C).

Y columns:

- Common-Mode Range - VCMRH - VDD (V)
- Common-Mode Range - VCMRL - VSS (V)

Blank cells:

- **VCMRH - VDD**, outside the visible curve or clipped/hidden: -50–-40.07463.
- **VCMRL - VSS**, outside the visible curve or clipped/hidden: -50–-40.07463.

### Page 7 — Figure 2-5: CMRR, PSRR vs. Ambient Temperature

Worksheet: 2-5 CMRR PSRR vs Temp. X column: Ambient Temperature (°C).

Y columns:

- Rejection - PSRR; VCM=VSS (dB)
- Rejection - CMRR; VCMRL to VCMRH (dB)

Blank cells:

- **PSRR; VCM=VSS**, outside the visible curve or clipped/hidden: -50–-40.01502, 125.
- **CMRR; VCMRL to VCMRH**, outside the visible curve or clipped/hidden: -50–-40.01502, 125.

### Page 7 — Figure 2-6: CMRR, PSRR vs. Frequency

Worksheet: 2-6 CMRR PSRR vs Frequency. X column: Frequency (Hz).

Y columns:

- Rejection - CMRR (dB)
- Rejection - PSRR+ (dB)
- Rejection - PSRR- (dB)

Blank cells:

- **CMRR**, outside the visible curve or clipped/hidden: 22758.46–100000.
- **PSRR-**, outside the visible curve or clipped/hidden: 2682.696.

### Page 8 — Figure 2-7: Measured Input Current vs. Input Voltage (below VSS)

Worksheet: 2-7 Input Current. X column: Input Voltage (V).

Y columns:

- Input Current Magnitude - -40°C (A)
- Input Current Magnitude - +25°C (A)
- Input Current Magnitude - +85°C (A)
- Input Current Magnitude - +125°C (A)

Blank cells:

- **-40°C**, outside the visible curve or clipped/hidden: -1–-0.8251748, -0.2237762–0.
- **+25°C**, outside the visible curve or clipped/hidden: -1–-0.7132867, -0.08741259–0.
- **+85°C**, outside the visible curve or clipped/hidden: -1–-0.6048951.
- **+125°C**, outside the visible curve or clipped/hidden: -1–-0.5314685.

### Page 8 — Figure 2-8: Open-Loop Gain, Phase vs. Frequency

Worksheet: 2-8 Open-Loop Gain Phase. X column: Frequency (Hz).

Y columns:

- Open-Loop Gain - Gain (dB)
- Open-Loop Phase - Phase (°)

Blank cells:

None.

### Page 8 — Figure 2-9: Input Noise Voltage Density vs. Frequency

Worksheet: 2-9 Input Noise Density. X column: Frequency (Hz).

Y columns:

- Input Noise Voltage Density - Noise (nV/√Hz)

Blank cells:

- **Noise**, outside the visible curve or clipped/hidden: 0.1–0.1814778.

### Page 8 — Figure 2-10: The MCP6L01/1R/1U/2/4 Show No Phase Reversal

Worksheet: 2-10 No Phase Reversal. X column: Time (µs).

Y columns:

- Voltage - VIN; G=+2 V/V (V)
- Voltage - VOUT; G=+2 V/V (V)

Blank cells:

- **VIN; G=+2 V/V**, outside the visible curve or clipped/hidden: 100.
- **VOUT; G=+2 V/V**, outside the visible curve or clipped/hidden: 100.

### Page 8 — Figure 2-11: Quiescent Current vs. Power Supply Voltage

Worksheet: 2-11 Quiescent Current. X column: Power Supply Voltage (V).

Y columns:

- Quiescent Current per Amplifier - -40°C (µA)
- Quiescent Current per Amplifier - +25°C (µA)
- Quiescent Current per Amplifier - +85°C (µA)
- Quiescent Current per Amplifier - +125°C (µA)

Blank cells:

- **-40°C**, outside the visible curve or clipped/hidden: 0.5–0.8896104, 5.5.
- **+25°C**, outside the visible curve or clipped/hidden: 0.5–0.775974, 5.5.
- **+85°C**, outside the visible curve or clipped/hidden: 0.5–0.6623377, 5.5.
- **+125°C**, outside the visible curve or clipped/hidden: 0.5–0.5324675, 5.5.

### Page 8 — Figure 2-12: Output Short-Circuit Current vs. Power Supply Voltage

Worksheet: 2-12 Short-Circuit Current. X column: Power Supply Voltage (V).

Y columns:

- Short-Circuit Current - -40°C; positive current (mA)
- Short-Circuit Current - -40°C; negative current (mA)
- Short-Circuit Current - +25°C; positive current (mA)
- Short-Circuit Current - +25°C; negative current (mA)
- Short-Circuit Current - +85°C; positive current (mA)
- Short-Circuit Current - +85°C; negative current (mA)
- Short-Circuit Current - +125°C; positive current (mA)
- Short-Circuit Current - +125°C; negative current (mA)

Blank cells:

- **-40°C; positive current**, individual series covered by another curve: 0–0.8979592, 1.159864–1.234694.
- **-40°C; negative current**, outside the visible curve or clipped/hidden: 5.163265–5.5.
- **-40°C; negative current**, individual series covered by another curve: 0–0.8979592, 1.534014–1.571429.
- **+25°C; positive current**, individual series covered by another curve: 0–0.7670068, 1.215986–1.234694.
- **+25°C; negative current**, individual series covered by another curve: 0–0.7670068, 1.571429–1.608844.

### Page 9 — Figure 2-13: Ratio of Output Voltage Headroom to Output Current vs. Output Current

Worksheet: 2-13 Output Headroom Ratio. X column: Output Current Magnitude (A).

Y columns:

- Output Headroom / Current - (VDD - VOH) / IOUT (mV/mA)
- Output Headroom / Current - (VOL - VSS) / (-IOUT) (mV/mA)

Blank cells:

None.

### Page 9 — Figure 2-14: Small Signal, Noninverting Pulse Response

Worksheet: 2-14 Small-Signal Response. X column: Time (µs).

Y columns:

- Output Voltage - G=+1 V/V (mV)

Blank cells:

- **G=+1 V/V**, outside the visible curve or clipped/hidden: 10.

### Page 9 — Figure 2-15: Large Signal, Noninverting Pulse Response

Worksheet: 2-15 Large-Signal Response. X column: Time (µs).

Y columns:

- Output Voltage - G=+1 V/V (V)

Blank cells:

None.

### Page 9 — Figure 2-16: Slew Rate vs. Ambient Temperature

Worksheet: 2-16 Slew Rate. X column: Ambient Temperature (°C).

Y columns:

- Slew Rate - VDD=5.5V; rising edge (V/µs)
- Slew Rate - VDD=5.5V; falling edge (V/µs)
- Slew Rate - VDD=1.8V; rising edge (V/µs)
- Slew Rate - VDD=1.8V; falling edge (V/µs)

Blank cells:

- **VDD=5.5V; rising edge**, outside the visible curve or clipped/hidden: -50–-40.14085.
- **VDD=5.5V; falling edge**, outside the visible curve or clipped/hidden: -50–-40.14085.
- **VDD=1.8V; rising edge**, outside the visible curve or clipped/hidden: -50–-40.14085.
- **VDD=1.8V; falling edge**, outside the visible curve or clipped/hidden: -50–-40.14085.

### Page 9 — Figure 2-17: Output Voltage Swing vs. Frequency

Worksheet: 2-17 Output Voltage Swing. X column: Frequency (Hz).

Y columns:

- Output Voltage Swing - VDD=5.5V (V p-p)
- Output Voltage Swing - VDD=1.8V (V p-p)

Blank cells:

None.

The manufacturer describes these graphs as typical performance curves from a limited sample set; they are informational and are not tested or guaranteed.
