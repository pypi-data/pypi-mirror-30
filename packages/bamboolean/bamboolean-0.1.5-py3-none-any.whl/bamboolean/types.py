from .exceptions import BambooleanTypeError


def typecheck(val1, val2, type):
    

def infer_type(value):
    types = {
        bool: Bool,
        int: Number,
        float: Number,
        str: String,
    }
    try:
        return types[type(value)]
    except KeyError:
        msg = "Unknown variable type. Value: {}, type: {}".format(type(value),
                                                                  value)
        raise BambooleanTypeError(msg)


class Type:
    def __init__(self, value):
        self.value = value


class Number(Type):
    pass


class Bool(Type):
    pass


class String(Type):
    pass
