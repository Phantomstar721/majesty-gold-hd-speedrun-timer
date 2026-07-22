# Speedrun Timer Design Notes

## Requirements

- Start automatically after pressing Start Quest and loading into a quest.
- Stop automatically on any quest completion condition.
- Do not display on menus.
- Display during active quest play and on the result screen.
- Adjust timing by current game-speed slider value.
- Preserve millisecond accuracy in the tracked value.

The display does not need to repaint every millisecond. It can update at the
normal UI or frame cadence as long as the accumulator is updated from a high
resolution wall clock.

## Timing Algorithm

Use `QueryPerformanceCounter` and `QueryPerformanceFrequency`.

State:

```text
running: byte
show_result: byte
last_counter: qword
adjusted_counter: qword
frequency: qword
```

On start:

```text
frequency = QueryPerformanceFrequency()
last_counter = QueryPerformanceCounter()
adjusted_counter = 0
running = 1
show_result = 0
```

On update:

```text
now = QueryPerformanceCounter()
delta = now - last_counter
last_counter = now
speed = *(int*)0x7B5304
adjusted_counter += delta * speed / 50
```

On stop:

```text
run one final update
running = 0
show_result = 1
```

To format milliseconds:

```text
milliseconds = adjusted_counter * 1000 / frequency
```

## Known Speed Values

The speed slider table near `0x7B5304` contains:

```text
10, 20, 30, 40, 50, 85, 120, 175, 250
```

Default is `50`.

## Hook Candidates

### Start

Reuse the places already identified by Remember Game Speed:

```text
0x4D90F9  writes restored/default speed during quest setup
0x4D9B4A  alternate quest-speed setup path
0x484DD2  game-speed object initialization
0x429006  new-quest speed object initialization
0x429019  alternate new-quest speed object initialization
```

The first prototype should prefer the latest hook that fires once when the quest
is actually live. Starting too early is less bad than stopping too late, but it
would include loading time, so this needs video testing.

### Stop

GPL functions are registered here:

```text
0x434F97 -> 0x42F250  DeclareVictory
0x434FDB -> 0x42F3D0  DeclareLoss
```

These are the preferred stop hooks because normal quests end through victory/loss
script calls. The stop hook should be idempotent.

### Display

Display is intentionally unresolved. The timer can be tracked accurately before
the draw hook is final.

Options to investigate:

- in-game text renderer calls around frequent `sprintf` and text draw paths,
- GDI `TextOutA`/DirectDraw use, if Majesty still composites UI through GDI paths,
- result-screen panel/controller population around quest result strings,
- an external transparent overlay as a fallback if internal rendering is too
  invasive.

## Patch Section

Use a new PE section name, likely `.msrt`, so the patch can coexist with:

```text
.mpst  Remember Active Mods
.mskp  Remember Game Speed
.mczp  Remember Camera Zoom
```
