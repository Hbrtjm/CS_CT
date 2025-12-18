import os
import sys
from sly import Parser
from scanner import Scanner
import AST
from TreePrinter import TreePrinter

class Mparser(Parser):
    had_error = False
    tokens = list(Scanner.tokens)
    start = 'program'
    # debugfile = 'debug/parser.out'

    precedence = (
        ('nonassoc', 'IFX'),
        ('nonassoc', 'ELSE'),
        ('nonassoc', ':'),
        ('nonassoc', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NE'),
        ('left', 'PLUS', 'MINUS', 'DOTADD', 'DOTSUB'),
        ('left', 'TIMES', 'DIVIDE', 'DOTMUL', 'DOTDIV'),
        ('right', 'UMINUS'),
        ('right', '\''),
        ('left', '['),
    )

    @_('statements')
    def program(self, p): return AST.Statements(p.statements)

    @_('statements statement')
    def statements(self, p): return p.statements + [p.statement]

    @_('statement')
    def statements(self, p): return [p.statement]

    @_('assignment ";"')
    def statement(self, p): return p.assignment

    @_('BREAK ";"')
    def statement(self, p): return AST.Break(p.lineno)
    
    @_('CONTINUE ";"')
    def statement(self, p): return AST.Continue(p.lineno)
    
    @_('RETURN expr ";"')
    def statement(self, p): return AST.Return(p.expr, p.lineno)

    @_('PRINT elements ";"')
    def statement(self, p): return AST.Print(p.elements, p.lineno)

    @_('IF "(" condition ")" statement %prec IFX')
    def statement(self, p): return AST.If(p.condition, p.statement)

    @_('IF "(" condition ")" statement ELSE statement')
    def statement(self, p): return AST.If(p.condition, p.statement0, p.statement1)
    
    @_('WHILE "(" condition ")" statement')
    def statement(self, p): return AST.While(p.condition, p.statement)

    @_('FOR ID "=" range_expr statement')
    def statement(self, p):
        var = AST.Variable(p.ID, p.lineno)
        return AST.For(var, p.range_expr, p.statement, p.lineno)

    @_('"{" statements "}"')
    def statement(self, p): return AST.Block(p.statements)

    @_('";"')
    def statement(self, p): return AST.Empty(p.lineno)

    @_('ID')
    def lvalue(self, p): return AST.Variable(p.ID)

    @_('_index')
    def lvalue(self, p): return p._index

    @_('lvalue "=" expr')
    @_('lvalue ADDASSIGN expr')
    @_('lvalue SUBASSIGN expr')
    @_('lvalue MULASSIGN expr')
    @_('lvalue DIVASSIGN expr')
    def assignment(self, p): return AST.Assign(p.lvalue, p[1], p.expr, p.lineno)
    
    @_('expr EQ expr')
    @_('expr NE expr')
    @_('expr LT expr')
    @_('expr LE expr')
    @_('expr GT expr')
    @_('expr GE expr')
    def condition(self, p): return AST.OpExpr(p[1], p.expr0, p.expr1, p.lineno)

    @_('expr PLUS expr')
    @_('expr MINUS expr')
    @_('expr DOTADD expr')
    @_('expr DOTSUB expr')
    @_('expr TIMES expr')
    @_('expr DIVIDE expr')
    @_('expr DOTMUL expr')
    @_('expr DOTDIV expr')
    def expr(self, p): return AST.Apply(p[1], [p.expr0,p.expr1], p.lineno)
    
    @_('MINUS expr %prec UMINUS')
    def expr(self, p): return AST.UnaryExpr('-', p.expr, p.lineno)

    @_('expr "\'"')
    def expr(self, p): return AST.Transpose(p.expr, p.lineno)

    @_('ID %prec "["') 
    def expr(self, p): return AST.Variable(p.ID, p.lineno)

    @_('ID "[" idx_list "]"')
    def _index(self, p):     
        var = AST.Variable(p.ID, p.lineno)
        return AST.MatrixIndex(var, p.idx_list, p.lineno)

    @_('_index')
    def expr(self, p): return p._index

    @_('ONES "(" idx_list ")"')
    def expr(self, p): return AST.Apply('ones', p.idx_list, p.lineno)

    @_('EYE "(" idx_list ")"')
    def expr(self, p): return AST.Apply('eye', p.idx_list, p.lineno)

    @_('ZEROS "(" idx_list ")"')
    def expr(self, p): return AST.Apply('zeros', p.idx_list, p.lineno)

    @_('"[" rows "]"')
    def expr(self, p): return AST.Matrix(p.rows, p.lineno)

    @_('"(" expr ")"')
    def expr(self, p): return p.expr

    @_('INTNUM')
    def expr(self, p): return AST.Literal.int(int(p.INTNUM), p.lineno)

    @_('FLOATNUM')
    def expr(self, p): return AST.Literal.float(float(p.FLOATNUM), p.lineno)

    @_('STRING')
    def expr(self, p): return AST.Literal.string(p.STRING[1:-1], p.lineno)  # Strip quotes

    @_('INTNUM')
    def idx_list(self, p): return [AST.Literal.int(int(p.INTNUM), p.lineno)]

    @_('idx_list "," INTNUM')
    def idx_list(self, p): return p.idx_list + [AST.Literal.int(int(p.INTNUM), p.lineno)]

    @_('elements')
    def rows(self, p): return [p.elements]

    @_('rows ";" elements')
    def rows(self, p): return p.rows + [p.elements]

    @_('expr')
    def elements(self, p): return [p.expr]

    @_('elements "," expr')
    def elements(self, p): return p.elements + [p.expr]

    @_('expr ":" expr ":" expr')
    def range_expr(self, p): return AST.Range(p.expr0, p.expr1, p.expr2, p.lineno)

    @_('expr ":" expr')
    def range_expr(self, p): return AST.Range(p.expr0, p.expr1, None, p.lineno)

    def error(self, p):
        if p:
            lineno = getattr(p, 'lineno', '?')
            val = getattr(p, 'value', None)
            print(f"Syntax error at line {lineno}: unexpected token {p.type} (value={val})")
            self.had_error = True
            self.errok()
        else:
            print("Syntax error at EOF (unexpected end of file)")


if __name__ == '__main__':
    lexer = Scanner()
    parser = Mparser()

    filename = sys.argv[1] if len(sys.argv) > 1 else "example3.m"
    filepath = os.path.join("tests", filename)
    with open(filepath, "r", encoding='utf-8') as f:
        text = f.read()

    try:
        result = parser.parse(lexer.tokenize(text))
        
        if parser.had_error:
            print("Parser error")
            sys.exit(1)
            
        if result and not isinstance(result, AST.Empty):
            N = 20
            print(N * "=" + "\tAST\t" + N * "=")
            TreePrinter.print_result(result)
    
    except Exception as e:
        print("Parser exception:", e)
