from romhandler import RomHandlerParent
import json

def extract_ext_spritemaps(rom, ext_spritemap_range):
    ext_spritemaps = []

    curr_addr = ext_spritemap_range[0]
    ext_spritemap_i = 0
    while True:
        if ext_spritemap_range[1] != None and curr_addr >= ext_spritemap_range[1]:
            break

        count = rom.read_from_snes_address(curr_addr, 2)
        if curr_addr+2+count*8 > (ext_spritemap_range[0] & 0xFF0000) + 0x10000: # abort if bankcross
            break

        ext_spritemap = []
        valid = True
        for i in range(count):
            x, y, spritemap, hitbox = rom.read_from_snes_address(curr_addr+2+i*8, '2'*4)
            if spritemap < 0x8000 or hitbox < 0x8000:
                valid = False
                break

            ext_spritemap.append({
                'x': x - (0x10000 if x >= 0x8000 else 0),
                'y': y - (0x10000 if y >= 0x8000 else 0),
                'spritemap': spritemap,
                'hitbox': hitbox
            })
        if not valid:
            break

        ext_spritemaps.append({
            'addr': curr_addr,
            'ext_spritemap': ext_spritemap
        })
        curr_addr += 2+count*8
        ext_spritemap_i += 1

    return ext_spritemaps

