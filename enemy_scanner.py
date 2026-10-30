from romhandler import RomHandlerParent

if __name__ == '__main__':
    rom = RomHandlerParent('Super Junkoid DX 2.3.sfc')
    enemies = []
    palette_pointers = set()
    gfx_pointers = set()
    vulns_pointers = set()
    name_pointers = set()
    data_ranges = []
    for addr in range(0xA08000, 0xA0FFC0):
        size = rom.read_from_snes_address(addr+0, 2) & 0x7FFF
        if size > 0x2600:
            continue
        p_palette = rom.read_from_snes_address(addr+2, 2)
        if p_palette < 0x8000 and not p_palette == 0:
            continue
        bank = rom.read_from_snes_address(addr+0xC, 1)
        if bank < 0x80:
            continue
        if rom.read_from_snes_address(addr+0x12, 2) < 0x8000:
            continue
        if rom.read_from_snes_address(addr+0x14, 2) >= 0x20:
            continue
        if rom.read_from_snes_address(addr+0x18, 2) < 0x8000:
            continue
        if rom.read_from_snes_address(addr+0x1A, 2) < 0x8000:
            continue
        '''if rom.read_from_snes_address(addr+0x1C, 2) < 0x8000:
            continue
        if rom.read_from_snes_address(addr+0x1E, 2) < 0x8000:
            continue'''
        '''if rom.read_from_snes_address(addr+0x30, 2) < 0x8000:
            continue
        if rom.read_from_snes_address(addr+0x32, 2) < 0x8000:
            continue'''
        p_gfx = rom.read_from_snes_address(addr+0x36, 3)
        if (p_gfx < 0x808000 or p_gfx & 0xFFFF < 0x8000) and not p_gfx == 0:
            continue
        if rom.read_from_snes_address(addr+0x39, 1) >= 8:
            continue
        '''if rom.read_from_snes_address(addr+0x3A, 2) < 0x8000:
            continue
        if rom.read_from_snes_address(addr+0x3C, 2) < 0x8000:
            continue'''
        enemies.append(addr)
        print(hex(addr))
        if p_palette >= 0x8000:
            palette_pointers.add(bank * 0x10000 + p_palette)
        if p_gfx >= 0x808000 and p_gfx & 0xFFFF >= 0x8000:
            gfx_pointers.add((p_gfx, size))
        p_vulns = rom.read_from_snes_address(addr+0x3C, 2)
        if p_vulns >= 0x8000:
            vulns_pointers.add(0xB48000 | p_vulns)
        p_name = rom.read_from_snes_address(addr+0x3E, 2)
        if p_name >= 0x8000:
            name_pointers.add(0xB48000 | p_name)

    for (p_gfx, size) in sorted(gfx_pointers):
        pc = rom.convert_to_pc_address(p_gfx)
        data_ranges.append((pc, pc + size))

    for p_palette in sorted(palette_pointers):
        pc = rom.convert_to_pc_address(p_palette)
        data_ranges.append((pc, pc + 0x20))

    for p_vulns in sorted(vulns_pointers):
        pc = rom.convert_to_pc_address(p_vulns)
        data_ranges.append((pc, pc + 0x16))

    for p_name in sorted(name_pointers):
        pc = rom.convert_to_pc_address(p_name)
        data_ranges.append((pc, pc + 0xA))

    prev_start = 0
    prev_end = 0
    for (start, end) in sorted(data_ranges):
        if start > prev_end:
            print()
        elif start < prev_end:
            raise AssertionError(f'Overlap detected at {rom.convert_to_snes_address(prev_start):06X},{rom.convert_to_snes_address(prev_end):06X} and {rom.convert_to_snes_address(start):06X},{rom.convert_to_snes_address(end):06X}')
            #start = prev_end
        print(f'{rom.convert_to_snes_address(start):06X},{rom.convert_to_snes_address(end):06X}')
        prev_start = start
        prev_end = end
