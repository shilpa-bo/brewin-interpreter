from intbase import InterpreterBase


# Enumerated type for our different language data types
class Type:
    INT = "int"
    BOOL = "bool"
    STRING = "string"
    NIL = "nil"
    VOID = "void"
    STRUCT = "struct"


# Represents a value, which has a type and its value
class Value:
    def __init__(self, type, value=None, struct=None):
        self.t = type
        self.v = value
        self.s = struct

    def value(self):
        return self.v

    def type(self):
        # if struct -> type is nil
        return self.t

    def struct_name(self):
        return self.s
        

def create_value(val):
    if val == InterpreterBase.TRUE_DEF:
        return Value(Type.BOOL, True)
    elif val == InterpreterBase.FALSE_DEF:
        return Value(Type.BOOL, False)
    elif val == InterpreterBase.NIL_DEF:
        return Value(Type.NIL, None)
    elif val == InterpreterBase.STRUCT_NODE:
        return Value(Type.STRUCT, "nil")
    elif isinstance(val, str):
        return Value(Type.STRING, val)
    elif isinstance(val, int):
        return Value(Type.INT, val)
    else:
        raise ValueError("Unknown value type")


def get_printable(val):
    if val.type() == Type.INT:
        return str(val.value())
    if val.type() == Type.STRING:
        return val.value()
    if val.type() == Type.BOOL:
        if val.value() is True:
            return "true"
        return "false"
    if val.type() == Type.NIL:
        return "nil"
    if val.type() == Type.STRUCT:
        return val.value()
    return None