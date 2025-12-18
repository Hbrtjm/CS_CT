import sys
import os
from parser import Mparser as Parser
from scanner import Scanner
from TreePrinter import TreePrinter
import AST

TESTS = "tests"

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "example3.m"
    filepath = os.path.join(TESTS, filename)
    custom_indent = sys.argv[2] if len(sys.argv) > 2 else "|  "
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
            TreePrinter.set_indent(custom_indent)
            TreePrinter.print_result(result)
    except IOError:
        print(f"Cannot open {filename} file")
        sys.exit(1)
    except Exception as e:
        print("Parser exception:", e)
