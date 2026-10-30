from romhandler import RomHandlerParent
from decompress import decompress
import sys

# python3 room_scanner.py sm.sfc >> test/rooms.txt
# python3 room_scanner.py "Super Junkoid DX 2.3.sfc" >> test/sjdx_rooms.txt

POSSIBLE_STATE_CONDITIONS = {
    0xE5E6: 0, # default
    0xE5EB: 2, # door pointer = [[X]]
    0xE5FF: 0, # main area boss is dead
    0xE612: 1, # event [[X]] is set
    0xE629: 1, # boss [[X]] is dead
    0xE640: 0, # morph ball has been collected
    0xE652: 0, # morph ball and missiles have been collected
    0xE669: 0, # power bombs have been collected
    0xE678: 0, # speed booster has been collected
    0xF300: 0,
}

def scan_room_pointers(rom):
    room_data_pointers = set()
    door_list_pointers = set()

    for addr in range(0x8F8000, 0x900000):
        (
            room_id,
            area_id,
            map_x,
            map_y,
            width,
            height,
            up_scroller,
            down_scroller,
            cre_bitset,
            p_door_list,
            first_state_condition
        ) = rom.read_from_snes_address(addr, '11111111122')
        if area_id >= 8:
            continue
        if map_x >= 64:
            continue
        if map_y >= 32:
            continue
        if width * height == 0 or width * height >= 50:
            continue
        if p_door_list < 0x8000:
            continue
        if first_state_condition not in POSSIBLE_STATE_CONDITIONS:
            continue
        room_data_pointers.add((area_id, room_id, addr & 0xFFFF))
        door_list_pointers.add(p_door_list)

    return (room_data_pointers, door_list_pointers)

def scan_state_pointers(rom, room_data_pointers, p_room_names=0):
    state_pointers = set()
    level_data_pointers = set()
    fx_pointers = set()
    enemy_population_pointers = set()
    enemy_set_pointers = set()
    scroll_pointers = set()
    main_asm_pointers = set()
    plm_population_pointers = set()
    library_background_pointers = set()
    setup_asm_pointers = set()
    ranges = []

    for (area_id, room_id, addr) in sorted(room_data_pointers):
        if p_room_names == 0:
            print(f'Room {addr:04X}: {area_id:02X} {room_id:02X}')
        else:
            name = bytearray()
            a = (p_room_names & 0xFF0000) | rom.read_from_snes_address(p_room_names + 2 * area_id, 2)
            b = (p_room_names & 0xFF0000) | rom.read_from_snes_address(a + 2 * room_id, 2)
            size = rom.read_from_snes_address(b, 1)
            b += 1
            name = rom.bulk_read_from_snes_address(b, size)
            print(f'Room {addr:04X} {name.decode()}: {area_id:02X} {room_id:02X}')

        scroll_size = rom.read_from_snes_address((0x8F0000 | addr) + 4, 1) * rom.read_from_snes_address((0x8F0000 | addr) + 5, 1)

        curr_addr = (0x8F0000 | addr) + 11
        states = []
        end = False
        while True:
            state_condition = rom.read_from_snes_address(curr_addr, 2)
            curr_addr += 2
            if state_condition == 0xE5E6:
                state_condition_params = bytearray()
                p_state = curr_addr & 0xFFFF
                end = True
            else:
                state_condition_params = rom.bulk_read_from_snes_address(curr_addr, POSSIBLE_STATE_CONDITIONS[state_condition])
                p_state = rom.read_from_snes_address(curr_addr+POSSIBLE_STATE_CONDITIONS[state_condition], 2)
                curr_addr += POSSIBLE_STATE_CONDITIONS[state_condition]+2
            states.append((state_condition, state_condition_params, p_state))
            if end:
                ranges.append((rom.convert_to_pc_address(0x8F0000 | addr), rom.convert_to_pc_address(curr_addr)))
                break

        for (state_condition, state_condition_params, p_state) in states:
            print(f'Condition {' '.join([f'{state_condition:04X}'] + [f'{b:02X}' for b in state_condition_params])}: {p_state:04X}')
            (
                p_level_data,
                tileset,
                music_data,
                music_track,
                p_fx,
                p_enemy_population,
                p_enemy_set,
                l2_scroll_y,
                l2_scroll_x,
                p_scroll,
                p_special_xray_blocks,
                main_asm,
                p_plm_population,
                p_library_background,
                p_setup_asm
            ) = rom.read_from_snes_address(0x8F0000 | p_state, '311122211222222')

            state_pointers.add(p_state)
            level_data_pointers.add(p_level_data)
            fx_pointers.add(p_fx)
            enemy_population_pointers.add(p_enemy_population)
            enemy_set_pointers.add(p_enemy_set)
            if p_scroll >= 0x8000:
                scroll_pointers.add((p_scroll, scroll_size))
            main_asm_pointers.add(main_asm)
            plm_population_pointers.add(p_plm_population)
            if p_library_background >= 0x8000:
                library_background_pointers.add(p_library_background)
            setup_asm_pointers.add(p_setup_asm)
            ranges.append((rom.convert_to_pc_address(0x8F0000 | p_state), rom.convert_to_pc_address((0x8F0000 | p_state) + 26)))
        print()

    return (
        state_pointers,
        level_data_pointers,
        fx_pointers,
        enemy_population_pointers,
        enemy_set_pointers,
        scroll_pointers,
        main_asm_pointers,
        plm_population_pointers,
        library_background_pointers,
        setup_asm_pointers,
        ranges
    )

