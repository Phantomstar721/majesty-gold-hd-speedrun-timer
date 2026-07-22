# Research Log

## Initial Findings

- Majesty imports `QueryPerformanceFrequency` at `0x7351BC`.
- Majesty imports `QueryPerformanceCounter` at `0x7351C0`.
- The current speed value used by quest setup is available at `0x7B5304`.
- The speed table contains `10, 20, 30, 40, 50, 85, 120, 175, 250`.
- Default speed is `50`.
- Existing Remember Game Speed work provides reliable quest setup references.
- GPL registers `DeclareVictory` to `0x42F250`.
- GPL registers `DeclareLoss` to `0x42F3D0`.

## Important Constraint

Do not use Majesty's internal simulation timer as the authoritative clock. It is
tick based. The speedrun timer should use a high-resolution real clock and only
use Majesty's speed value as a multiplier.

## Next Investigation

1. Find the least invasive once-per-frame or frequent UI update hook.
2. Confirm which quest setup hook fires closest to actual playable quest start.
3. Confirm `DeclareVictory` and `DeclareLoss` catch every result path used by
   normal quests.
4. Identify a text rendering or result-panel update path for display.
