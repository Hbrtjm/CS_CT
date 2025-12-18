import sys
from scanner import Scanner
from parser import Mparser
from TreePrinter import TreePrinter
from TypeChecker import TypeChecker
from Interpreter import Interpreter


def main():
    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else "./tests/example1.m"
        with open(filename, "r") as file:
            text = file.read()
    except IOError:
        print(f"Cannot open file: {filename}")
        sys.exit(1)

    print(f"=== Running {filename} ===\n")

    scanner = Scanner()

    parser = Mparser()
    try:
        ast = parser.parse(scanner.tokenize(text))
    except Exception as e:
        print(f"Parse error: {e}")
        sys.exit(1)

    if ast is None:
        print("Parsing failed")
        sys.exit(1)

    try:
        type_checker = TypeChecker()
        ast.accept(type_checker)
    except Exception as e:
        print(f"Type checking error: {e}")

    try:
        interpreter = Interpreter()
        ast.accept(interpreter)
    except Exception as e:
        print(f"\nRuntime error: {e}")
        import traceback
        traceback.print_exc()

    print("\nDone")


if __name__ == '__main__':
    main()