def scan_tilesets(rom, data_buffer=0):
    tile_table_pointers = set()
    tiles_pointers = set()
    palette_pointers = set()

    p_tilest_pointers = 0x8F0000 | rom.read_from_snes_address(0x82DF03, 2)
    i_tileset = 0
    while True:
        p_tilest = 0x8F0000 | rom.read_from_snes_address(p_tilest_pointers + 2 * i_tileset, 2)
        if p_tilest < 0x8F8000:
            break
        (
            p_tile_table,
            p_tiles,
            p_palette
        ) = rom.read_from_snes_address(p_tilest, '333')
        if p_tile_table < 0x808000 or p_tile_table & 0xFFFF < 0x8000:
            break
        if p_tiles < 0x808000 or p_tiles & 0xFFFF < 0x8000:
            break
        if p_palette < 0x808000 or p_palette & 0xFFFF < 0x8000:
            break
        tile_table_pointers.add(p_tile_table)
        tiles_pointers.add(p_tiles)
        palette_pointers.add(p_palette)
        print(f'Tileset {i_tileset:02X}: tile table {p_tile_table:06X}, tiles {p_tiles:06X}, palette {p_palette:06X}')
        i_tileset += 1

    ranges = []
    for p_tile_table in sorted(tile_table_pointers):
        (tile_table, compressed_size) = decompress(rom, p_tile_table)
        p_tile_table_pc = rom.convert_to_pc_address(p_tile_table)
        ranges.append((p_tile_table_pc, p_tile_table_pc + compressed_size + data_buffer))
    for p_tiles in sorted(tiles_pointers):
        (tiles, compressed_size) = decompress(rom, p_tiles)
        p_tiles_pc = rom.convert_to_pc_address(p_tiles)
        ranges.append((p_tiles_pc, p_tiles_pc + compressed_size + data_buffer))
    for p_palette in sorted(palette_pointers):
        (palette, compressed_size) = decompress(rom, p_palette)
        p_palette_pc = rom.convert_to_pc_address(p_palette)
        ranges.append((p_palette_pc, p_palette_pc + compressed_size + data_buffer))

    return ranges

