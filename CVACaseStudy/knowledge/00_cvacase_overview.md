# CVACaseStudy benchmark overview

Source: Ruiz-Carcel, Cao, Mba, Lao and Samuel, "Statistical process monitoring of a multiphase flow facility", Control Engineering Practice, 2015.

## Purpose

CVACaseStudy is a real experimental benchmark for statistical process monitoring of a Cranfield University multiphase flow facility. It was created to evaluate fault detection and diagnosis methods under changing operating conditions, using real plant data instead of only simulated benchmark processes.

## Process

The facility supplies controlled air, water and oil flows to a pressurized multiphase system. The benchmark experiments used air and water. The main flow path is the 4 inch line, which includes a long inclined pipeline, a 10.5 m riser, a top separator, and a ground-level three-phase separator. A 2 inch line is normally isolated and is used only in Fault Case 6.

Important equipment and locations:

- Air supply line before mixing point: PT312, FT305, VC302.
- Water input line: FT104, VC101, PO1.
- 4 inch riser: PT401 at bottom, PT408 at top, FT407 at top.
- Top separator: PT403, LI405, FT406, input valve VC404.
- Three-phase separator: PT501, LI504, VC501.
- Alternative bypass line: direct 4 inch bypass from mixing point to three-phase separator, bypassing riser and top separator.
- 2 inch line: PT417, used for pressurization fault.

## Data

All data were sampled at 1 Hz. Normal operation contains three training data sets: T1, T2 and T3. Air and water setpoints were deliberately varied to cover dynamic operating conditions. The paper selects T2 and T3 as the final combined training set because this combination gives the lowest false alarm behavior when monitoring the remaining normal set.

For Fault Cases 1-5, variables 1-23 are used. For Fault Case 6, variable 24, PT417 pressure in the 2 inch line, is also included.

## Monitoring setup from the paper

The paper applies Canonical Variate Analysis (CVA) with:

- past lag length p = 15
- future lag length f = 15
- retained state dimension r = 25
- confidence level alpha = 0.99
- threshold estimation by Kernel Density Estimation (KDE)
- health indicators: T2 for retained canonical variate space and Q/SPE for residual space

T2 and Q are complementary. A fault alarm is raised when either statistic exceeds its upper control limit. Q often detects faults earlier but can be oversensitive and produce more false alarms. T2 contribution plots were usually more directly connected to the seeded physical fault.

## RAG usage

Use this knowledge base to map abnormal variables and temporal symptoms to plausible CVACaseStudy fault classes. Prefer fault mechanisms and affected measurements over raw detection rates when explaining a diagnosis.
