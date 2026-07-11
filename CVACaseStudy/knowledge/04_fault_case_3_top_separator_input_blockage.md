# Fault Case 3: top separator input blockage

## Fault class

Top separator input blockage. Incipient fault.

## Physical mechanism

The fault is introduced by manipulating valve VC404 at the top separator input. VC404 is pneumatically operated and its position can be observed accurately, but the VC404 position is not included as a monitoring variable. The valve behavior is nonlinear: pressure drop changes little near fully open positions and changes much more near nearly closed positions.

## Data sets

- Set 3.1: changing operating conditions, duration 9090 s, fault from 1136 s to 8352 s.
- Set 3.2: steady-state, water 2 kg/s, air 0.0278 m3/s, duration 6272 s, fault from 333 s to 5871 s.
- Set 3.3: steady-state, water 3.5 kg/s, air 0.0208 m3/s, duration 10764 s, fault from 596 s to 9566 s.

## Diagnostic evidence from data set 3.1

In the paper example, the first detection occurs at sample 1230 for T2 and sample 1324 for Q, after four short false alarms. These points correspond to VC404 openings of about 60% and 45%. When the valve is fully reopened and the fault is removed, both indicators return below the control limits.

The T2 contribution plot at sample 1230 is dominated by the differential pressure over VC404, measured as PT408-PT403. This points directly to excessive pressure loss across the valve. LI504, the gas-liquid level in the three-phase separator, also has significant contribution. For Q, the main variables are differential pressure over VC404 and bottom riser pressure PT401.

## Expected symptoms

- x7, differential pressure over VC404, becomes a primary diagnostic variable.
- x2 PT401 and x19 LI504 may also become abnormal.
- T2 contribution evidence is highly meaningful because it localizes the excessive pressure loss at VC404.

## Retrieval cues

top separator input blockage, VC404 blockage, PT408-PT403, x7 high contribution, excessive pressure loss, LI504, PT401, top separator input valve.
