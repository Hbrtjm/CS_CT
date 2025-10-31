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
        ('right', 'NEGATE', 'UMINUS'),
        ('right', '[', '\''),
    )

    @_('statements')
    def program(self, p): return ('program', p.statements)

    @_('statements statement')
    def statements(self, p): return p.statements + [p.statement]

    @_('statement')
    def statements(self, p): return [p.statement]

    @_('simple_stmt ";"')
    def statement(self, p): return p.simple_stmt

    @_('compound_stmt')
    def statement(self, p): return p.compound_stmt

    @_('compound_block')
    def statement(self, p): return p.compound_block

    @_('";"')
    def statement(self, _): return ('empty',)

    @_('assignment')
    def simple_stmt(self, p): return p

    @_('expr')
    def simple_stmt(self, p): return p.expr
    
    @_('BREAK')
    def simple_stmt(self, p): return ('break',)
    
    @_('CONTINUE')
    def simple_stmt(self, p): return ('continue',)
    
    @_('RETURN expr')
    def simple_stmt(self, p): return ('return', p.expr)

    @_('ID')
    def lvalue(self, p): return ('id', p.ID)

    @_('index')
    def lvalue(self, p): return p

    @_('lvalue "=" expr')
    def assignment(self, p): return ('assign', '=', p.lvalue, p.expr)

    @_('lvalue ADDASSIGN expr')
    def assignment(self, p): return ('addassign', '+=', p.lvalue, p.expr)

    @_('lvalue SUBASSIGN expr')
    def assignment(self, p): return ('subassign', '-=', p.lvalue, p.expr)

    @_('lvalue MULASSIGN expr')
    def assignment(self, p): return ('mulassign', '*=', p.lvalue, p.expr)

    @_('lvalue DIVASSIGN expr')
    def assignment(self, p): return ('divassign', '/=', p.lvalue, p.expr)

    @_('PRINT print_list')
    def simple_stmt(self, p): return ('print', p.print_list)

    @_('expr "," print_list')
    def print_list(self, p): return [p.expr] + p.print_list

    @_('expr')
    def print_list(self, p): return [p.expr]

    @_('IF "(" condition ")" statement %prec IFX')
    def compound_stmt(self, p): return ('if', p.condition, p.statement)

    @_('IF "(" condition ")" statement ELSE statement')
    def compound_stmt(self, p): return ('if_else', p.condition, p.statement0, p.statement1)
    
    @_('WHILE "(" condition ")" statement')
    def compound_stmt(self, p): return ('while', p.condition, p.statement)

    @_('FOR ID "=" range_expr statement')
    def compound_stmt(self, p): return ('for', ('id', p.ID), p.range_expr, p.statement)
    
    @_('"{" statements "}"')
    def compound_block(self, p): return ('block', p.statements)

    @_('expr EQ expr')
    def condition(self, p): return ('eq', p.expr0, p.expr1)

    @_('expr NE expr')
    def condition(self, p): return ('ne', p.expr0, p.expr1)

    @_('expr LT expr')
    def condition(self, p): return ('lt', p.expr0, p.expr1)

    @_('expr LE expr')
    def condition(self, p): return ('le', p.expr0, p.expr1)

    @_('expr GT expr')
    def condition(self, p): return ('gt', p.expr0, p.expr1)

    @_('expr GE expr')
    def condition(self, p): return ('ge', p.expr0, p.expr1)

    @_('expr PLUS term')
    def expr(self, p): return ('+', p.expr, p.term)

    @_('expr MINUS term')
    def expr(self, p): return ('-', p.expr, p.term)

    @_('expr DOTADD term')
    def expr(self, p): return ('.+', p.expr, p.term)

    @_('expr DOTSUB term')
    def expr(self, p): return ('.-', p.expr, p.term)

    @_('term')
    def expr(self, p): return p.term

    @_('term TIMES factor')
    def term(self, p): return ('*', p.term, p.factor)

    @_('term DIVIDE factor')
    def term(self, p): return ('/', p.term, p.factor)

    @_('term DOTMUL factor')
    def term(self, p): return ('.*', p.term, p.factor)

    @_('term DOTDIV factor')
    def term(self, p): return ('./', p.term, p.factor)

    @_('factor')
    def term(self, p): return p.factor
    
    @_('MINUS term %prec UMINUS')
    def term(self, p): return ('neg', p.term)

    @_('NEGATE term %prec NEGATE')
    def term(self, p): return ('negate', p.term)

    @_('ID "[" idx_list "]"')
    def index(self, p):
        return ('index', p.ID, p.idx_list)

    @_('ID') 
    def factor(self, p): return ('id', p.ID)

    @_('index')
    def factor(self, p): return p

    @_('factor "\'"')
    def factor(self, p): return ('transpose', p.factor)

    @_('ONES "(" idx_list ")"')
    def factor(self, p): return ('ones', p.idx_list)

    @_('EYE "(" idx_list ")"')
    def factor(self, p): return ('eye', p.idx_list)

    @_('ZEROS "(" idx_list ")"')
    def factor(self, p): return ('zeros', p.idx_list)

    @_('matrix_literal')
    def factor(self, p): return p.matrix_literal

    @_('"(" expr ")"')
    def factor(self, p): return p.expr

    @_('INTNUM')
    def factor(self, p): return ('int', int(p.INTNUM))

    @_('FLOATNUM')
    def factor(self, p): return ('float', float(p.FLOATNUM))

    @_('SCINOTATION')
    def factor(self, p): return ('float', float(p.SCINOTATION))

    @_('STRING')
    def factor(self, p): return ('str', p.STRING)

    @_('INTNUM')
    def idx_list(self, p): return [p.INTNUM]

    @_('idx_list "," INTNUM')
    def idx_list(self, p): return p.idx_list + [p.INTNUM]

    @_('"[" rows "]"')
    def matrix_literal(self, p): return ('matrix', p.rows)

    @_('row')
    def rows(self, p): return [p.row]

    @_('rows ";" row')
    def rows(self, p): return p.rows + [p.row]

    @_('elements')
    def row(self, p): return p.elements

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
