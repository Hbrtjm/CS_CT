from dataclasses import dataclass
from typing import List, Optional, Iterator

@dataclass
class Node(object):
    def __init__(self, lineno):
        self.lineno = lineno

class Expr(Node):
    def __init__(self, lineno=None):
        super().__init__(lineno)

@dataclass(init=False)
class Statements(Node):
    statements: list[Node]

    def __init__(self, statements: list[Node], lineno: Optional[int] = None):
        super().__init__(lineno)
        self.statements = statements

    def __iter__(self) -> Iterator[Node]:
        return iter(self.statements)

class Empty(Node):
    def __init__(self, lineno=None):
        super().__init__(lineno)

class Block(Node):
    statements: List[Node]
    
    def __init__(self, statements, lineno=None):
        super().__init__(lineno)
        self.statements = statements

class Variable(Node):
    name: str

    def __init__(self, name, lineno=None):
        super().__init__(lineno)
        self.name = name

class OpExpr(Node):
    op: str
    left: Expr
    right: Expr
        
    def __init__(self, op, left, right, lineno=None):
        super().__init__(lineno)
        self.op = op
        self.left = left
        self.right = right

class Matrix(Node):
    rows: List[List[Expr]]
    
    def __init__(self, rows, lineno=None):
        super().__init__(lineno)
        self.rows = rows

class Transpose(Node):
    matrix: Matrix
    
    def __init__(self, matrix, lineno=None):
        super().__init__(lineno)
        self.matrix = matrix

class Break(Node):
    def __init__(self, lineno=None):
        super().__init__(lineno)

class Continue(Node):
    def __init__(self, lineno=None):
        super().__init__(lineno)

class Return(Node):
    value: Optional[Expr]
    
    def __init__(self, value, lineno=None):
        super().__init__(lineno)
        self.value = value

class Print(Node):
    printlist: List[Expr]
    
    def __init__(self, printlist, lineno=None):
        super().__init__(lineno)
        self.printlist = printlist

class Range(Node):
    start: Expr
    end: Expr
    step: Optional[Expr]
    
    def __init__(self, start, end, step=None, lineno=None):
        super().__init__(lineno)
        self.start = start
        self.end = end
        self.step = step

class For(Node):
    var: Variable
    _range: Range
    statement: Node
    
    def __init__(self, var, _range, statement, lineno=None):
        super().__init__(lineno)
        self.var = var
        self._range = _range
        self.statement = statement

class While(Node):
    condition: Expr
    block: Node
    
    def __init__(self, condition, block, lineno=None):
        super().__init__(lineno)
        self.condition = condition
        self.block = block

class If(Node):
    condition: Expr
    block: Block
    _else: Optional[Block]
    
    def __init__(self, condition, block, _else=None, lineno=None):
        super().__init__(lineno)
        self.condition = condition
        self.block = block
        self._else = _else if isinstance(_else, Block) else (Block(_else, lineno) if _else else None)

class Apply(Expr):
    ref: str
    args: list[Expr]

    def __init__(self, ref: str, args: list[Expr], lineno: int):
        super().__init__(lineno)
        self.ref = ref
        self.args = args

class UnaryExpr(Node):
    def __init__(self, op, expr, lineno=None):
        super().__init__(lineno)
        self.op = op
        self.expr = expr

class Literal(Node):
    def __init__(self, value, typename, lineno=None):
        super().__init__(lineno)
        self.value = value
        self.typename = typename
    @staticmethod
    def int(value, lineno=None):
        return Literal(value, "int", lineno)
    @staticmethod
    def float(value, lineno=None):
        return Literal(value, "float", lineno)
    @staticmethod
    def string(value, lineno=None):
        return Literal(value, "string", lineno)

class MatrixIndex(Node):
    def __init__(self, matrix: Variable, indices: list[Expr], lineno=None):
        super().__init__(lineno)
        self.matrix = matrix
        self.indices = indices


class Assign(Node):
    lvalue: Variable
    expr: Expr 
    operator: str
    
    def __init__(self, lvalue, operator, expr, lineno=None):
        super().__init__(lineno)
        self.lvalue = lvalue
        self.operator = operator
        self.expr = expr