if __name__ == '__main__':
    rom = RomHandlerParent(sys.argv[1])

    P_ROOM_NAMES = 0xDFD502
    DATA_BUFFER = 200

    (room_data_pointers, door_list_pointers) = scan_room_pointers(rom)
    (
        state_pointers,
        level_data_pointers,
        fx_pointers,
        enemy_population_pointers,
        enemy_set_pointers,
        scroll_pointers,
        main_asm_pointers,
        plm_population_pointers,
        library_background_pointers,
        setup_asm_pointers,
        data_ranges
    ) = scan_state_pointers(rom, room_data_pointers, P_ROOM_NAMES)

    for p_door_list in sorted(door_list_pointers):
        curr_addr = (0x8F0000 | p_door_list)
        while True:
            valid = False
            p_door = rom.read_from_snes_address(curr_addr, 2)
            if p_door >= 0x8000:
                (
                    dest_room,
                    elevator_props,
                    direction,
                    doorcap_x,
                    doorcap_y,
                    x_screen,
                    y_screen,
                    samus_dist_from_door,
                    p_door_asm
                ) = rom.read_from_snes_address(0x830000 | p_door, '211111122')
                for (area_id, room_id, room_addr) in sorted(room_data_pointers):
                    if room_addr == dest_room:
                        pc = rom.convert_to_pc_address(0x830000 | p_door)
                        data_ranges.append((pc, pc + 0xC))
                        valid = True
                        break
            if p_door == 0xBCD2: # sjdx 2.3 only
                valid = True
            if not valid:
                # i don't know why smart adds a filler word after the door list sometimes
                data_ranges.append((rom.convert_to_pc_address(0x8F0000 | p_door_list), rom.convert_to_pc_address(curr_addr + 2)))
                break
            curr_addr += 2

    for p_level_data in sorted(level_data_pointers):
        (level_data, compressed_level_data_size) = decompress(rom, p_level_data)
        p_level_data_pc = rom.convert_to_pc_address(p_level_data)
        data_ranges.append((p_level_data_pc, p_level_data_pc + compressed_level_data_size + DATA_BUFFER))

    for p_fx in sorted(fx_pointers):
        cur_addr = 0x830000 | p_fx
        while True:
            p_door = rom.read_from_snes_address(cur_addr, 2)
            cur_addr += 0x10
            if p_door == 0:
                break
        data_ranges.append((rom.convert_to_pc_address(0x830000 | p_fx), rom.convert_to_pc_address(cur_addr)))

    for p_enemy_set in sorted(enemy_set_pointers):
        cur_addr = 0xB40000 | p_enemy_set
        while True:
            enemy_id = rom.read_from_snes_address(cur_addr, 2)
            cur_addr += 2
            if enemy_id == 0xFFFF:
                break
            else:
                cur_addr += 2
        data_ranges.append((rom.convert_to_pc_address(0xB40000 | p_enemy_set), rom.convert_to_pc_address(cur_addr)))

    for (p_scroll, scroll_size) in sorted(scroll_pointers):
        data_ranges.append((rom.convert_to_pc_address(0x8F0000 | p_scroll), rom.convert_to_pc_address((0x8F0000 | p_scroll) + scroll_size)))

    plm_scroll_pointers = set()
    for p_plm_population in sorted(plm_population_pointers):
        curr_addr = (0x8F0000 | p_plm_population)
        while True:
            plm_id = rom.read_from_snes_address(curr_addr, 2)
            if plm_id == 0:
                curr_addr += 2
                break
            else:
                if plm_id == 0xB703:
                    plm_scroll_pointers.add(rom.read_from_snes_address(curr_addr + 4, 2))
                curr_addr += 6
        data_ranges.append((rom.convert_to_pc_address(0x8F0000 | p_plm_population), rom.convert_to_pc_address(curr_addr)))

    for p_plm_scroll in plm_scroll_pointers:
        curr_addr = (0x8F0000 | p_plm_scroll)
        while True:
            screen = rom.read_from_snes_address(curr_addr, 1)
            curr_addr += 1
            if screen >= 0x80:
                break
            else:
                curr_addr += 1
        data_ranges.append((rom.convert_to_pc_address(0x8F0000 | p_plm_scroll), rom.convert_to_pc_address(curr_addr)))

    p_backgrounds = set()
    for p_library_background in sorted(library_background_pointers):
        curr_addr = (0x8F0000 | p_library_background)
        while True:
            command = rom.read_from_snes_address(curr_addr, 2)
            curr_addr += 2
            if command == 0:
                data_ranges.append((rom.convert_to_pc_address(0x8F0000 | p_library_background), rom.convert_to_pc_address(curr_addr)))
                break
            elif command == 2:
                if rom.read_from_snes_address(curr_addr, 3) >= 0x800000:
                    print(hex(rom.read_from_snes_address(curr_addr, 3)))
                curr_addr += 7
            elif command == 4:
                p_backgrounds.add(rom.read_from_snes_address(curr_addr, 3))
                curr_addr += 5
            elif command == 8:
                if rom.read_from_snes_address(curr_addr, 3) >= 0x800000:
                    print(hex(rom.read_from_snes_address(curr_addr, 3)))
                curr_addr += 7
            elif command == 0xE:
                if rom.read_from_snes_address(curr_addr, 5) >= 0x800000:
                    print(hex(rom.read_from_snes_address(curr_addr, 3)))
                curr_addr += 9

    for p_background in sorted(p_backgrounds):
        (background, compressed_size) = decompress(rom, p_background)
        p_background_pc = rom.convert_to_pc_address(p_background)
        data_ranges.append((p_background_pc, p_background_pc + compressed_size))

    data_ranges += scan_tilesets(rom, DATA_BUFFER)

    p_cre_tile_table = rom.read_from_snes_address(0x82E83D, 1) * 0x10000 + rom.read_from_snes_address(0x82E841, 2)
    (cre_tile_table, compressed_size) = decompress(rom, p_cre_tile_table)
    p_cre_tile_table_pc = rom.convert_to_pc_address(p_cre_tile_table)
    data_ranges.append((p_cre_tile_table_pc, p_cre_tile_table_pc + compressed_size + DATA_BUFFER))

    p_cre_tiles = rom.read_from_snes_address(0x82E797, 1) * 0x10000 + rom.read_from_snes_address(0x82E79B, 2)
    (cre_tiles, compressed_size) = decompress(rom, p_cre_tiles)
    pc = rom.convert_to_pc_address(p_cre_tiles)
    data_ranges.append((pc, pc + compressed_size + DATA_BUFFER))

    p_credits_tilemap = rom.read_from_snes_address(0x8BE0BF, 1) * 0x10000 + rom.read_from_snes_address(0x8BE0C3, 2)
    (credits_tilemap, compressed_size) = decompress(rom, p_credits_tilemap)
    pc = rom.convert_to_pc_address(p_credits_tilemap)
    data_ranges.append((pc, pc + compressed_size + DATA_BUFFER))

    p_credits_tiles = rom.read_from_snes_address(0x8BD5F5, 1) * 0x10000 + rom.read_from_snes_address(0x8BD5F9, 2)
    (credits_tiles, compressed_size) = decompress(rom, p_credits_tiles)
    pc = rom.convert_to_pc_address(p_credits_tiles)
    data_ranges.append((pc, pc + compressed_size + DATA_BUFFER))

    prev_start = 0
    prev_end = 0
    for (start, end) in sorted(data_ranges):
        if start > prev_end:
            print()
        elif start < prev_end:
            #raise AssertionError(f'Overlap detected at {rom.convert_to_snes_address(prev_start):06X},{rom.convert_to_snes_address(prev_end):06X} and {rom.convert_to_snes_address(start):06X},{rom.convert_to_snes_address(end):06X}')
            start = prev_end
        print(f'{rom.convert_to_snes_address(start):06X},{rom.convert_to_snes_address(end):06X}')
        prev_start = start
        prev_end = end
