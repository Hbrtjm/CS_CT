import sys
from sly import Lexer

class Scanner(Lexer):
    
    tokens = {
        'PLUS', 
        'MINUS',
        'TIMES', 
        'DIVIDE',

        'DOTADD', 
        'DOTSUB', 
        'DOTMUL', 
        'DOTDIV',

        'ADDASSIGN', 
        'SUBASSIGN', 
        'MULASSIGN', 
        'DIVASSIGN',
        
        'EQ', 
        'LE', 
        'GE', 
        'LT', 
        'GT', 
        'NE',

        'INTNUM', 
        'FLOATNUM',
        'STRING', 
        'ID',

        'ZEROS', 
        'ONES', 
        'EYE', 
        'PRINT',
        
        'IF', 
        'ELSE', 
        'WHILE', 
        'FOR', 
        'CONTINUE',
        'BREAK', 
        'RETURN',
    }
    
    literals = { '[', ']', '(', ')', '{', '}', ';', ':', ',', '=', '\'', '"'}
    
    FLOATNUM = r'(\d+\.\d*|\.\d+)((E|e)[-+]?\d+)?'
    INTNUM   = r'\d+'
    STRING   = r'\"[^\"]*\"'

    ADDASSIGN = r'\+='
    SUBASSIGN = r'-='
    MULASSIGN = r'\*='
    DIVASSIGN = r'/='

    DOTADD = r'\.\+'
    DOTSUB = r'\.-'
    DOTMUL = r'\.\*'
    DOTDIV = r'\./'

    PLUS   = r'\+'
    MINUS  = r'-'
    TIMES  = r'\*'
    DIVIDE = r'/'
    
    EQ = r'=='
    LE = r'<='
    GE = r'>='
    NE = r'!='
    LT = r'<'
    GT = r'>'
    
    ID = r'[A-Za-z_][A-Za-z0-9_]*'
    ID['zeros']    = 'ZEROS'
    ID['ones']     = 'ONES'
    ID['eye']      = 'EYE'
    ID['print']    = 'PRINT'
    ID['if']       = 'IF'
    ID['else']     = 'ELSE'
    ID['while']    = 'WHILE'
    ID['for']      = 'FOR'
    ID['continue'] = 'CONTINUE'
    ID['break'] = 'BREAK'
    ID['return']   = 'RETURN'
    
    ignore = ' \t'
    ignore_comment = r'\#.*'

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print(f"Illegal character {t.value[0]!r} at line {self.lineno}")
        self.index += 1


if __name__ == '__main__':

    lexer = Scanner()

    filename = sys.argv[1] if len(sys.argv) > 1 else "./tests/example0.m"
    with open(filename, "r") as file:
        text = file.read()

    for tok in lexer.tokenize(text):
        print(f"{tok.lineno}: {tok.type}({tok.value})")