"""Integer language lang_int AST nodes and interpreter."""

import ast


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


def is_expression(e):
    match e:
        case Constant(value=n):
            return isinstance(n, int)
        case Call(func=Name(id="input_int"), args=[]):
            return True
        case UnaryOp(op=USub(), operand=e1):
            return is_expression(e1)
        case BinOp(left=e1, op=Add(), right=e2):
            return is_expression(e1) and is_expression(e2)
        case BinOp(left=e1, op=USub(), right=e2):
            return is_expression(e1) and is_expression(e2)
        case _:
            return False


def is_statement(s):
    match s:
        case Expr(value=Call(func=Name(id="print"), args=[e])):
            return is_expression(e)
        case Expr(value=e):
            return is_expression(e)
        case _:
            return False


def is_lang_int_module(m):
    match m:
        case Module(body=body):
            return all([is_statement(s) for s in body])
        case _:
            return False


def main():
    eight = Constant(8)
    neg_eight = UnaryOp(USub(), eight)
    read = Call(Name("input_int"), [])
    ast1_1 = BinOp(read, Add(), neg_eight)
    print(ast1_1)

    m1 = Module([Expr(ast1_1)])
    print(is_lang_int_module(m1))

    m2 = Module([Expr(BinOp(read, Sub(), UnaryOp(Add(), Constant(8))))])
    print(is_lang_int_module(m2))


if __name__ == "__main__":
    main()
