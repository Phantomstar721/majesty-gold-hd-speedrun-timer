from __future__ import annotations

import argparse
import struct
from pathlib import Path

from install_speedrun_timer import (
    DEFAULT_GAME_PATH,
    GET_TICK_COUNT_CALLS,
    GET_TICK_COUNT_ORIGINAL,
    IMAGE_BASE,
    LOSS_HOOK_OFFSET,
    LOSS_ORIGINAL,
    LOSS_HOOK_VA,
    MSKP_START_JUMPS,
    PATCH_RAW_SIZE,
    QPC_CALLS,
    QPC_ORIGINAL,
    SECTION_NAME,
    START_HOOK_OFFSET,
    START_HOOK_VA,
    START_ORIGINAL,
    TIME_GET_TIME_CALLS,
    TIME_GET_TIME_ORIGINAL,
    VICTORY_HOOK_OFFSET,
    VICTORY_HOOK_VA,
    VICTORY_ORIGINAL,
    align,
    bytes_equal,
    get_pe_info,
    jmp32,
    rel32,
)


def get_paths(game_path_arg: str) -> tuple[Path, Path]:
    game_path = Path(game_path_arg) if game_path_arg else DEFAULT_GAME_PATH
    exe = game_path / "MajestyHD.exe"
    if not exe.exists():
        raise SystemExit(f"Could not find MajestyHD.exe at {exe}")
    return game_path, exe


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--game-path", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    game_path, exe = get_paths(args.game_path)
    data = bytearray(exe.read_bytes())
    pe = get_pe_info(data)
    section = next((s for s in pe["sections"] if s["name"] == SECTION_NAME), None)

    print("Majesty Gold HD Speedrun Timer restore")
    print(f"Game path: {game_path}")
    if args.dry_run:
        print("Dry run: no files will be changed.")
    print()

    if not section:
        print("MajestyHD.exe: Speedrun Timer is not installed.")
        return 0

    patch_va = IMAGE_BASE + section["rva"]
    hook_sets = [
        (
            START_HOOK_OFFSET,
            START_ORIGINAL,
            [jmp32(START_HOOK_VA, patch_va + 0x100) + b"\x90\x90\x90"],
        ),
        (
            VICTORY_HOOK_OFFSET,
            VICTORY_ORIGINAL,
            [
                jmp32(VICTORY_HOOK_VA, patch_va + 0x140) + b"\x90\x90\x90",
                jmp32(VICTORY_HOOK_VA, patch_va + 0x180) + b"\x90\x90\x90",
            ],
        ),
        (
            LOSS_HOOK_OFFSET,
            LOSS_ORIGINAL,
            [
                jmp32(LOSS_HOOK_VA, patch_va + 0x180) + b"\x90\x90\x90",
                jmp32(LOSS_HOOK_VA, patch_va + 0x1C0) + b"\x90\x90\x90",
            ],
        ),
    ]
    qpc_patches = [(offset, QPC_ORIGINAL, [rel32(va, patch_va) + b"\x90"]) for va, offset in QPC_CALLS]
    tick_patches = [(offset, GET_TICK_COUNT_ORIGINAL, [rel32(va, patch_va) + b"\x90"]) for va, offset in GET_TICK_COUNT_CALLS]
    time_patches = [(offset, TIME_GET_TIME_ORIGINAL, [rel32(va, patch_va + 0x40) + b"\x90"]) for va, offset in TIME_GET_TIME_CALLS]
    mskp_patches = [
        (offset, original, [jmp32(va, patch_va + target_offset)])
        for va, offset, original, _, target_offset in MSKP_START_JUMPS
    ]
    all_checks = hook_sets + qpc_patches + tick_patches + time_patches + mskp_patches

    if not any(bytes_equal(data, offset, patched) for offset, _, patched_list in all_checks for patched in patched_list):
        print("MajestyHD.exe: no Speedrun Timer hooks are installed.")
        return 0

    if section["index"] != pe["section_count"] - 1:
        raise SystemExit(f"{SECTION_NAME} is not the last PE section. Refusing to remove it automatically.")

    for offset, original, patched_list in all_checks:
        if not (bytes_equal(data, offset, original) or any(bytes_equal(data, offset, patched) for patched in patched_list)):
            raise SystemExit(f"Unexpected bytes at hook file offset 0x{offset:X}.")

    previous = next(s for s in pe["sections"] if s["index"] == section["index"] - 1)
    restored_size = section["raw_offset"]
    restored_image_size = align(previous["rva"] + max(previous["virtual_size"], previous["raw_size"]), pe["section_alignment"])

    if args.dry_run:
        print("Would restore quest-start, victory, loss, status-pulse, and bridge hooks.")
        print(f"Would remove {SECTION_NAME} section at file offset 0x{section['raw_offset']:X}.")
        return 0

    out = bytearray(restored_size)
    out[:] = data[:restored_size]
    for offset, original, _ in all_checks:
        out[offset : offset + len(original)] = original
    struct.pack_into("<H", out, pe["section_count_offset"], pe["section_count"] - 1)
    struct.pack_into("<I", out, pe["size_of_image_offset"], restored_image_size)
    out[section["header_offset"] : section["header_offset"] + 40] = b"\0" * 40
    exe.write_bytes(out)
    print("Done. Speedrun Timer hooks are removed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
