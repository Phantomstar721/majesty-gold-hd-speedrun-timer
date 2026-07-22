from __future__ import annotations

import argparse
import shutil
import struct
from pathlib import Path


DEFAULT_GAME_PATH = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Majesty HD")
SECTION_NAME = ".msrt"
PATCH_RAW_SIZE = 0x2000
PATCH_VIRTUAL_SIZE = 0x2000
BACKUP_DIR = "_speedrun_timer_originals"
BACKUP_NAME = "MajestyHD.exe.before-speedrun-timer"

IMAGE_BASE = 0x400000

SPEED_GLOBAL = 0x7B5304
QUERY_PERFORMANCE_FREQUENCY_IAT = 0x7351BC
QUERY_PERFORMANCE_COUNTER_IAT = 0x7351C0
GET_TICK_COUNT_IAT = 0x735178
TIME_GET_TIME_IAT = 0x7355C8
GET_PROC_ADDRESS_IAT = 0x735190
LOAD_LIBRARY_A_IAT = 0x735194
GET_ACTIVE_WINDOW_IAT = 0x7354AC
GET_GAME_VA = 0x4D6FC0

START_HOOK_VA = 0x4D9B50
START_HOOK_OFFSET = 0xD8F50
START_ORIGINAL = bytes.fromhex("C7 44 24 34 FF FF FF FF")

VICTORY_HOOK_VA = 0x42F250
VICTORY_HOOK_OFFSET = 0x2E650
VICTORY_ORIGINAL = bytes.fromhex("83 EC 24 56 8B 74 24 2C")

LOSS_HOOK_VA = 0x42F3D0
LOSS_HOOK_OFFSET = 0x2E7D0
LOSS_ORIGINAL = bytes.fromhex("83 EC 20 56 8B 74 24 28")

QPC_ORIGINAL = bytes.fromhex("FF 15 C0 51 73 00")
QPC_CALLS = [
    (0x42666B, 0x25A6B),
    (0x426967, 0x25D67),
    (0x426A84, 0x25E84),
    (0x552C94, 0x152094),
    (0x55316F, 0x15256F),
    (0x553222, 0x152622),
    (0x5532B8, 0x1526B8),
    (0x5533C6, 0x1527C6),
    (0x553480, 0x152880),
    (0x553560, 0x152960),
    (0x55361A, 0x152A1A),
    (0x553713, 0x152B13),
    (0x553866, 0x152C66),
    (0x6D9DED, 0x2D91ED),
]

GET_TICK_COUNT_ORIGINAL = bytes.fromhex("FF 15 78 51 73 00")
GET_TICK_COUNT_CALLS = [
    (0x58C3F8, 0x18B7F8),
    (0x58C454, 0x18B854),
    (0x591C90, 0x191090),
    (0x5927E4, 0x191BE4),
    (0x6D9DE1, 0x2D91E1),
]

