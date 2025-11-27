import AST

def addToClass(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator


class TreePrinter:
    @staticmethod
    def safe_print_tree(obj, indent_level=0) -> None:
        prefix = "|  " * indent_level
        if obj is not None and hasattr(obj, "print_tree"):
            obj.print_tree(indent_level)
        else:
            print(f"{prefix}{obj}")

    @addToClass(AST.Statements)
    def print_tree(self, *args) -> None:
        statements = self.statements
        if isinstance(statements, (tuple, list)):
            for r in statements:
                if hasattr(r, "print_tree"):
                    r.print_tree(0)
                else:
                    print(r)
        elif hasattr(statements, "print_tree"):
            statements.print_tree(0)
        else:
            print(statements)

    @addToClass(AST.Block)
    def print_tree(self, indent_level=0) -> None:
        statements = self.statements
        if isinstance(statements, (tuple, list)):
            for statement in statements:
                if hasattr(statement, "print_tree"):
                    statement.print_tree(indent_level)
                else:
                    print(statement)
        elif hasattr(statements, "print_tree"):
            statements.print_tree(indent_level)
        else:
            print(statements)

    @addToClass(AST.Variable)
    def print_tree(self, indent_level=0) -> None:
        print("|  " * indent_level + f"{self.name}")

    @addToClass(AST.OpExpr)
    def print_tree(self, indent_level=0) -> None:
        print("|  " * indent_level + self.op)
        TreePrinter.safe_print_tree(self.left, indent_level + 1)
        TreePrinter.safe_print_tree(self.right, indent_level + 1)

    @addToClass(AST.Matrix)
    def print_tree(self, indent_level=0) -> None:
        print("|  " * indent_level + "MATRIX")
        for row in self.rows:
            print("|  " * (indent_level + 1) + "ROW")
            for elem in row:
                TreePrinter.safe_print_tree(elem, indent_level + 2)

    @addToClass(AST.Transpose)
    def print_tree(self, indent_level=0) -> None:
        print("|  " * indent_level + "TRANSPOSE")
        TreePrinter.safe_print_tree(self.matrix, indent_level + 1)

    @addToClass(AST.Break)
    def print_tree(self, indent_level=0) -> None:
        print("|  " * indent_level + "BREAK")

    @addToClass(AST.Continue)
    def print_tree(self, indent_level=0) -> None:
        print("|  " * indent_level + "CONTINUE")

    @addToClass(AST.Return)
    def print_tree(self, indent_level=0) -> None:
        print("|  " * indent_level + "RETURN")
        TreePrinter.safe_print_tree(self.value, indent_level + 1)

    @addToClass(AST.Print)
    def print_tree(self, indent_level=0) -> None:
        print("|  " * indent_level + "PRINT")
        for expr in self.printlist:
            TreePrinter.safe_print_tree(expr, indent_level + 1)

    @addToClass(AST.Range)
    def print_tree(self, indent_level=0) -> None:
        print("|  " * indent_level + "RANGE")
        TreePrinter.safe_print_tree(self.start, indent_level + 1)
        TreePrinter.safe_print_tree(self.end, indent_level + 1)
        if getattr(self, "step", None):
            TreePrinter.safe_print_tree(self.step, indent_level + 1)

    @addToClass(AST.For)
    def print_tree(self, indent_level=0) -> None:
        print("|  " * indent_level + "FOR")
        print("|  " * (indent_level + 1) + self.var.name)
        TreePrinter.safe_print_tree(self._range, indent_level + 1)
        TreePrinter.safe_print_tree(self.statement, indent_level + 1)

    @addToClass(AST.While)
    def print_tree(self, indent_level=0) -> None:
        print("|  " * indent_level + "WHILE")
        TreePrinter.safe_print_tree(self.condition, indent_level + 1)
        TreePrinter.safe_print_tree(self.block, indent_level + 1)

    @addToClass(AST.If)
    def print_tree(self, indent_level=0) -> None:
        print("|  " * indent_level + "IF")
        TreePrinter.safe_print_tree(self.condition, indent_level + 1)
        if self.block:
            print("|  " * (indent_level + 1) + "THEN")
            TreePrinter.safe_print_tree(self.block, indent_level + 1)
        if getattr(self, "_else", None):
            print("|  " * (indent_level + 1) + "ELSE")
            TreePrinter.safe_print_tree(self._else, indent_level + 1)

    @addToClass(AST.Apply)
    def print_tree(self, indent_level=0) -> None:
        print("|  " * indent_level + f"{self.ref}")
        for arg in self.args:
            TreePrinter.safe_print_tree(arg, indent_level + 1)

    @addToClass(AST.UnaryExpr)
    def print_tree(self, indent_level=0) -> None:
        print("|  " * indent_level + f"UNARY {self.op}")
        TreePrinter.safe_print_tree(self.expr, indent_level + 1)

    @addToClass(AST.Literal)
    def print_tree(self, indent_level=0) -> None:
        print("|  " * indent_level + str(self.value))

    @addToClass(AST.MatrixIndex)
    def print_tree(self, indent_level=0) -> None:
        print("|  " * indent_level + "MATRIX INDEX")
        print("|  " * (indent_level + 1) + "ARGUMENTS")
        TreePrinter.safe_print_tree(self.matrix, indent_level + 2)
        print("|  " * (indent_level + 1) + "INDICES")
        for index in self.indices:
            TreePrinter.safe_print_tree(index, indent_level + 2)

    @addToClass(AST.Assign)
    def print_tree(self, indent_level=0) -> None:
        print("|  " * indent_level + self.operator)
        TreePrinter.safe_print_tree(self.lvalue, indent_level + 1)
        TreePrinter.safe_print_tree(self.expr, indent_level + 1)

    @staticmethod
    def print_result(result):
        if isinstance(result, list):
            for r in result:
                if hasattr(r, "print_tree"):
                    r.print_tree(0)
                else:
                    print(r)
        elif hasattr(result, "print_tree"):
            result.print_tree(0)
        else:
            print(result)
