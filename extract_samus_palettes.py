from romhandler import RomHandlerParent
import json

if __name__ == '__main__':
    rom = RomHandlerParent('../sm.sfc')

    j = json.load(open('samus_palettes.json', 'r'))

    for p in j:
        print(f'{p['name']}: dw {','.join(f'${color:04X}' for color in rom.read_from_snes_address(int(p['addr'], 16), '2'*p['size']))}')