TIME_GET_TIME_ORIGINAL = bytes.fromhex("FF 15 C8 55 73 00")
TIME_GET_TIME_CALLS = [
    (0x426A05, 0x25E05),
    (0x428E6F, 0x2826F),
    (0x455F75, 0x55375),
    (0x45E677, 0x5DA77),
    (0x466E0C, 0x6620C),
    (0x4683F4, 0x677F4),
    (0x468518, 0x67918),
    (0x46854C, 0x6794C),
    (0x46EAE7, 0x6DEE7),
    (0x46F12F, 0x6E52F),
    (0x47F6CC, 0x7EACC),
    (0x485801, 0x84C01),
    (0x4C8EE5, 0xC82E5),
    (0x4D2D46, 0xD2146),
    (0x4D3057, 0xD2457),
    (0x4D3164, 0xD2564),
    (0x4D31E0, 0xD25E0),
    (0x4D3349, 0xD2749),
    (0x4D37C8, 0xD2BC8),
    (0x4D3863, 0xD2C63),
    (0x4D3964, 0xD2D64),
    (0x4D4685, 0xD3A85),
    (0x4E24EB, 0xE18EB),
    (0x4F53A0, 0xF47A0),
    (0x50C365, 0x10B765),
    (0x594C21, 0x194021),
    (0x597883, 0x196C83),
    (0x59CB3E, 0x19BF3E),
    (0x59CCAF, 0x19C0AF),
    (0x5BABF9, 0x1B9FF9),
    (0x6022A3, 0x2016A3),
    (0x6022D3, 0x2016D3),
    (0x602702, 0x201B02),
    (0x602762, 0x201B62),
    (0x607203, 0x206603),
    (0x607213, 0x206613),
    (0x607233, 0x206633),
    (0x6170E7, 0x2164E7),
    (0x6263B1, 0x2257B1),
    (0x6305F1, 0x22F9F1),
    (0x63062F, 0x22FA2F),
    (0x635010, 0x234410),
    (0x635050, 0x234450),
    (0x635080, 0x234480),
    (0x6350B0, 0x2344B0),
    (0x63A72A, 0x239B2A),
    (0x63BD90, 0x23B190),
    (0x63BE21, 0x23B221),
    (0x63FD82, 0x23F182),
    (0x67C5EE, 0x27B9EE),
    (0x67C635, 0x27BA35),
    (0x67C6D5, 0x27BAD5),
    (0x67D025, 0x27C425),
    (0x67D668, 0x27CA68),
    (0x686473, 0x285873),
    (0x690409, 0x28F809),
    (0x69FB70, 0x29EF70),
    (0x69FD46, 0x29F146),
    (0x6A5F2D, 0x2A532D),
    (0x6B66BD, 0x2B5ABD),
    (0x6BC3DF, 0x2BB7DF),
    (0x6BC41C, 0x2BB81C),
    (0x6C0740, 0x2BFB40),
    (0x6CE844, 0x2CDC44),
    (0x6CE959, 0x2CDD59),
    (0x6CEA25, 0x2CDE25),
    (0x6CEC6E, 0x2CE06E),
    (0x6CFA0D, 0x2CEE0D),
    (0x6CFC84, 0x2CF084),
]

MSKP_START_JUMPS = [
    (0x810429, 0x3C1C29, bytes.fromhex("E9 DE 8B C1 FF"), 0x42900C, 0x100),
    (0x810469, 0x3C1C69, bytes.fromhex("E9 B1 8B C1 FF"), 0x42901F, 0x130),
]


