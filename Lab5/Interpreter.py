import AST
from SymbolTable import SymbolTable
from Memory import *
from Exceptions import  *
from visit import *
import sys
import operator
import numpy as np

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
            return np.zeros((n, m), dtype=int)
        return np.zeros((n, n), dtype=int)

    def _ones(self, n, *args):
        if args:
            m = int(args[0])
            return np.ones((n, m), dtype=int)
        return np.ones((n, n), dtype=int)

    def _eye(self, n, *args):
        if args:
            m = int(args[0])
            return np.eye(n, m, dtype=int)
        return np.eye(n, dtype=int)

    def _add(self, a, b):
        try:
            return a + b
        except (DimensionError, TypeError) as e:
            raise TypeError(f"Cannot add {type(a).__name__} and {type(b).__name__}") from e

    def _sub(self, a, b):
        return a - b

    def _mul(self, a, b):
        if isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
            return a @ b
        elif isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
            return np.multiply(a, b)
        else:
            return a * b

    def _div(self, a, b):
        if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
            return np.divide(a, b)
        else:
            return a / b

    def _scalar_mul(self, matrix, scalar):
        return np.multiply(matrix, scalar)

    def _scalar_add(self, matrix, scalar):
        return np.add(matrix, scalar)

    def _matrix_mul(self, a, b):
        try:
            return a @ b
        except ValueError as e:
            raise DimensionError(f"Matrix dimensions incompatible for multiplication: {e}")

    def _elem_add(self, a, b):
        if isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
            try:
                return a + b
            except ValueError as e:
                raise DimensionError(f"Matrix dimensions incompatible for element-wise addition: {e}")
        else:
            raise TypeError("Element-wise addition requires matrices")

    def _elem_sub(self, a, b):
        if isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
            try:
                return a - b
            except ValueError as e:
                raise DimensionError(f"Matrix dimensions incompatible for element-wise subtraction: {e}")
        else:
            raise TypeError("Element-wise subtraction requires matrices")

    def _elem_mul(self, a, b):
        if isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
            try:
                return a * b
            except ValueError as e:
                raise DimensionError(f"Matrix dimensions incompatible for element-wise multiplication: {e}")
        else:
            raise TypeError("Element-wise multiplication requires matrices")

    def _elem_div(self, a, b):
        if isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
            try:
                return a / b
            except ValueError as e:
                raise DimensionError(f"Matrix dimensions incompatible for element-wise division: {e}")
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
                    current = matrix[indices[0], indices[1]]
                else:
                    raise Exception("Invalid number of indices")
                result = current + value
            elif node.operator == '-=':
                if len(indices) == 1:
                    current = matrix[indices[0]]
                elif len(indices) == 2:
                    current = matrix[indices[0], indices[1]]
                else:
                    raise IndexError("Invalid number of indices for matrix assignment")
                result = current - value
            elif node.operator == '*=':
                if len(indices) == 1:
                    current = matrix[indices[0]]
                elif len(indices) == 2:
                    current = matrix[indices[0], indices[1]]
                else:
                    raise IndexError("Invalid number of indices for matrix assignment")
                result = current * value
            elif node.operator == '/=':
                if len(indices) == 1:
                    current = matrix[indices[0]]
                elif len(indices) == 2:
                    current = matrix[indices[0], indices[1]]
                else:
                    raise IndexError("Invalid number of indices for matrix assignment")
                result = current / value
            else:
                raise UnknownOperatorError(f"Unknown assignment operator: {node.operator}")

            if len(indices) == 1:
                matrix[indices[0]] = result
            elif len(indices) == 2:
                matrix[indices[0], indices[1]] = result
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
        formatted_values = []
        for val in values:
            if isinstance(val, np.ndarray):
                formatted_values.append(val.tolist())
            else:
                formatted_values.append(val)
        print(*formatted_values)
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
        return np.array(result)

    @when(AST.Transpose)
    def visit(self, node):
        matrix = node.matrix.accept(self)
        if not isinstance(matrix, np.ndarray):
            raise TypeError("Transpose requires a matrix")

        return matrix.T

    @when(AST.MatrixIndex)
    def visit(self, node):
        matrix = self.memory_stack.get(node.matrix.name)
        indices = [idx.accept(self) for idx in node.indices]

        try:
            if len(indices) == 1:
                return matrix[indices[0]]
            elif len(indices) == 2:
                result = matrix[indices[0], indices[1]]
                return result.item() if isinstance(result, np.ndarray) and result.ndim == 0 else result
            else:
                raise IndexError(f"Invalid number of indices: expected 1 or 2, got {len(indices)}")
        except (KeyError, IndexError) as e:
            if isinstance(e, KeyError):
                raise IndexError(f"Index out of bounds")
            raise IndexError(f"Index out of bounds: {e}")
        except Exception as e:
            raise TypeError(f"Cannot index matrix: {e}")



