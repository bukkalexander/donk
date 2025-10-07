"""Integer language (lang int) AST nodes and interpreter."""

import ast


# =============================================================================
#   AST Nodes
# =============================================================================
class AstNode:
    def __repr__(self):
        params = ", ".join(f"{value!r}" for _, value in vars(self).items())
        return f"{self.__class__.__name__}({params})"


class Constant(AstNode):
    def __init__(self, value):
        self.value = value


class UnaryOp(AstNode):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand


class Call(AstNode):
    def __init__(self, func, args):
        self.func = func
        self.args = args


class Name(AstNode):
    def __init__(self, id):
        self.id = id


class BinOp(AstNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class Add(AstNode, ast.Add):
    pass


class Sub(AstNode, ast.Sub):
    pass


class USub(AstNode, ast.USub):
    pass


class Expr(AstNode):
    def __init__(self, value):
        self.value = value


class Module(AstNode):
    def __init__(self, body):
        self.body = body


# =============================================================================
#   Matcher
# =============================================================================
def is_exp(e):
    match e:
        case Constant(value=n):
            return isinstance(n, int)
        case Call(func=Name(id="input_int"), args=[]):
            return True
        case UnaryOp(op=USub(), operand=e1):
            return is_exp(e1)
        case BinOp(left=e1, op=Add(), right=e2):
            return is_exp(e1) and is_exp(e2)
        case BinOp(left=e1, op=USub(), right=e2):
            return is_exp(e1) and is_exp(e2)
        case _:
            return False


def is_stmt(s):
    match s:
        case Expr(value=Call(func=Name(id="print"), args=[e])):
            return is_exp(e)
        case Expr(value=e):
            return is_exp(e)
        case _:
            return False


def is_lang_int(p):
    match p:
        case Module(body=body):
            return all([is_stmt(s) for s in body])
        case _:
            return False


# =============================================================================
#   Interpreter
# =============================================================================

################################################################################
# Auxiliary Functions
################################################################################

# signed 64-bit arithmetic

min_int64 = -(1 << 63)

max_int64 = (1 << 63) - 1

mask_64 = (1 << 64) - 1

offset_64 = 1 << 63


def to_signed(x):
    return ((x + offset_64) & mask_64) - offset_64


def add64(x, y):
    return to_signed(x + y)


def sub64(x, y):
    return to_signed(x - y)


def neg64(x):
    return to_signed(-x)


def is_int64(x) -> bool:
    return isinstance(x, int) and (x >= min_int64 and x <= max_int64)


def input_int() -> int:
    # entering illegal characters may cause exception,
    # but we won't worry about that
    x = int(input())
    # clamp to 64 bit signed number, emulating behavior of C's scanf
    x = min(max_int64, max(min_int64, x))
    return x


def interp_exp(e):
    match e:
        case BinOp(left=left, op=Add(), right=right):
            l = interp_exp(left)
            r = interp_exp(right)
            return add64(l, r)
        case BinOp(left=left, op=Sub(), right=right):
            l = interp_exp(left)
            r = interp_exp(right)
            return sub64(l, r)
        case UnaryOp(op=USub(), operand=v):
            return neg64(interp_exp(v))
        case Constant(value=value):
            return value
        case Call(func=Name(id="input_int"), args=[]):
            return input_int()


def interp_stmt(s):
    match s:
        case Expr(value=Call(func=Name(id="print"), args=[arg])):
            print(interp_exp(arg))
        case Expr(value=value):
            interp_exp(value)


def interp_lang_int(p):
    match p:
        case Module(body=body):
            for s in body:
                interp_stmt(s)


def main():
    eight = Constant(8)
    neg_eight = UnaryOp(USub(), eight)
    read = Call(Name("input_int"), [])
    ast1_1 = BinOp(read, Add(), neg_eight)
    p1 = Module([Expr(ast1_1)])
    print(f"p1 = {p1}")

    if is_lang_int(p1):
        print("p1 is a program in lang int. Interpreting it...")
        interp_lang_int(p1)
    else:
        print("p1 is NOT a program in lang int.")

    p2 = Module([Expr(BinOp(read, Sub(), UnaryOp(Add(), Constant(8))))])
    print(f"p2 = {p2}")

    if is_lang_int(p2):
        print("p2 is a program in lang int. Interpreting it...")
        interp_lang_int(p2)
    else:
        print("p2 is NOT a program in lang int.")


if __name__ == "__main__":
    main()
