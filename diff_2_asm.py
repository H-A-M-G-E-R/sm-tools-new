from romhandler import RomHandlerParent
import csv

if __name__ == '__main__':
    MAX_GAP = 3
    sm = RomHandlerParent('sm.sfc')
    sj = RomHandlerParent('Super Junkoid DX 2.3.sfc')
    exclude_csv = csv.reader(open('exclude.csv'))
    exclude = [False] * 0x400000
    for exclude_range in exclude_csv:
        if len(exclude_range) == 2:
            i = sj.convert_to_pc_address(int(exclude_range[0], 16))
            while i < sj.convert_to_pc_address(int(exclude_range[1], 16)):
                exclude[i] = True
                i += 1

    diff = 0
    diff_bytes = []
    diff_addr = 0
    for bank in range(0x80, 0xE0):
        file = open(f'test/sjdx_diffs/{bank:02X}.asm', 'w')
        print(f'incsrc "raw_diffs/{bank:02X}.asm"')
        for addr in range(bank*0x10000+0x8000, bank*0x10000+0x10000):
            orig_byte = sm.read_from_snes_address(addr, 1)
            new_byte = sj.read_from_snes_address(addr, 1)
            if not exclude[sj.convert_to_pc_address(addr)] and orig_byte != new_byte:
                if diff == 0:
                    if bank == 0xBF:
                        print(hex(addr))
                    diff_addr = addr
                diff = MAX_GAP
                diff_bytes.append(new_byte)
            elif diff > 0:
                diff_bytes.append(new_byte)
                diff -= 1
            if diff == 0 and diff_bytes != []:
                file.write(f'org ${diff_addr:06X} : db {','.join(f'${b:02X}' for b in diff_bytes[:-MAX_GAP])}\n')
                diff_bytes = []
        if diff_bytes != []:
            if MAX_GAP - diff == 0:
                a = diff_bytes
            else:
                a = diff_bytes[:-(MAX_GAP - diff)]
            if bank == 0xBF:
                print(hex(len(a)))
            file.write(f'org ${diff_addr:06X} : db {','.join(f'${b:02X}' for b in a)}\n')
            diff_bytes = []
            diff = 0
