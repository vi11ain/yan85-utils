from textwrap import wrap
import argparse

from instructions import Inst, IMM


def parse_args():
    arg_parser = argparse.ArgumentParser(
        description="Dis/assembles Yan85 yancode to Yan85 assembly")
    arg_parser.add_argument('-d', '--disasm', action='store_true')
    arg_parser.add_argument('-a', '--asm', action='store_true')
    arg_parser.add_argument('input_file', type=str)
    return arg_parser.parse_args()


def disassemble_yancode(yancode):
    disassembly = []
    address = 0
    ip_changes = []
    for line in [yancode[i:i+3] for i in range(0, len(yancode), 3)]:
        instruction = Inst.disassemble(line)

        if type(instruction) == IMM and instruction.arg1.name == 'i':
            ip_changes.append((address, instruction.arg2.val))

        bytecode = "%02X %02X %02X" % (line[0], line[1], line[2])
        disassembly.append(f"\t{hex(address)}\t\t{bytecode}\t{instruction}")
        address += 1

    for src, dst in ip_changes:
        for i, line in enumerate(disassembly):
            if i == src:
                disassembly[i] = '-<' + line
            elif i == dst:
                disassembly[i] = '->' + line
            elif (i > src and i < dst) or (i < src and i > dst):
                disassembly[i] = '| ' + line
            else:
                disassembly[i] = '  ' + line

    return '\n'.join(disassembly)


def assemble_yancode(assembly):
    yancode = b''

    for line in assembly.split('\n'):
        instruction = Inst.assemble(line)
        print(instruction)
        yancode += bytes(instruction)

    return yancode


def main():
    args = parse_args()

    with open(args.input_file, 'rb') as f:
        yancode = f.read()

    if args.disasm:
        print(disassemble_yancode(yancode))
    elif args.asm:
        with open(args.input_file + '_asm.bin', 'wb') as f:
            f.write(assemble_yancode(yancode.decode()))


if __name__ == '__main__':
    main()
