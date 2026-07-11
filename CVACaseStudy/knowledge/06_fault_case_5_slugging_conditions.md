# Fault Case 5: slugging conditions

## Fault class

Slugging conditions. Intermittent operating fault.

## Physical mechanism

Slugging occurs when gas and liquid velocities are low. Liquid accumulates at the base of the riser and temporarily blocks gas flow. Pressure builds until the blockage is flushed out; remaining liquid then falls back and restarts the cycle. This creates repetitive, large-amplitude oscillations in pressure and flow.

The fault is introduced by reducing the air and water flow rates to regimes where slugging is expected. During the test, operating conditions move between normal and slugging regions.

## Data sets

- Set 5.1: changing operating conditions, duration 2541 s, slugging period 1 from 686 s to 1172 s and period 2 from 1772 s to 2253 s.
- Set 5.2: changing operating conditions, duration 10608 s, slugging period 1 from 1633 s to 2955 s, period 2 from 7031 s to 7553 s, and period 3 from 8057 s to 10608 s.

## Diagnostic evidence from data set 5.2

The paper reports visible pressure oscillations in PT401 at the bottom of the riser during slugging. T2 detects the three slugging periods at samples 1716, 7075 and 8171. Q detects at samples 1643 and 8103; the second slugging period is harder for Q because Q is already above threshold in a transition zone before slugging begins.

At the first detection point, the main T2 contribution variables are:

- density at the top of the riser, FT407 density (x13)
- differential pressure between bottom and top of riser, PT401-PT408 (x6)
- bottom riser pressure PT401 (x2)

The main Q contribution variables are:

- flow rate at the top of the riser, FT407 flow (x10)
- density at the top of the riser, FT407 density (x13)

## Expected symptoms

Slugging should be suspected when riser pressure, riser pressure drop, top riser flow, and top riser density show cyclic or oscillatory behavior, especially under low air and water flow conditions. Both T2 and Q can fluctuate due to the repetitive nature of slugging.

## Retrieval cues

slugging, oscillation, cyclic pressure, PT401 oscillates, x13 density top riser, x6 PT401-PT408, x10 FT407 flow, low air water flow, intermittent fault.