def u16(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def u32(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def align(value: int, alignment: int) -> int:
    return ((value + alignment - 1) // alignment) * alignment


def rel32(source_va: int, target_va: int) -> bytes:
    return b"\xE8" + struct.pack("<i", target_va - (source_va + 5))


def jmp32(source_va: int, target_va: int) -> bytes:
    return b"\xE9" + struct.pack("<i", target_va - (source_va + 5))


def section_header(name: str, virtual_size: int, rva: int, raw_size: int, raw_offset: int) -> bytes:
    out = bytearray(40)
    out[: len(name)] = name.encode("ascii")
    struct.pack_into("<IIII", out, 8, virtual_size, rva, raw_size, raw_offset)
    struct.pack_into("<I", out, 36, 0xE0000020)
    return bytes(out)


def get_pe_info(data: bytes | bytearray) -> dict:
    pe = u32(data, 0x3C)
    optional = pe + 24
    section_count = u16(data, pe + 6)
    optional_size = u16(data, pe + 20)
    section_table = optional + optional_size
    sections = []
    for index in range(section_count):
        off = section_table + index * 40
        name = bytes(data[off : off + 8]).rstrip(b"\0").decode("ascii", errors="replace")
        sections.append(
            {
                "index": index,
                "header_offset": off,
                "name": name,
                "virtual_size": u32(data, off + 8),
                "rva": u32(data, off + 12),
                "raw_size": u32(data, off + 16),
                "raw_offset": u32(data, off + 20),
            }
        )
    return {
        "section_count_offset": pe + 6,
        "section_count": section_count,
        "optional": optional,
        "section_alignment": u32(data, optional + 32),
        "file_alignment": u32(data, optional + 36),
        "size_of_image_offset": optional + 56,
        "size_of_headers": u32(data, optional + 60),
        "section_table": section_table,
        "sections": sections,
    }


def bytes_equal(data: bytes | bytearray, offset: int, expected: bytes) -> bool:
    return bytes(data[offset : offset + len(expected)]) == expected


class Code:
    def __init__(self, base_va: int, size: int) -> None:
        self.base_va = base_va
        self.data = bytearray(size)
        self.offset = 0
        self.labels: dict[str, int] = {}
        self.patches: list[tuple[int, str, int, str]] = []

    def va(self) -> int:
        return self.base_va + self.offset

    def label(self, name: str) -> None:
        self.labels[name] = self.offset

    def b(self, *values: int) -> None:
        self.data[self.offset : self.offset + len(values)] = bytes(values)
        self.offset += len(values)

    def raw(self, values: bytes) -> None:
        self.data[self.offset : self.offset + len(values)] = values
        self.offset += len(values)

    def u32(self, value: int) -> None:
        self.raw(struct.pack("<I", value))

    def iat_call(self, iat_va: int) -> None:
        self.b(0xFF, 0x15)
        self.u32(iat_va)

    def call(self, label: str) -> None:
        patch_at = self.offset
        self.b(0xE8, 0, 0, 0, 0)
        self.patches.append((patch_at + 1, label, self.base_va + patch_at + 5, "rel32"))

    def call_abs(self, target_va: int) -> None:
        self.raw(rel32(self.va(), target_va))

    def jmp(self, label: str) -> None:
        patch_at = self.offset
        self.b(0xE9, 0, 0, 0, 0)
        self.patches.append((patch_at + 1, label, self.base_va + patch_at + 5, "rel32"))

    def je32(self, label: str) -> None:
        patch_at = self.offset
        self.b(0x0F, 0x84, 0, 0, 0, 0)
        self.patches.append((patch_at + 2, label, self.base_va + patch_at + 6, "rel32"))

    def jb8(self, label: str) -> None:
        patch_at = self.offset
        self.b(0x72, 0)
        self.patches.append((patch_at + 1, label, self.base_va + patch_at + 2, "rel8"))

    def finish(self) -> bytes:
        for offset, label, next_va, kind in self.patches:
            target_va = self.base_va + self.labels[label]
            delta = target_va - next_va
            if kind == "rel32":
                struct.pack_into("<i", self.data, offset, delta)
            elif kind == "rel8":
                if not -128 <= delta <= 127:
                    raise ValueError(f"rel8 jump to {label} is out of range")
                struct.pack_into("b", self.data, offset, delta)
            else:
                raise ValueError(kind)
        return bytes(self.data)


def mov_abs_u8(code: Code, address: int, value: int) -> None:
    code.b(0xC6, 0x05)
    code.u32(address)
    code.b(value)


def mov_abs_u32(code: Code, address: int, value: int) -> None:
    code.b(0xC7, 0x05)
    code.u32(address)
    code.u32(value)


def mov_eax_abs(code: Code, address: int) -> None:
    code.b(0xA1)
    code.u32(address)


def mov_abs_eax(code: Code, address: int) -> None:
    code.b(0xA3)
    code.u32(address)


def mov_abs_edx(code: Code, address: int) -> None:
    code.b(0x89, 0x15)
    code.u32(address)


def mov_mem_al(code: Code, address: int) -> None:
    code.b(0xA2)
    code.u32(address)


def mov_mem_dl(code: Code, address: int) -> None:
    code.b(0x88, 0x15)
    code.u32(address)


def write_two_digits(code: Code, address: int) -> None:
    code.b(0x31, 0xD2)  # xor edx, edx
    code.b(0xB9)
    code.u32(10)
    code.b(0xF7, 0xF1)  # div ecx
    code.b(0x04, 0x30)  # add al, '0'
    code.b(0x80, 0xC2, 0x30)  # add dl, '0'
    mov_mem_al(code, address)
    mov_mem_dl(code, address + 1)


def build_patch(patch_va: int) -> bytes:
    c = Code(patch_va, PATCH_RAW_SIZE)

    running = patch_va + 0x1000
    show_result = patch_va + 0x1001
    last_counter = patch_va + 0x1004
    last_status = patch_va + 0x100C
    adjusted_ms = patch_va + 0x1010
    final_ms = patch_va + 0x1014
    display_ms = patch_va + 0x1018
    qpc_remainder = patch_va + 0x101C
    qpc_frequency = patch_va + 0x1020
    current_counter = patch_va + 0x1024
    set_window_text_a_ptr = patch_va + 0x102C
    temp_ms = patch_va + 0x1030
    temp_sec = patch_va + 0x1034
    qpc_delta = patch_va + 0x1038
    status_buffer = patch_va + 0x1040
    user32_name = patch_va + 0x10A0
    set_window_text_name = patch_va + 0x10AC

    c.label("tick_wrapper")
    c.iat_call(GET_TICK_COUNT_IAT)
    c.b(0x50)  # push eax
    c.b(0x60)  # pushad
    c.call("update_and_emit")
    c.b(0x61)  # popad
    c.b(0x58)  # pop eax
    c.b(0xC3)

    c.offset = 0x40
    c.label("time_wrapper")
    c.iat_call(TIME_GET_TIME_IAT)
    c.b(0x50)  # push eax
    c.b(0x60)  # pushad
    c.call("update_and_emit")
    c.b(0x61)  # popad
    c.b(0x58)  # pop eax
    c.b(0xC3)

    c.offset = 0x100
    c.label("mskp_start_one")
    c.b(0x60)
    c.call("timer_start")
    c.b(0x61)
    c.raw(jmp32(patch_va + c.offset, 0x42900C))

    c.offset = 0x130
    c.label("mskp_start_two")
    c.b(0x60)
    c.call("timer_start")
    c.b(0x61)
    c.raw(jmp32(patch_va + c.offset, 0x42901F))

    c.offset = 0x180
    c.label("victory_hook")
    c.b(0x60)
    c.call("timer_stop")
    c.b(0x61)
    c.raw(VICTORY_ORIGINAL)
    c.raw(jmp32(patch_va + c.offset, VICTORY_HOOK_VA + len(VICTORY_ORIGINAL)))

    c.offset = 0x1C0
    c.label("loss_hook")
    c.b(0x60)
    c.call("timer_stop")
    c.b(0x61)
    c.raw(LOSS_ORIGINAL)
    c.raw(jmp32(patch_va + c.offset, LOSS_HOOK_VA + len(LOSS_ORIGINAL)))

    c.offset = 0x240
    c.label("timer_start")
    mov_abs_u8(c, running, 1)
    mov_abs_u8(c, show_result, 0)
    mov_abs_u32(c, adjusted_ms, 0)
    mov_abs_u32(c, final_ms, 0)
    mov_abs_u32(c, display_ms, 0)
    mov_abs_u32(c, qpc_remainder, 0)
    c.b(0x68)
    c.u32(qpc_frequency)
    c.iat_call(QUERY_PERFORMANCE_FREQUENCY_IAT)
    c.b(0x85, 0xC0)
    c.je32("timer_start_done")
    c.b(0x68)
    c.u32(last_counter)
    c.iat_call(QUERY_PERFORMANCE_COUNTER_IAT)
    c.b(0x85, 0xC0)
    c.je32("timer_start_done")
    c.iat_call(GET_TICK_COUNT_IAT)
    mov_abs_eax(c, last_status)
    c.call("format_time")
    c.call("emit_status")
    c.label("timer_start_done")
    c.b(0xC3)

    c.offset = 0x2C0
    c.label("timer_stop")
    c.b(0x80, 0x3D)
    c.u32(running)
    c.b(0)
    c.je32("timer_stop_done")
    c.call("update_and_emit")
    mov_abs_u8(c, running, 0)
    mov_abs_u8(c, show_result, 1)
    mov_eax_abs(c, adjusted_ms)
    mov_abs_eax(c, final_ms)
    mov_abs_eax(c, display_ms)
    c.call("format_time")
    c.call("emit_status")
    c.label("timer_stop_done")
    c.b(0xC3)

    c.offset = 0x380
    c.label("update_and_emit")
    c.b(0x80, 0x3D)
    c.u32(running)
    c.b(0)
    c.je32("update_done")
    c.b(0x68)
    c.u32(current_counter)
    c.iat_call(QUERY_PERFORMANCE_COUNTER_IAT)
    c.b(0x85, 0xC0)
    c.je32("update_done")
    mov_eax_abs(c, current_counter)
    c.b(0x2B, 0x05)  # sub eax, [last_counter]
    c.u32(last_counter)
    mov_abs_eax(c, qpc_delta)
    mov_eax_abs(c, current_counter)
    mov_abs_eax(c, last_counter)
    mov_eax_abs(c, current_counter + 4)
    mov_abs_eax(c, last_counter + 4)
    mov_eax_abs(c, qpc_delta)
    c.b(0x85, 0xC0)  # test eax, eax
    c.je32("update_maybe_emit")
    c.b(0xBB)
    c.u32(50)
    c.b(0xF7, 0xE3)  # mul ebx
    c.b(0x8B, 0x0D)
    c.u32(SPEED_GLOBAL)
    c.b(0x85, 0xC9)
    c.je32("update_done")
    c.b(0xF7, 0xF1)  # div ecx
    c.b(0xB9)
    c.u32(1000)
    c.b(0xF7, 0xE1)  # mul ecx
    c.b(0x03, 0x05)  # add eax, [qpc_remainder]
    c.u32(qpc_remainder)
    c.b(0x83, 0xD2, 0x00)  # adc edx, 0
    c.b(0x8B, 0x0D)
    c.u32(qpc_frequency)
    c.b(0x85, 0xC9)
    c.je32("update_done")
    c.b(0xF7, 0xF1)  # div ecx
    mov_abs_edx(c, qpc_remainder)
    c.b(0x01, 0x05)  # add [adjusted_ms], eax
    c.u32(adjusted_ms)
    c.label("update_maybe_emit")
    mov_eax_abs(c, adjusted_ms)
    mov_abs_eax(c, display_ms)
    c.iat_call(GET_TICK_COUNT_IAT)
    c.b(0x89, 0xC6)  # mov esi, eax
    c.b(0x2B, 0x05)
    c.u32(last_status)
    c.b(0x3D)
    c.u32(1000)
    c.jb8("update_done")
    c.b(0x89, 0x35)
    c.u32(last_status)
    c.call("format_time")
    c.call("emit_status")
    c.label("update_done")
    c.b(0xC3)

    c.offset = 0x480
    c.label("emit_status")
    c.b(0x83, 0x3D)
    c.u32(set_window_text_a_ptr)
    c.b(0)
    c.je32("resolve_title_proc")
    c.jmp("have_title_proc")
    c.label("resolve_title_proc")
    c.b(0x68)
    c.u32(user32_name)
    c.iat_call(LOAD_LIBRARY_A_IAT)
    c.b(0x85, 0xC0)
    c.je32("emit_done")
    c.b(0x68)
    c.u32(set_window_text_name)
    c.b(0x50)
    c.iat_call(GET_PROC_ADDRESS_IAT)
    c.b(0x85, 0xC0)
    c.je32("emit_done")
    mov_abs_eax(c, set_window_text_a_ptr)
    c.label("have_title_proc")
    c.iat_call(GET_ACTIVE_WINDOW_IAT)
    c.b(0x85, 0xC0)
    c.je32("emit_done")
    c.b(0x68)
    c.u32(status_buffer)
    c.b(0x50)
    c.b(0xFF, 0x15)
    c.u32(set_window_text_a_ptr)
    c.label("emit_done")
    c.b(0xC3)

    c.offset = 0x600
    c.label("format_time")
    mov_eax_abs(c, display_ms)
    c.b(0x31, 0xD2)
    c.b(0xB9)
    c.u32(1000)
    c.b(0xF7, 0xF1)
    mov_abs_edx(c, temp_ms)
    c.b(0x31, 0xD2)
    c.b(0xB9)
    c.u32(60)
    c.b(0xF7, 0xF1)
    mov_abs_edx(c, temp_sec)
    c.b(0x31, 0xD2)
    c.b(0xB9)
    c.u32(100)
    c.b(0xF7, 0xF1)
    c.b(0x89, 0xD0)  # mov eax, edx
    write_two_digits(c, status_buffer + 25)
    mov_eax_abs(c, temp_sec)
    write_two_digits(c, status_buffer + 28)
    mov_eax_abs(c, temp_ms)
    c.b(0x31, 0xD2)
    c.b(0xB9)
    c.u32(100)
    c.b(0xF7, 0xF1)
    c.b(0x04, 0x30)
    mov_mem_al(c, status_buffer + 31)
    c.b(0x89, 0xD0)
    write_two_digits(c, status_buffer + 32)
    c.b(0xC3)

    c.offset = 0x1040
    c.raw(b"Majesty - Speedrun Time: 00:00.000\0")
    c.offset = 0x10A0
    c.raw(b"user32.dll\0")
    c.offset = 0x10AC
    c.raw(b"SetWindowTextA\0")

    return c.finish()


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
    existing = next((s for s in pe["sections"] if s["name"] == SECTION_NAME), None)

    if existing:
        patch_raw = existing["raw_offset"]
        patch_rva = existing["rva"]
        patch_va = IMAGE_BASE + patch_rva
        patch_header_offset = existing["header_offset"]
        patched_file_size = patch_raw + PATCH_RAW_SIZE
    else:
        last = max(pe["sections"], key=lambda s: s["raw_offset"])
        patch_raw = align(len(data), pe["file_alignment"])
        last_virtual_end = last["rva"] + max(last["virtual_size"], last["raw_size"])
        patch_rva = align(last_virtual_end, pe["section_alignment"])
        patch_va = IMAGE_BASE + patch_rva
        patch_header_offset = pe["section_table"] + pe["section_count"] * 40
        patched_file_size = patch_raw + PATCH_RAW_SIZE
        if patch_header_offset + 40 > pe["size_of_headers"]:
            raise SystemExit("No room remains in the PE header for another patch section.")
        if any(data[patch_header_offset : patch_header_offset + 40]):
            raise SystemExit(f"PE header slot at 0x{patch_header_offset:X} is not empty.")
        if patch_raw != len(data):
            raise SystemExit(
                f"MajestyHD.exe has unaligned trailing data. Expected 0x{patch_raw:X}, got 0x{len(data):X}."
            )

    patch_blob = build_patch(patch_va)
    header = section_header(SECTION_NAME, PATCH_VIRTUAL_SIZE, patch_rva, PATCH_RAW_SIZE, patch_raw)
    new_size_of_image = align(patch_rva + PATCH_VIRTUAL_SIZE, pe["section_alignment"])

    start_patch = jmp32(START_HOOK_VA, patch_va + 0x100) + b"\x90\x90\x90"
    old_victory_patch = jmp32(VICTORY_HOOK_VA, patch_va + 0x140) + b"\x90\x90\x90"
    old_loss_patch = jmp32(LOSS_HOOK_VA, patch_va + 0x180) + b"\x90\x90\x90"
    victory_patch = jmp32(VICTORY_HOOK_VA, patch_va + 0x180) + b"\x90\x90\x90"
    loss_patch = jmp32(LOSS_HOOK_VA, patch_va + 0x1C0) + b"\x90\x90\x90"
    legacy_qpc_patches = [(va, off, rel32(va, patch_va) + b"\x90") for va, off in QPC_CALLS]
    tick_patches = [(va, off, rel32(va, patch_va) + b"\x90") for va, off in GET_TICK_COUNT_CALLS]
    time_patches = [(va, off, rel32(va, patch_va + 0x40) + b"\x90") for va, off in TIME_GET_TIME_CALLS]
    mskp_patches = [
        (va, off, original, jmp32(va, patch_va + target_offset), target_offset)
        for va, off, original, _, target_offset in MSKP_START_JUMPS
    ]

    hooks = [
        ("victory hook", VICTORY_HOOK_OFFSET, VICTORY_ORIGINAL, victory_patch, [old_victory_patch]),
        ("loss hook", LOSS_HOOK_OFFSET, LOSS_ORIGINAL, loss_patch, [old_loss_patch]),
    ]
    for name, offset, original, patched, old_patches in hooks:
        if not (
            bytes_equal(data, offset, original)
            or bytes_equal(data, offset, patched)
            or any(bytes_equal(data, offset, old_patched) for old_patched in old_patches)
        ):
            raise SystemExit(f"Unexpected bytes at {name} file offset 0x{offset:X}.")
    if not (bytes_equal(data, START_HOOK_OFFSET, START_ORIGINAL) or bytes_equal(data, START_HOOK_OFFSET, start_patch)):
        raise SystemExit(f"Unexpected bytes at legacy quest-start hook file offset 0x{START_HOOK_OFFSET:X}.")
    for va, offset, patched in legacy_qpc_patches:
        if not (bytes_equal(data, offset, QPC_ORIGINAL) or bytes_equal(data, offset, patched)):
            raise SystemExit(f"Unexpected bytes at QPC call file offset 0x{offset:X} / VA 0x{va:X}.")
    for va, offset, patched in tick_patches:
        if not (bytes_equal(data, offset, GET_TICK_COUNT_ORIGINAL) or bytes_equal(data, offset, patched)):
            raise SystemExit(f"Unexpected bytes at GetTickCount call file offset 0x{offset:X} / VA 0x{va:X}.")
    for va, offset, patched in time_patches:
        if not (bytes_equal(data, offset, TIME_GET_TIME_ORIGINAL) or bytes_equal(data, offset, patched)):
            raise SystemExit(f"Unexpected bytes at timeGetTime call file offset 0x{offset:X} / VA 0x{va:X}.")
    for va, offset, original, patched, _ in mskp_patches:
        if not (bytes_equal(data, offset, original) or bytes_equal(data, offset, patched)):
            raise SystemExit(f"Unexpected bytes at Remember Game Speed bridge file offset 0x{offset:X} / VA 0x{va:X}.")

    already = (
        existing
        and bytes_equal(data, patch_header_offset, header)
        and len(data) >= patched_file_size
        and bytes_equal(data, patch_raw, patch_blob)
        and bytes_equal(data, START_HOOK_OFFSET, START_ORIGINAL)
        and all(bytes_equal(data, offset, patched) for _, offset, _, patched, _ in hooks)
        and all(bytes_equal(data, offset, QPC_ORIGINAL) for _, offset, _ in legacy_qpc_patches)
        and all(bytes_equal(data, offset, patched) for _, offset, patched in tick_patches)
        and all(bytes_equal(data, offset, patched) for _, offset, patched in time_patches)
        and all(bytes_equal(data, offset, patched) for _, offset, _, patched, _ in mskp_patches)
    )

    print("Majesty Gold HD Speedrun Timer installer")
    print(f"Game path: {game_path}")
    print(f"Patch section: {SECTION_NAME}")
    if args.dry_run:
        print("Dry run: no files will be changed.")
    print()

    if already:
        print("MajestyHD.exe: Speedrun Timer is already installed.")
        return 0

    if args.dry_run:
        if existing:
            print(f"Would update {SECTION_NAME} at file offset 0x{patch_raw:X}.")
        else:
            print(f"Would add {SECTION_NAME} header at file offset 0x{patch_header_offset:X}.")
            print(f"Would append {SECTION_NAME} data at file offset 0x{patch_raw:X}.")
        print("Would patch quest-start, victory, loss, GetTickCount, and timeGetTime update hooks.")
        return 0

    backup_dir = game_path / BACKUP_DIR
    backup_dir.mkdir(exist_ok=True)
    backup_path = backup_dir / BACKUP_NAME
    if not backup_path.exists():
        shutil.copy2(exe, backup_path)

    out = bytearray(patched_file_size)
    out[: len(data)] = data
    if not existing:
        struct.pack_into("<H", out, pe["section_count_offset"], pe["section_count"] + 1)
        struct.pack_into("<I", out, pe["size_of_image_offset"], new_size_of_image)
    out[patch_header_offset : patch_header_offset + 40] = header
    out[patch_raw : patch_raw + PATCH_RAW_SIZE] = patch_blob
    out[START_HOOK_OFFSET : START_HOOK_OFFSET + len(START_ORIGINAL)] = START_ORIGINAL
    for _, offset, _, patched, _ in hooks:
        out[offset : offset + len(patched)] = patched
    for _, offset, _ in legacy_qpc_patches:
        out[offset : offset + len(QPC_ORIGINAL)] = QPC_ORIGINAL
    for _, offset, patched in tick_patches:
        out[offset : offset + len(patched)] = patched
    for _, offset, patched in time_patches:
        out[offset : offset + len(patched)] = patched
    for _, offset, _, patched, _ in mskp_patches:
        out[offset : offset + len(patched)] = patched

    exe.write_bytes(out)
    print("Done. Start a quest and watch the title bar for 'Majesty - Speedrun Time: mm:ss.mmm'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