if __name__ == '__main__':
    rom = RomHandlerParent('../sm.sfc')

    # Draygon
    '''ext_spritemaps = extract_ext_spritemaps(rom, (0xA5A2B7, 0xA5A94D))

    tail_tip_dma_idxs = [
        (0xB6C4, 0),
        (0xB6D5, 1),
        (0xB6E6, 2),
        (0xB6FC, 3),
        (0xB708, 4),
        (0xB719, 5),
        (0xB72A, 6),
        (0xB73B, 7),

        (0xB747, 0),
        (0xB758, 1),
        (0xB769, 2),
        (0xB77F, 3),
        (0xB78B, 4),
        (0xB79C, 5),
        (0xB7AD, 6),
        (0xB7BE, 7),

        (0xC33B, 0),
        (0xC34C, 1),
        (0xC35D, 2),
        (0xC373, 3),
        (0xC37F, 4),
        (0xC390, 5),
        (0xC3A1, 6),
        (0xC3B2, 7),

        (0xC3BE, 0),
        (0xC3CF, 1),
        (0xC3E0, 2),
        (0xC3F6, 3),
        (0xC402, 4),
        (0xC413, 5),
        (0xC424, 6),
        (0xC435, 7)
    ]

    for (spritemap_addr, dma_idx) in tail_tip_dma_idxs:
        for ext_spritemap in ext_spritemaps:
            for entry in ext_spritemap['ext_spritemap']:
                if entry['spritemap'] == spritemap_addr:
                    print(f'org ${ext_spritemap['addr']:06X}+1 : db ${dma_idx:02X}')'''

    # Crocomire
    '''ARM_DMA_BASE = 0x108

    remap = {
        # projectile, toungue, foot
        0xD0: 0x100,
        0xD1: 0x101,
        0xD2: 0x102,
        0xD3: 0x103,
        0xD4: 0x104,
        0xD5: 0x105,
        0xD6: 0x106,
        0xD7: 0x107,
        0xD8: 0x110,
        0xD9: 0x111,
        0xDA: 0x112,
        0xDB: 0x113,
        0xDC: 0x114,
        0xDD: 0x115,
        0xDE: 0x116,
        0xDF: 0x117,

        # arm
        0xE0: 0x1E0,
        0xE2: 0x1E2,
        0xE4: 0x1E4,
        0x100: 0x1E6,
        0x102: 0x1E8,
        0x104: 0x1EA,

        # arm dma
        0x106: ARM_DMA_BASE+0x00,
        0x108: ARM_DMA_BASE+0x02,
        0xF6: ARM_DMA_BASE+0x12,
        0xE7: ARM_DMA_BASE+0x03,

        0x109: ARM_DMA_BASE+0x00,
        0xE9: ARM_DMA_BASE+0x02,

        0xEB: ARM_DMA_BASE+0x00,
        0x10B: ARM_DMA_BASE+0x02,

        0xED: ARM_DMA_BASE+0x00,
        0xEF: ARM_DMA_BASE+0x02,
        0xFF: ARM_DMA_BASE+0x12,
        0x10D: ARM_DMA_BASE+0x03,

        # eyes
        0x1E0: 0x160,
        0x1E2: 0x162,
        0x1E4: 0x164,

        0x1E6: 0x166,
        0x1E8: 0x168,
        0x1EA: 0x16A,

        0x14D: 0x16C,
        0x15D: 0x17C,
        0x14E: 0x16D,
        0x15E: 0x17D,
        0x14F: 0x16E,
        0x15F: 0x17E,

        0x1CE: 0x16F,
        0x1DE: 0x17F,
        0x1CF: 0x180,
        0x1DF: 0x190,
        0x12F: 0x181,
        0x13F: 0x191
    }

    arm_tile_dma_idxs = [
        (0x106, 1),
        (0x109, 2),
        (0xEB, 3),
        (0xED, 4)
    ]

    arm_spritemap_dma_idxs = []
    changed_spritemaps = []

    #project = json.load(open('Crocomire.json', 'r'))
    project = json.load(open('CrocomireCorpse.json', 'r'))

    for spritemap in project['spritemaps']:
        changed = False
        for entry in spritemap['spritemap']:
            for (tile, dma) in arm_tile_dma_idxs:
                if entry['tile'] == tile:
                    arm_spritemap_dma_idxs.append((int(spritemap['name'][-4:], 16), dma))
            if entry['tile'] in remap:
                changed = True
                entry['tile'] = remap[entry['tile']]
        if changed:
            changed_spritemaps.append(spritemap['name'])

    for name in changed_spritemaps:
        print(name)

    #json.dump(project, open('CrocomireNew.json', 'w'), indent=1)
    json.dump(project, open('CrocomireCorpseNew.json', 'w'), indent=1)

    #ext_spritemaps = extract_ext_spritemaps(rom, (0xA4BFC4, 0xA4CB00))
    ext_spritemaps = extract_ext_spritemaps(rom, (0xA4E1FE, 0xA4E720))

    for ext_spritemap in ext_spritemaps:
        for entry in ext_spritemap['ext_spritemap']:
            for (spritemap_addr, dma_idx) in arm_spritemap_dma_idxs:
                if entry['spritemap'] == spritemap_addr:
                    print(f'org ${ext_spritemap['addr']:06X}+1 : db ${dma_idx:02X}')'''

    # Torizo
    '''FRONT_UPPER_ARM_DMA_BASE = 0x124
    HEAD_DMA_BASE = 0x18C
    BEAK_DMA_BASE = 0x1C0
    remap = {
        # Upper arm
        0x106: FRONT_UPPER_ARM_DMA_BASE+0x00,
        0x108: FRONT_UPPER_ARM_DMA_BASE+0x00,
        0x10A: FRONT_UPPER_ARM_DMA_BASE+0x00,
        0x10C: FRONT_UPPER_ARM_DMA_BASE+0x00,
        0x10E: FRONT_UPPER_ARM_DMA_BASE+0x00,

        0x124: FRONT_UPPER_ARM_DMA_BASE+0x02,
        0x126: FRONT_UPPER_ARM_DMA_BASE+0x02,
        0x128: FRONT_UPPER_ARM_DMA_BASE+0x02,
        0x12A: FRONT_UPPER_ARM_DMA_BASE+0x02,

        # Leg at bottom 16px row
        0x1EA: 0x10A,
        0x1EB: 0x10B,
        0x1EC: 0x10C,

        0x1FA: 0x11A,
        0x1FB: 0x11B,

        0x1FC: 0x11C,
        0x1ED: 0x10D,
        0x1EF: 0x10F,
        0x1FF: 0x11F,

        # A hand
        0x18E: 0x14C,
        0x18F: 0x15F,

        # Facing forward
        0x1E4: FRONT_UPPER_ARM_DMA_BASE+0x00,
        0x1E6: FRONT_UPPER_ARM_DMA_BASE+0x02,
        0x19F: FRONT_UPPER_ARM_DMA_BASE+0x04,
        0x15F: FRONT_UPPER_ARM_DMA_BASE+0x14,
        0x1CE: FRONT_UPPER_ARM_DMA_BASE+0x05,
        0x1DE: FRONT_UPPER_ARM_DMA_BASE+0x15,
        0x19E: FRONT_UPPER_ARM_DMA_BASE+0x06,
        0x14C: FRONT_UPPER_ARM_DMA_BASE+0x16,
        0x1CF: FRONT_UPPER_ARM_DMA_BASE+0x07,
        0x1DF: FRONT_UPPER_ARM_DMA_BASE+0x17,

        # Head
        0x1C8: HEAD_DMA_BASE+0x00,
        0x1CA: HEAD_DMA_BASE+0x02,
        0x1CB: HEAD_DMA_BASE+0x03,

        0x1C4: HEAD_DMA_BASE+0x00,
        0x1C6: HEAD_DMA_BASE+0x02,

        # Beak
        0x1E8: BEAK_DMA_BASE+0x00,

        0x1DA: BEAK_DMA_BASE+0x00,
        0x1DB: BEAK_DMA_BASE+0x01,

        0x1C0: BEAK_DMA_BASE+0x00,

        0x1C2: BEAK_DMA_BASE+0x00,

        0x1E0: BEAK_DMA_BASE+0x00,

        0x1E2: BEAK_DMA_BASE+0x00,
        0x1E3: BEAK_DMA_BASE+0x01,
        0x1F2: BEAK_DMA_BASE+0x10,
        0x1F3: BEAK_DMA_BASE+0x11,

        # Egg
        0x18C: 0x106,
        0x1CC: 0x108
    }

    tile_2_dma_idx = {
        # Upper arm
        0x106: (0, 1),
        0x108: (0, 2),
        0x10A: (0, 3),
        0x10C: (0, 4),
        0x10E: (0, 5),

        # Facing forward
        0x1E4: (2, 3),

        # Head
        0x1C8: (2, 1),
        0x1C4: (2, 2),

        # Beak
        0x1E8: (3, 1),
        0x1DA: (3, 2),
        0x1C0: (3, 3),
        0x1C2: (3, 4),
        0x1E0: (3, 5),
        0x1E2: (3, 6)
    }

    project = json.load(open('Torizo.json', 'r'))

    spritemap_addr_2_name = {}
    for spritemap in project['spritemaps']:
        spritemap_addr_2_name[int(spritemap['name'][-4:], 16)] = spritemap['name']

    dma_idx_lists = [[0, 0, 0, 0]]

    ext_spritemaps = extract_ext_spritemaps(rom, (0xAAA4E6, 0xAAB096))

    for ext_spritemap in ext_spritemaps:
        dma_idxs = [0, 0, 0, 0] # front upper arm, back upper arm, head, beak
        for entry in ext_spritemap['ext_spritemap']:
            # find spritemap
            for spritemap in project['spritemaps']:
                if spritemap['name'] == spritemap_addr_2_name[entry['spritemap']]:
                    break

            for entry in spritemap['spritemap']:
                if entry['tile'] in tile_2_dma_idx:
                    dma_type = tile_2_dma_idx[entry['tile']][0]
                    if entry['palette'] == 2: # back upper arm
                        dma_type = 1
                    dma_idxs[dma_type] = tile_2_dma_idx[entry['tile']][1]

        if dma_idxs not in dma_idx_lists:
            dma_idx_lists.append(dma_idxs)

        print(f'org ${ext_spritemap['addr']:06X}+1 : db ${dma_idx_lists.index(dma_idxs):02X}')

    for dma_idxs in dma_idx_lists:
        print(f'  db {','.join(f'${i:02X}' for i in dma_idxs)}')

    for spritemap in project['spritemaps']:
        spritemap_addr_2_name[int(spritemap['name'][-4:], 16)] = spritemap['name']
        for entry in spritemap['spritemap']:
            if entry['tile'] in remap:
                entry['tile'] = remap[entry['tile']]
                if entry['palette'] == 2: # back upper arm
                    if entry['tile'] == FRONT_UPPER_ARM_DMA_BASE+0x00 or entry['tile'] == FRONT_UPPER_ARM_DMA_BASE+0x02:
                        entry['tile'] += 4

    json.dump(project, open('TorizoNew.json', 'w'), indent=1)

    project = json.load(open('GoldenTorizoEgg.json', 'r'))

    for spritemap in project['spritemaps']:
        spritemap_addr_2_name[int(spritemap['name'][-4:], 16)] = spritemap['name']
        for entry in spritemap['spritemap']:
            if entry['tile'] in remap:
                entry['tile'] = remap[entry['tile']]
            elif entry['tile'] < 0xF0:
                entry['tile'] += 0x110

    json.dump(project, open('GoldenTorizoEggNew.json', 'w'), indent=1)'''

    '''project = json.load(open('TourianStatue.json', 'r'))

    for spritemap in project['spritemaps']:
        for entry in spritemap['spritemap']:
            if entry['tile'] < 0x100:
                entry['tile'] += 0xE0

    json.dump(project, open('TourianStatueNew.json', 'w'), indent=1)'''

    '''project = json.load(open('MotherBrainParticle.json', 'r'))

    for spritemap in project['spritemaps']:
        for entry in spritemap['spritemap']:
            if entry['tile'] < 0x100:
                entry['tile'] += 0xA0

    json.dump(project, open('MotherBrainParticleNew.json', 'w'), indent=1)'''

    project = json.load(open('CeresDoor.json', 'r'))

    for spritemap in project['spritemaps']:
        for entry in spritemap['spritemap']:
            if entry['tile'] >= 0xD0 and entry['tile'] < 0x100:
                entry['tile'] += 0x30
            elif entry['tile'] >= 0x100:
                entry['tile'] += 0xC0
            entry['palette'] = 0

    json.dump(project, open('CeresDoorNew.json', 'w'), indent=1)
