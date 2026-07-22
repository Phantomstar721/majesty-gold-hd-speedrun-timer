# Majesty Gold HD - Speedrun Timer

Work-in-progress research repo for a speedrun timer for the Steam version of
**Majesty Gold HD**.

The goal is an in-quest timer that:

- starts automatically when a quest loads,
- stops automatically when the quest ends,
- remains visible during the quest result screen,
- hides everywhere else,
- tracks speed-adjusted time so default-speed and max-speed runs can be compared,
- stays accurate even if the visible timer text only refreshes at the game's normal
  UI cadence.

This is not installable yet. The repo currently captures the hook map and design
notes needed for the first prototype.

## Timing Model

The timer should not use Majesty's internal simulation clock. Instead, it should
integrate real elapsed time from `QueryPerformanceCounter` against the current
game-speed value:

```text
adjusted_time += real_elapsed_time * (current_speed / 50)
```

Majesty's default game speed is `50`. At default speed, the timer runs in normal
real time. At max speed, the timer advances proportionally faster. If the player
changes the speed slider mid-quest, the next timer update uses the new speed.

## Current Hook Map

Known useful addresses in the tested Steam EXE:

```text
QueryPerformanceFrequency IAT  0x7351BC
QueryPerformanceCounter IAT    0x7351C0
Current speed global           0x7B5304
Default speed value            50

Remember Game Speed hooks:
  0x4D90F9
  0x4D9B4A
  0x484DD2
  0x429006
  0x429019

GPL DeclareVictory handler     0x42F250
GPL DeclareLoss handler        0x42F3D0
GPL registration area          0x434F6E..0x434FE1
```

The likely first prototype should:

- start/reset the timer from a quest-start or quest-object initialization hook,
- update the accumulator from a frequent in-quest update or draw hook,
- stop/freeze the timer from `DeclareVictory` and `DeclareLoss`,
- keep the frozen value available on the quest result screen.

## Open Work

The unresolved part is display. The timer core can be accurate without the display
updating every millisecond, but we still need a robust way to draw text during a
quest and on the result screen without showing it on menus.

Candidate display paths:

- hook an existing in-game text rendering path,
- add a small game UI element through an existing panel/controller,
- use a companion overlay only if an internal draw hook proves too brittle.

The preferred solution is still an EXE patch like the other Majesty Gold HD QoL
utilities, not a Steam Workshop mod.

## Notes

This repo does not contain Majesty game assets or game files.
