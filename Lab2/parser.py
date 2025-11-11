import os
from sly import Parser
from scanner import Scanner

class Mparser(Parser):
    tokens = list(Scanner.tokens)

    start = 'program'
    debugfile = 'debug/parser.out'

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
    def program(self, p): return ('program', p.statements)

    @_('statements statement')
    def statements(self, p): return p.statements + [p.statement]

    @_('statement')
    def statements(self, p): return [p.statement]

    @_('assignment ";"')
    def statement(self, p): return p.assignment if hasattr(p, 'assignment') else p.expr
    
    @_('BREAK ";"')
    def statement(self, p): return ('break',)
    
    @_('CONTINUE ";"')
    def statement(self, p): return ('continue',)
    
    @_('RETURN expr ";"')
    def statement(self, p): return ('return', p.expr)

    @_('PRINT elements ";"')
    def statement(self, p): return ('print', p.elements)

    @_('IF "(" condition ")" statement %prec IFX')
    def statement(self, p): return ('if', p.condition, p.statement)

    @_('IF "(" condition ")" statement ELSE statement')
    def statement(self, p): return ('if_else', p.condition, p.statement0, p.statement1)
    
    @_('WHILE "(" condition ")" statement')
    def statement(self, p): return ('while', p.condition, p.statement)

    @_('FOR ID "=" range_expr statement')
    def statement(self, p): return ('for', ('id', p.ID), p.range_expr, p.statement)
     
    @_('"{" statements "}"')
    def statement(self, p): return ('block', p.statements)

    @_('";"')
    def statement(self, _): return ('empty',)

    @_('ID')
    @_('_index')
    def lvalue(self, p): return p[0]

    @_('lvalue "=" expr')
    @_('lvalue ADDASSIGN expr')
    @_('lvalue SUBASSIGN expr')
    @_('lvalue MULASSIGN expr')
    @_('lvalue DIVASSIGN expr')
    def assignment(self, p): return ('assign', p[1], p.lvalue, p.expr)

    @_('expr EQ expr')
    @_('expr NE expr')
    @_('expr LT expr')
    @_('expr LE expr')
    @_('expr GT expr')
    @_('expr GE expr')
    def condition(self, p): return ('condition', p[1], p.expr0, p.expr1)

    @_('expr PLUS expr')
    @_('expr MINUS expr')
    @_('expr DOTADD expr')
    @_('expr DOTSUB expr')
    @_('expr TIMES expr')
    @_('expr DIVIDE expr')
    @_('expr DOTMUL expr')
    @_('expr DOTDIV expr')
    def expr(self, p): return (p[1], p.expr0, p.expr1)

    @_('MINUS expr %prec UMINUS')
    def expr(self, p): return ('unary', '-', p.expr)

    @_('ID "[" idx_list "]"')
    def _index(self, p):
        return ('index', p.ID, p.idx_list)

    @_('ID  %prec "["') 
    def expr(self, p): return ('id', p.ID)

    @_('_index')
    def expr(self, p): return p

    @_('expr "\'"')
    def expr(self, p): return ('transpose', p.expr)

    @_('ONES "(" idx_list ")"')
    def expr(self, p): return ('ones', p.idx_list)

    @_('EYE "(" idx_list ")"')
    def expr(self, p): return ('eye', p.idx_list)

    @_('ZEROS "(" idx_list ")"')
    def expr(self, p): return ('zeros', p.idx_list)

    @_('"[" rows "]"')
    def expr(self, p): return ('matrix', p.rows)

    @_('"(" expr ")"')
    def expr(self, p): return p.expr

    @_('INTNUM')
    def expr(self, p): return ('int', int(p.INTNUM))

    @_('FLOATNUM')
    def expr(self, p): return ('float', float(p.FLOATNUM))

    @_('STRING')
    def expr(self, p): return ('str', p.STRING)

    @_('INTNUM')
    def idx_list(self, p): return [p.INTNUM]

    @_('idx_list "," INTNUM')
    def idx_list(self, p): return p.idx_list + [p.INTNUM]

    @_('elements')
    def rows(self, p): return [p.elements]

    @_('rows ";" elements')
    def rows(self, p): return p.rows + [p.elements]

    @_('expr')
    def elements(self, p): return [p.expr]

    @_('elements "," expr')
    def elements(self, p): return p.elements + [p.expr]

    @_('expr ":" expr ":" expr')
    def range_expr(self, p): return ('range', p.expr0, p.expr1, p.expr2)

    @_('expr ":" expr')
    def range_expr(self, p): return ('range', p.expr0, p.expr1)

    def error(self, p):
        if p:
            lineno = getattr(p, 'lineno', '?')
            val = getattr(p, 'value', None)
            print(f"Syntax error at line {lineno}: unexpected token {p.type} (value={val})")
            self.errok()
        else:
            print("Syntax error at EOF (unexpected end of file)")


if __name__ == '__main__':
    import sys
    lexer = Scanner()
    parser = Mparser()

    filename = sys.argv[1] if len(sys.argv) > 1 else "example3.m"
    filepath = os.path.join("tests", filename)
    with open(filepath, "r", encoding='utf-8') as f:
        text = f.read()

    try:
        result = parser.parse(lexer.tokenize(text))
        print("=== AST ===")
        import pprint
        pprint.pprint(result)
    except Exception as e:
        print("Parser exception:", e)
