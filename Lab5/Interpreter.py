import AST
from SymbolTable import SymbolTable
from Memory import *
from Exceptions import  *
from visit import *
import sys
import operator

sys.setrecursionlimit(10000)

class Interpreter(object):

    def __init__(self):
        self.memory_stack = MemoryStack()
        self.memory_stack.push(Memory("global"))

        self.builtins = {
            'zeros': self._zeros,
            'ones': self._ones,
            'eye': self._eye,
        }

        self.operators = {
            '+': self._add,
            '-': self._sub,
            '*': self._mul,
            '/': self._div,
            '==': operator.eq,
            '!=': operator.ne,
            '<': operator.lt,
            '<=': operator.le,
            '>': operator.gt,
            '>=': operator.ge,
            '.+': self._elem_add,
            '.-': self._elem_sub,
            '.*': self._elem_mul,
            './': self._elem_div,
        }

    def _zeros(self, n, *args):
        if args:
            m = int(args[0])
            return [[0 for _ in range(m)] for _ in range(n)]
        return [[0 for _ in range(n)] for _ in range(n)]

    def _ones(self, n, *args):
        if args:
            m = int(args[0])
            return [[1 for _ in range(m)] for _ in range(n)]
        return [[1 for _ in range(n)] for _ in range(n)]

    def _eye(self, n, *args):
        if args:
            m = int(args[0])
            matrix = [[0 for _ in range(m)] for _ in range(n)]
            min_dim = min(n, m)
            for i in range(min_dim):
                matrix[i][i] = 1
            return matrix
        matrix = [[0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            matrix[i][i] = 1
        return matrix

    def _add(self, a, b):
        try:
            if isinstance(a, list) and isinstance(b, list):
                return self._elem_add(a, b)
            elif isinstance(a, list):
                return self._scalar_add(a, b)
            elif isinstance(b, list):
                return self._scalar_add(b, a)
            else:
                return operator.add(a, b)
        except (DimensionError, TypeError):
            raise
        except Exception:
            raise TypeError(f"Cannot add {type(a).__name__} and {type(b).__name__}")

    def _sub(self, a, b):
        if isinstance(a, list) and isinstance(b, list):
            return self._elem_sub(a, b)
        elif isinstance(a, list):
            rows = len(a)
            cols = len(a[0]) if rows > 0 else 0
            result = []
            for i in range(rows):
                row = []
                for j in range(cols):
                    row.append(a[i][j] - b)
                result.append(row)
            return result
        elif isinstance(b, list):
            rows = len(b)
            cols = len(b[0]) if rows > 0 else 0
            result = []
            for i in range(rows):
                row = []
                for j in range(cols):
                    row.append(a - b[i][j])
                result.append(row)
            return result
        else:
            return operator.sub(a, b)

    def _mul(self, a, b):
        if isinstance(a, list) and isinstance(b, list):
            return self._matrix_mul(a, b)
        elif isinstance(a, list):
            return self._scalar_mul(a, b)
        elif isinstance(b, list):
            return self._scalar_mul(b, a)
        else:
            return operator.mul(a, b)

    def _div(self, a, b):
        if isinstance(a, list) and isinstance(b, list):
            return self._elem_div(a, b)
        elif isinstance(a, list):
            rows = len(a)
            cols = len(a[0]) if rows > 0 else 0
            result = []
            for i in range(rows):
                row = []
                for j in range(cols):
                    row.append(a[i][j] / b)
                result.append(row)
            return result
        else:
            return operator.truediv(a, b)

    def _scalar_mul(self, matrix, scalar):
        rows = len(matrix)
        cols = len(matrix[0]) if rows > 0 else 0
        result = []
        for i in range(rows):
            row = []
            for j in range(cols):
                row.append(matrix[i][j] * scalar)
            result.append(row)
        return result

    def _scalar_add(self, matrix, scalar):
        rows = len(matrix)
        cols = len(matrix[0]) if rows > 0 else 0
        result = []
        for i in range(rows):
            row = []
            for j in range(cols):
                row.append(matrix[i][j] + scalar)
            result.append(row)
        return result

    def _matrix_mul(self, a, b):
        rows_a = len(a)
        cols_a = len(a[0]) if rows_a > 0 else 0
        rows_b = len(b)
        cols_b = len(b[0]) if rows_b > 0 else 0

        if cols_a != rows_b:
            raise DimensionError(
                f"Matrix dimensions incompatible for multiplication: ({rows_a}x{cols_a}) * ({rows_b}x{cols_b})"
            )

        result = []
        for i in range(rows_a):
            row = []
            for j in range(cols_b):
                sum_val = 0
                for k in range(cols_a):
                    sum_val += a[i][k] * b[k][j]
                row.append(sum_val)
            result.append(row)
        return result

    def _elem_add(self, a, b):
        if isinstance(a, list) and isinstance(b, list):
            rows_a = len(a)
            cols_a = len(a[0]) if rows_a > 0 else 0
            rows_b = len(b)
            cols_b = len(b[0]) if rows_b > 0 else 0

            if rows_a != rows_b or cols_a != cols_b:
                raise DimensionError(
                    f"Matrix dimensions must match for element-wise addition: ({rows_a}x{cols_a}) vs ({rows_b}x{cols_b})"
                )

            result = []
            for i in range(rows_a):
                row = []
                for j in range(cols_a):
                    row.append(a[i][j] + b[i][j])
                result.append(row)
            return result
        else:
            raise TypeError("Element-wise addition requires matrices")

    def _elem_sub(self, a, b):
        if isinstance(a, list) and isinstance(b, list):
            rows_a = len(a)
            cols_a = len(a[0]) if rows_a > 0 else 0
            rows_b = len(b)
            cols_b = len(b[0]) if rows_b > 0 else 0

            if rows_a != rows_b or cols_a != cols_b:
                raise DimensionError(
                    f"Matrix dimensions must match for element-wise subtraction: ({rows_a}x{cols_a}) vs ({rows_b}x{cols_b})"
                )

            result = []
            for i in range(rows_a):
                row = []
                for j in range(cols_a):
                    row.append(a[i][j] - b[i][j])
                result.append(row)
            return result
        else:
            raise TypeError("Element-wise subtraction requires matrices")

    def _elem_mul(self, a, b):
        if isinstance(a, list) and isinstance(b, list):
            rows_a = len(a)
            cols_a = len(a[0]) if rows_a > 0 else 0
            rows_b = len(b)
            cols_b = len(b[0]) if rows_b > 0 else 0

            if rows_a != rows_b or cols_a != cols_b:
                raise DimensionError(
                    f"Matrix dimensions must match for element-wise multiplication: ({rows_a}x{cols_a}) vs ({rows_b}x{cols_b})"
                )

            result = []
            for i in range(rows_a):
                row = []
                for j in range(cols_a):
                    row.append(a[i][j] * b[i][j])
                result.append(row)
            return result
        else:
            raise TypeError("Element-wise multiplication requires matrices")

    def _elem_div(self, a, b):
        if isinstance(a, list) and isinstance(b, list):
            rows_a = len(a)
            cols_a = len(a[0]) if rows_a > 0 else 0
            rows_b = len(b)
            cols_b = len(b[0]) if rows_b > 0 else 0

            if rows_a != rows_b or cols_a != cols_b:
                raise DimensionError(
                    f"Matrix dimensions must match for element-wise division: ({rows_a}x{cols_a}) vs ({rows_b}x{cols_b})"
                )

            result = []
            for i in range(rows_a):
                row = []
                for j in range(cols_a):
                    row.append(a[i][j] / b[i][j])
                result.append(row)
            return result
        else:
            raise TypeError("Element-wise division requires matrices")

    @on('node')
    def visit(self, node):
        pass

    @when(AST.Statements)
    def visit(self, node):
        result = None
        try:
            for stmt in node.statements:
                result = stmt.accept(self)
        except (BreakException, ContinueException):
            pass
        except ReturnValueException:
            pass
        return result

    @when(AST.Block)
    def visit(self, node):
        try:
            result = None
            if isinstance(node.statements, list):
                for stmt in node.statements:
                    result = stmt.accept(self)
            else:
                result = node.statements.accept(self)
            return result
        finally:
            pass

    @when(AST.Empty)
    def visit(self, node):
        pass

    @when(AST.Literal)
    def visit(self, node):
        return node.value

    @when(AST.Variable)
    def visit(self, node):
        return self.memory_stack.get(node.name)

    @when(AST.Assign)
    def visit(self, node):
        value = node.expr.accept(self)

        if isinstance(node.lvalue, AST.MatrixIndex):
            matrix = self.memory_stack.get(node.lvalue.matrix.name)
            indices = [idx.accept(self) for idx in node.lvalue.indices]

            if node.operator == '=':
                result = value
            elif node.operator == '+=':
                if len(indices) == 1:
                    current = matrix[indices[0]]
                elif len(indices) == 2:
                    current = matrix[indices[0]][indices[1]]
                else:
                    raise Exception("Invalid number of indices")
                result = current + value
            elif node.operator == '-=':
                if len(indices) == 1:
                    current = matrix[indices[0]]
                elif len(indices) == 2:
                    current = matrix[indices[0]][indices[1]]
                else:
                    raise IndexError("Invalid number of indices for matrix assignment")
                result = current - value
            elif node.operator == '*=':
                if len(indices) == 1:
                    current = matrix[indices[0]]
                elif len(indices) == 2:
                    current = matrix[indices[0]][indices[1]]
                else:
                    raise IndexError("Invalid number of indices for matrix assignment")
                result = current * value
            elif node.operator == '/=':
                if len(indices) == 1:
                    current = matrix[indices[0]]
                elif len(indices) == 2:
                    current = matrix[indices[0]][indices[1]]
                else:
                    raise IndexError("Invalid number of indices for matrix assignment")
                result = current / value
            else:
                raise UnknownOperatorError(f"Unknown assignment operator: {node.operator}")

            if len(indices) == 1:
                matrix[indices[0]] = result
            elif len(indices) == 2:
                matrix[indices[0]][indices[1]] = result
            else:
                raise IndexError("Invalid number of indices for matrix assignment")

            return result

        if node.operator == '=':
            result = value
        elif node.operator == '+=':
            current = self.memory_stack.get(node.lvalue.name)
            result = current + value
        elif node.operator == '-=':
            current = self.memory_stack.get(node.lvalue.name)
            result = current - value
        elif node.operator == '*=':
            current = self.memory_stack.get(node.lvalue.name)
            result = current * value
        elif node.operator == '/=':
            current = self.memory_stack.get(node.lvalue.name)
            result = current / value

        else:
            raise UnknownOperatorError(f"Unknown assignment operator: {node.operator}")

        try:
            self.memory_stack.set(node.lvalue.name, result)
        except:
            self.memory_stack.insert(node.lvalue.name, result) 
            
        return result

    @when(AST.If)
    def visit(self, node):
        condition = node.condition.accept(self)

        if condition:
            return node.block.accept(self)
        elif node._else:
            return node._else.accept(self)

        return None

    @when(AST.While)
    def visit(self, node):
        result = None
        try:
            while node.condition.accept(self):
                try:
                    result = node.block.accept(self)
                except ContinueException:
                    continue
                except BreakException:
                    break
        except BreakException:
            pass

        return result

    @when(AST.For)
    def visit(self, node):
        range_vals = node._range.accept(self)
        self.memory_stack.push(Memory("for"))
        result = None
        try:
            for val in range_vals:
                self.memory_stack.insert(node.var.name, val)
                try:
                    result = node.statement.accept(self)
                except ContinueException:
                    continue
                except BreakException:
                    break
        finally:
            self.memory_stack.pop()
        return result

    @when(AST.Range)
    def visit(self, node):
        start = node.start.accept(self)
        end = node.end.accept(self)
        step = node.step.accept(self) if node.step else 1

        return list(range(start, end + 1, step))

    @when(AST.Break)
    def visit(self, node):
        raise BreakException()

    @when(AST.Continue)
    def visit(self, node):
        raise ContinueException()

    @when(AST.Return)
    def visit(self, node):
        value = node.value.accept(self) if node.value else None
        raise ReturnValueException(value)

    @when(AST.Print)
    def visit(self, node):
        values = [elem.accept(self) for elem in node.printlist]
        print(*values)
        return None

    @when(AST.Apply)
    def visit(self, node):
        if node.ref in self.builtins:
            args = [arg.accept(self) for arg in node.args]
            return self.builtins[node.ref](*args)

        if node.ref in self.operators:
            args = [arg.accept(self) for arg in node.args]
            return self.operators[node.ref](*args)

        raise UnknownFunctionError(f"Unknown function or operator: {node.ref}")

    @when(AST.OpExpr)
    def visit(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)

        if node.op in self.operators:
            return self.operators[node.op](left, right)
        else:
            raise UnknownOperatorError(f"Unknown operator: {node.op}")

    @when(AST.UnaryExpr)
    def visit(self, node):
        value = node.expr.accept(self)
        if node.op == '-':
            return -value
        elif node.op == '+':
            return value
        else:
            raise UnknownOperatorError(f"Unknown unary operator: {node.op}")

    @when(AST.Matrix)
    def visit(self, node):
        result = []
        for row in node.rows:
            row_values = []
            for elem in row:
                row_values.append(elem.accept(self))
            result.append(row_values)
        return result

    @when(AST.Transpose)
    def visit(self, node):
        matrix = node.matrix.accept(self)
        if not isinstance(matrix, list):
            raise TypeError("Transpose requires a matrix")

        rows = len(matrix)
        cols = len(matrix[0]) if rows > 0 else 0

        result = []
        for j in range(cols):
            new_row = []
            for i in range(rows):
                new_row.append(matrix[i][j])
            result.append(new_row)

        return result

    @when(AST.MatrixIndex)
    def visit(self, node):
        matrix = self.memory_stack.get(node.matrix.name)
        indices = [idx.accept(self) for idx in node.indices]

        try:
            if len(indices) == 1:
                return matrix[indices[0]]
            elif len(indices) == 2:
                return matrix[indices[0]][indices[1]]
            else:
                raise IndexError(f"Invalid number of indices: expected 1 or 2, got {len(indices)}")
        except (KeyError, IndexError) as e:
            if isinstance(e, KeyError):
                raise IndexError(f"Index out of bounds")
            raise IndexError(f"Index out of bounds: {e}")
        except Exception as e:
            raise TypeError(f"Cannot index matrix: {e}")



