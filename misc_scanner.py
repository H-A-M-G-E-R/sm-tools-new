from romhandler import RomHandlerParent

if __name__ == '__main__':
    rom = RomHandlerParent('../sm.sfc')

    for addr in range(0xAA8687, 0xAAD745):
        instruction = rom.read_from_snes_address(addr, '2232')
        if instruction[0] == 0x814B and instruction[3] == 0x7D80:
            #print(f'org ${addr:06X} : dw ${instruction[0]:04X},${instruction[1]:04X} : dl ${instruction[2]:06X} : dw ${instruction[3]:04X}')
            print(f'org ${addr:06X} : dw TorizoInst_SetEyeGFXPtr,${instruction[2] & 0xFFFF:04X}')

    for addr in range(0xAA8687, 0xAAD745):
        instruction = rom.read_from_snes_address(addr, '2232')
        if instruction[0] == 0x814B and (instruction[3] == 0x7300 or instruction[3] == 0x7400):
            print(f'org ${addr:06X} : dw ${instruction[0]:04X},${instruction[1]:04X} : dl ${instruction[2]:06X} : dw ${instruction[3]:04X}')
