# Majesty Gold HD - Speedrun Timer

Adds a speed-adjusted speedrun timer to the Steam version of **Majesty Gold HD**.

The timer appears in the Majesty window title bar while a quest is running:

```text
Majesty - Speedrun Time: 00:00.000
```

## What It Does

- Starts automatically when a quest loads.
- Resets to `00:00.000` on each new quest start.
- Stops and freezes when the quest ends through victory or loss.
- Uses `QueryPerformanceCounter` real-time measurement rather than Majesty's internal simulation tick.
- Scales elapsed time by the current game-speed slider value so runs at different game speeds can be compared.
- Updates correctly if the game-speed slider changes mid-quest.

## Install

Close Majesty Gold HD, then run:

```text
Install - Speedrun Timer.bat
```

The installer looks for Majesty at the default Steam path:

```text
C:\Program Files (x86)\Steam\steamapps\common\Majesty HD
```

If your game is installed somewhere else, run the installer script manually:

```powershell
python scripts\install_speedrun_timer.py --game-path "D:\Path\To\Majesty HD"
```

## Uninstall

Close Majesty Gold HD, then run:

```text
Uninstall - Restore Stock Timer.bat
```

For a custom game path:

```powershell
python scripts\restore_speedrun_timer.py --game-path "D:\Path\To\Majesty HD"
```

## Notes

- Requires Python 3.
- The patch modifies `MajestyHD.exe` by adding a reversible `.msrt` section.
- The installer creates a backup in `_speedrun_timer_originals` the first time it runs.
- Manual return to the main menu before victory/loss does not currently stop the timer, but the next quest starts from zero.
- This repo does not include Majesty game files or assets.
