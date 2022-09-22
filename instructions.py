import re

from arguments import Val, Reg, Con, Sys


class InvalidOpcode(Exception):
    pass


class InvalidLine(Exception):
    pass


INSTRUCTION_BYTEORDER = {
    'opcode': 1,
    'arg1': 2,
    'arg2': 0
}


class Instruction:
    opcode = None
    fmt = None
    arg1_type = None
    arg2_type = None

    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2

    @classmethod
    def disassemble(cls, line: bytes):
        opcode = line[INSTRUCTION_BYTEORDER['opcode']]
        arg1 = line[INSTRUCTION_BYTEORDER['arg1']]
        arg2 = line[INSTRUCTION_BYTEORDER['arg2']]

        if opcode != cls.opcode:
            raise InvalidOpcode

        return cls(cls.arg1_type.disassemble(arg1), cls.arg2_type.disassemble(arg2))

    @classmethod
    def assemble(cls, line: str):
        line = line.strip()
        regex_fmt = re.escape(cls.fmt).replace("\\{", "{").replace("\\}", "}").replace("\\ ", " ").format(
            arg1="(?P<arg1>.*)", arg2="(?P<arg2>.*)")
        regex_line = f'{re.escape(cls.__name__)} {regex_fmt}'.replace(
            ' ', '\s')

        line_match = re.search(regex_line, line)
        if not line_match:
            raise InvalidLine(line)

        arg1 = line_match.groupdict()['arg1']
        arg2 = line_match.groupdict()['arg2']

        return cls(cls.arg1_type.assemble(arg1), cls.arg2_type.assemble(arg2))

    def __str__(self):
        """
        Disassemble to string
        """
        return f'{self.__class__.__name__} {self.fmt.format(arg1=self.arg1, arg2=self.arg2)}'

    def __bytes__(self):
        """
        Assemble to bytes
        """
        line = [0, 0, 0]

        line[INSTRUCTION_BYTEORDER['opcode']
             ] = self.opcode.to_bytes(1, 'little')
        line[INSTRUCTION_BYTEORDER['arg1']] = bytes(self.arg1)
        line[INSTRUCTION_BYTEORDER['arg2']] = bytes(self.arg2)

        return b''.join(line)


class IMM(Instruction):
    opcode = 0x4
    fmt = "{arg1} = {arg2}"
    arg1_type = Reg
    arg2_type = Val


class ADD(Instruction):
    opcode = 0x20
    fmt = "{arg1} += {arg2}"
    arg1_type = Reg
    arg2_type = Reg


class STK(Instruction):
    opcode = 0x10
    fmt = "POP {arg1}, PUSH {arg2}"
    arg1_type = Reg
    arg2_type = Reg


class STM(Instruction):
    opcode = 0x40
    fmt = "*{arg1} = {arg2}"
    arg1_type = Reg
    arg2_type = Reg


class LDM(Instruction):
    opcode = 0x8
    fmt = "{arg1} = *{arg2}"
    arg1_type = Reg
    arg2_type = Reg


class CMP(Instruction):
    opcode = 0x80
    fmt = "{arg1} {arg2}"
    arg1_type = Reg
    arg2_type = Reg


class JMP(Instruction):
    opcode = 0x1
    fmt = "{arg1} {arg2}"
    arg1_type = Con
    arg2_type = Reg


class SYS(Instruction):
    opcode = 0x2
    fmt = "{arg1} -> {arg2}"
    arg1_type = Sys
    arg2_type = Reg


INSTRUCTIONS = [IMM, ADD, STK, STM, LDM, CMP, JMP, SYS]
INSTRUCTION_NAMES = {i.__name__: i for i in INSTRUCTIONS}
INSTRUCTION_OPCODES = {i.opcode: i for i in INSTRUCTIONS}


class Inst(Instruction):
    """
    Instruction factory
    """
    @classmethod
    def assemble(cls, line):
        name = re.search('(\w+)', line).group()
        if name in INSTRUCTION_NAMES:
            return INSTRUCTION_NAMES[name].assemble(line)
        raise InvalidLine

    @classmethod
    def disassemble(cls, line: bytes):
        opcode = line[INSTRUCTION_BYTEORDER['opcode']]
        if opcode in INSTRUCTION_OPCODES:
            return INSTRUCTION_OPCODES[opcode].disassemble(line)
        raise InvalidOpcode
