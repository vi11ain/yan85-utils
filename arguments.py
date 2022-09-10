from abc import ABC, abstractclassmethod
from codecs import namereplace_errors


class ArgType(ABC):
    @abstractclassmethod
    def assemble(cls, line):
        pass

    @abstractclassmethod
    def disassemble(cls, line):
        pass


class NamedArgType(ArgType):
    NAME_LOOKUP = None
    CODE_LOOKUP = None

    def __init__(self, name, code):
        self.name = name
        self.code = code

    @classmethod
    def assemble(cls, name):
        if name in cls.NAME_LOOKUP:
            code = cls.NAME_LOOKUP[name]
            return cls(name, code)

    @classmethod
    def disassemble(cls, code):
        if code in cls.CODE_LOOKUP:
            name = cls.CODE_LOOKUP[code]
            return cls(name, code)

    def __str__(self):
        return self.name

    def __bytes__(self):
        return self.code.to_bytes(1, 'little')


class Val(ArgType):
    def __init__(self, val):
        self.val = val

    @classmethod
    def assemble(cls, val):
        return cls(int(val, 16))

    @classmethod
    def disassemble(cls, val):
        return cls(val)

    def __str__(self):
        return hex(self.val)

    def __bytes__(self):
        return self.val.to_bytes(1, 'little')


class Reg(NamedArgType):
    NAME_LOOKUP = {
        'a': 0x2,
        'b': 0x8,
        'c': 0x20,
        'd': 0x10,
        's': 0x4,
        'i': 0x1,
        'f': 0x40,
        'NONE': 0x0
    }
    CODE_LOOKUP = dict(zip(NAME_LOOKUP.values(), NAME_LOOKUP.keys()))


class Sys(NamedArgType):
    NAME_LOOKUP = {
        'open': 0x20,
        'read_code': 0x1,
        'read_memory': 0x10,
        'write': 0x2,
        'sleep': 0x4,
        'exit': 0x8
    }
    CODE_LOOKUP = dict(zip(NAME_LOOKUP.values(), NAME_LOOKUP.keys()))


class Con(NamedArgType):
    NAME_LOOKUP = {
        '*': 0x0,
        'E': 0x1,
        'Z': 0x2,
        'N': 0x4,
        'G': 0x8,
        'L': 0x10
    }
    CODE_LOOKUP = dict(zip(NAME_LOOKUP.values(), NAME_LOOKUP.keys()))
