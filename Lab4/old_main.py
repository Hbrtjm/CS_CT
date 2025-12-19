
import sys
import os
from parser import Mparser as Parser
from scanner import Scanner
from TreePrinter import TreePrinter
import AST
from TypeChecker import TypeChecker

TESTS = "./Lab4/tests"

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "example1.m"
    filepath = os.path.join(TESTS, filename)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        lexer = Scanner()
        parser = Parser()
        result = parser.parse(lexer.tokenize(text))
        if getattr(parser, "had_error", False):
            print("Parser error")
            sys.exit(1)

        if result and not isinstance(result, AST.Empty):
            TreePrinter.print_result(result)
            try:
                typeChecker = TypeChecker()   
                typeChecker.visit(result)
            except Exception as e:
                print("Checker exception:", e)
            
    except IOError:
        print(f"Cannot open {filename} file")
        sys.exit(1)
    except Exception as e:
        print("Parser exception:", e)

