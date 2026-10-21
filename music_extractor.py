from romhandler import RomHandlerParent

rom = RomHandlerParent('../sm.sfc')

p_song_table = rom.read_from_snes_address(0x808F73, 3)
print(hex(p_song_table))

ranges = []
i_song = 0
while True:
    valid = True
    try:
        curr_addr = rom.convert_to_pc_address(rom.read_from_snes_address(p_song_table+i_song, 3)) # song pointer, have to convert to pc to cross banks
    except:
        break # invalid pointer
    start_addr = curr_addr
    nspc = bytearray()
    while True:
        (size, spc_addr) = rom.read(curr_addr, '22')
        curr_addr += 4
        nspc.append(size&0xFF)
        nspc.append(size>>8)
        nspc.append(spc_addr&0xFF)
        nspc.append(spc_addr>>8)
        if size == 0:
            break
        if spc_addr+size > 0x10000: # can't overflow
            valid = False
            break
        chunk = rom.bulk_read(curr_addr, size)
        curr_addr += size
        nspc += chunk
    if not valid:
        break
    end_addr = curr_addr
    ranges.append((start_addr, end_addr, i_song))

    file = open(f'test/vanilla_music/{i_song:02X}.nspc', 'wb')
    file.write(nspc)

    i_song += 3
i_song += 3
print(hex(i_song))

ranges.sort(key=lambda r: r[0])
prev_end = 0
for (start_addr, end_addr, i_song) in ranges:
    if prev_end != 0 and start_addr != prev_end:
        print('gap')
    prev_end = end_addr
    print(f'${i_song:02X}: ${rom.convert_to_snes_address(start_addr):06X}..{rom.convert_to_snes_address(end_addr):06X}')
