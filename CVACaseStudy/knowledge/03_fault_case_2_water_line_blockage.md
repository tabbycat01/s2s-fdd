# Fault Case 2: water line blockage

## Fault class

Water line blockage. Incipient fault.

## Physical mechanism

The water line manual valve is gradually closed before the mixing point. The fault is similar in setup to Fault Case 1, but the consequences differ because air and water have different density and viscosity.

## Data sets

- Set 2.1: changing operating conditions, duration 9192 s, fault from 2244 s to 6616 s.
- Set 2.2: steady-state, water 2 kg/s, air 0.0278 m3/s, duration 3496 s, fault from 476 s to 2656 s.
- Set 2.3: steady-state, water 3.5 kg/s, air 0.0417 m3/s, duration 3421 s, fault from 331 s to 2467 s.

## Paper observations

Fault Case 2 is especially challenging. PCA and DPCA fail to produce consistent T2 detections. PLS and DPLS can detect with high false alarm rates. CVA with KDE is described as the only method producing consistent and reliable T2 detection for this fault family, while the Q statistic of CVA with KDE is not satisfactory for this case.

## Expected symptoms

Likely symptoms include water input flow FT104 deviation, water valve VC101 compensation, water pump current PO1 changes, and downstream density/flow effects. Because the blockage is gradual, early symptoms may be weak and may require T2-space evidence rather than Q-only evidence.

## Retrieval cues

water line blockage, FT104 abnormal, VC101 compensation, PO1 current, gradual water restriction, difficult detection, Q statistic not enough.
