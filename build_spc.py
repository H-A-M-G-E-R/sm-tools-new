import glob, os.path, sys

nspc_paths = glob.glob('**/*.nspc' if len(sys.argv) == 1 else sys.argv[1], recursive=True)

for nspc_path in nspc_paths:
    nspc = open(nspc_path, 'rb')
    spc = open(os.path.splitext(nspc_path)[0] + '.spc', 'wb')
    org = open('smorg.spc' if len(sys.argv) < 3 else sys.argv[2], 'rb')

    spc.write(org.read()) # Copy org to spc

    while True:
        size = int.from_bytes(nspc.read(2), 'little')
        dest = int.from_bytes(nspc.read(2), 'little')
        if size == 0:
            break

        spc.seek(dest+0x100)
        spc.write(nspc.read(size))
