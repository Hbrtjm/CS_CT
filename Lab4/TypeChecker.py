#!/usr/bin/python
from __future__ import annotations

from SymbolTable import SymbolTable
import AST

def is_scalar(t): return t in {"int", "float", "bool", "string"}
def is_numeric(t): return t in {"int", "float"}
def is_matrix(t): return isinstance(t, tuple) and len(t) == 3 and t[0] == "matrix"
def is_range(t):  return isinstance(t, tuple) and len(t) == 2 and t[0] == "range"

def mat_elem(t):  return t[1] if is_matrix(t) else None
def mat_shape(t): return t[2] if is_matrix(t) else (None, None)
def matrix_t(elem, rows, cols): return ("matrix", elem, (rows, cols))
def range_t(elem): return ("range", elem)

def base_elem(t):
    while is_matrix(t):
        t = mat_elem(t)
    return t

def total_shape(t):
    assert is_matrix(t), "total_shape expects a matrix type"
    r, c = mat_shape(t)
    e = mat_elem(t)
    if is_matrix(e):
        ir, ic = total_shape(e)
        tr = None if r is None or ir is None else r * ir
        tc = None if c is None or ic is None else c * ic
        return (tr, tc)
    return (r, c)

def tstr(t):
    if is_matrix(t):
        (r, c) = mat_shape(t)
        return f"matrix<{tstr(mat_elem(t))}>[{r}x{c}]"
    if is_range(t):
        return f"range<{tstr(t[1])}>"
    return str(t)

class NodeVisitor(object):

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        # Fall back: walk children if present
        if isinstance(node, AST.Statements):
            for statement in node.statements:
                self.visit(statement)
        else:
            for child in getattr(node, "children", []):
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, AST.Node):
                            self.visit(item)
                elif isinstance(child, AST.Node):
                    self.visit(child)

class TypeChecker(NodeVisitor):
    ttype = {
        "+": {
            "int":  {"int": "int",   "float": "float"},
            "float":{"int": "float", "float": "float"},
            "string":{"string": "string"}
        },
        "-": {
            "int":  {"int": "int",   "float": "float"},
            "float":{"int": "float", "float": "float"},
        },
        "*": {
            "int":  {"int": "int",   "float": "float"},
            "float":{"int": "float", "float": "float"},
        },
        "/": {
            "int":  {"int": "int",   "float": "float"},
            "float":{"int": "float", "float": "float"},
        },
        "==": {
            "int":   {"int": "bool",    "float": "bool"},
            "float": {"int": "bool",    "float": "bool"},
            "bool":  {"bool": "bool"},
            "string":{"string": "bool"},
        },
        "!=": {
            "int":   {"int": "bool",    "float": "bool"},
            "float": {"int": "bool",    "float": "bool"},
            "bool":  {"bool": "bool"},
            "string":{"string": "bool"},
        },
        "<": {
            "int":   {"int": "bool",    "float": "bool"},
            "float": {"int": "bool",    "float": "bool"},
        },
        "<=": {
            "int":   {"int": "bool",    "float": "bool"},
            "float": {"int": "bool",    "float": "bool"},
        },
        ">": {
            "int":   {"int": "bool",    "float": "bool"},
            "float": {"int": "bool",    "float": "bool"},
        },
        ">=": {
            "int":   {"int": "bool",    "float": "bool"},
            "float": {"int": "bool",    "float": "bool"},
        },
        ".+": {
            "matrix": {"matrix":"matrix"},
            "int": {"matrix":"matrix"},
            "float": {"matrix":"matrix"}
        },
        ".*": {
            "matrix": {"matrix":"matrix"},
            "int": {"matrix":"matrix"},
            "float": {"matrix":"matrix"}
        },
        ".-": {
            "matrix": {"matrix":"matrix"},
            "int": {"matrix":"matrix"},
            "float": {"matrix":"matrix"}
        },
        "./": {
            "matrix": {"matrix":"matrix"},
            "int": {"matrix":"matrix"},
            "float": {"matrix":"matrix"}
        }
    }

    def __init__(self, info=False):
        self.st = SymbolTable()
        self.functions = {
            "ones":  (["int"], lambda r, c: matrix_t("float", r, c)),
            "zeros": (["int"], lambda r, c: matrix_t("float", r, c)),
            "eye":   (["int"], lambda r, c: matrix_t("float", r, c)),
        }
        self.info = info

    def error(self, msg, node=None):
        line = getattr(node, "lineno", None)
        if line is not None:
            print(f"[line {line}] {msg}")
        else:
            print(msg)

    def info(self, msg, node=None):
        line = getattr(node, "lineno", None)
        if line is not None and self.info:
            print(f"[line {line}] {msg}")
        else:
            print(msg)
            
    def _transpose_type(self, t, node):
        if not is_matrix(t):
            self.error(f"Transpose expects a matrix, got {tstr(t)}", node)
            return t
        e = mat_elem(t)
        r, c = mat_shape(t)
        te = self._transpose_type(e, node) if is_matrix(e) else e
        return matrix_t(te, c, r)

    def _promote_numeric(self, a, b):
        try:
            return self.ttype["+"][a][b]
        except KeyError:
            return None

    def check_unary(self, op, ty, node):
        if op in {"+", "-"} and is_numeric(ty):
            return ty
        if op in {"+", "-"} and is_matrix(ty):
            return ty
        if op == "!" and ty == "bool":
            return "bool"
        self.error(f"No rule for unary op '{op}' with {tstr(ty)}", node)
        return ty

    def _matrix_broadcast(self, a, b):
        if not (is_matrix(a) and is_matrix(b)):
            return False
        ar, ac = total_shape(a)
        br, bc = total_shape(b)
        r_ok = (ar is None or br is None or ar == br)
        c_ok = (ac is None or bc is None or ac == bc)
        r_multiple = (ar is None or br is None or ( ar % br == 0 and ar != 1 and br != 1))
        c_multiple = (ac is None or bc is None or ac % bc == 0 and ac != 1 and bc != 1)
        return (r_ok and r_multiple) or (c_ok and c_multiple)

    def _same_shape(self, a, b):
        if not (is_matrix(a) and is_matrix(b)):
            return False
        ar, ac = total_shape(a)
        br, bc = total_shape(b)
        r_ok = (ar is None or br is None or ar == br)
        c_ok = (ac is None or bc is None or ac == bc)
        return r_ok and c_ok

    def check_binop(self, op, lt, rt, node):
        if op in self.ttype and (lt in self.ttype[op]) and (rt in self.ttype[op][lt]):
            return self.ttype[op][lt][rt]

        if is_scalar(lt) and is_scalar(rt):
            if lt == "string" or rt == "string":
                if op == "+" and lt == "string" and rt == "string":
                    return "string"
                self.error(f"Unsupported op '{op}' for strings", node)
                return None
            if lt == "bool" or rt == "bool":
                self.error(f"Unsupported numeric op '{op}' for bool", node)
            res = self._promote_numeric(lt, rt)
            if res is None:
                self.error(f"Type mismatch: {tstr(lt)} {op} {tstr(rt)}", node)
            return res

        if is_matrix(lt) and is_matrix(rt):
            if op not in {"+", "-", "*", "/",
                          ".+", ".-", ".*", "./"}:
                self.error(f"Unsupported matrix op '{op}'", node)
            if self._matrix_broadcast(lt, rt):
                self.info(f"Matrixes can boradcast together {tstr(lt)} {op} {tstr(rt)}", node)
            if not self._same_shape(lt, rt):
                self.error(f"Shape mismatch for '{op}': {tstr(lt)} {op} {tstr(rt)}", node)
            le = base_elem(lt)
            re = base_elem(rt)
            if not (is_numeric(le) and is_numeric(re)):
                self.error(
                    f"Matrix elements must be numeric for '{op}', got {tstr(le)} and {tstr(re)}",
                    node,
                )
            elem_res = self._promote_numeric(le, re)
            if elem_res is None:
                self.error(f"Type mismatch in elements: {tstr(le)} {op} {tstr(re)}", node)
            r, c = total_shape(lt)
            return matrix_t(elem_res, r, c)

        if is_matrix(lt) and is_scalar(rt):
            le = base_elem(lt)
            if not (is_numeric(le) and is_numeric(rt)):
                self.error(
                    f"Unsupported op '{op}' between {tstr(lt)} and {tstr(rt)}",
                    node,
                )
            elem_res = self._promote_numeric(le, rt)
            if elem_res is None:
                self.error(f"Type mismatch: {tstr(lt)} {op} {tstr(rt)}", node)
            r, c = total_shape(lt)
            return matrix_t(elem_res, r, c)

        if is_scalar(lt) and is_matrix(rt):
            re = base_elem(rt)
            if not (is_numeric(lt) and is_numeric(re)):
                self.error(
                    f"Unsupported op '{op}' between {tstr(lt)} and {tstr(rt)}",
                    node,
                )
            elem_res = self._promote_numeric(lt, re)
            if elem_res is None:
                self.error(f"Type mismatch: {tstr(lt)} {op} {tstr(rt)}", node)
            r, c = total_shape(rt)
            return matrix_t(elem_res, r, c)

        self.error(
            f"No rule for binary op '{op}' with {tstr(lt)} and {tstr(rt)}",
            node,
        )
        return None

    def check_assign(self, op, ltype, rtype, node):
        if op == "=":
            if ltype != rtype:
                self.error(f"Cannot assign {tstr(rtype)} to {tstr(ltype)}", node)
            return ltype
        if op.endswith("="):
            res = self.check_binop(op[:-1], ltype, rtype, node)
            if res != ltype:
                self.error(
                    f"Result of '{op}' ({tstr(res)}) not assignable to {tstr(ltype)}",
                    node,
                )
            return ltype
        self.error(f"Unknown assignment operator '{op}'", node)
        return ltype

    def expect_bool(self, ty, ctx, node):
        if ty != "bool":
            self.error(f"Expected bool in {ctx}, got {tstr(ty)}", node)

    def visit_Statements(self, node: AST.Statements):
        last = None
        for s in node.statements:
            last = self.visit(s)
        return last

    def visit_Block(self, node: AST.Block):
        parent = self.st
        self.st = parent.fork(in_loop=parent.in_loop)
        try:
            last = None
            for s in node.statements:
                last = self.visit(s)
            return last
        finally:
            self.st = parent

    def visit_Variable(self, node: AST.Variable):
        return self.st.get(node.name)

    def visit_Literal(self, node: AST.Literal):
        return node.typename

    def visit_UnaryExpr(self, node: AST.UnaryExpr):
        t = self.visit(node.expr)
        return self.check_unary(node.op, t, node)

    def visit_OpExpr(self, node: AST.OpExpr):
        lt = self.visit(node.left)
        rt = self.visit(node.right)
        return self.check_binop(node.op, lt, rt, node)

    def visit_Assign(self, node: AST.Assign):
        rtype = self.visit(node.expr)

        if isinstance(node.lvalue, AST.Variable):
            name = node.lvalue.name
            ltype = self.st.get(name)
            if ltype is None:
                self.st.put(name, rtype)
                ltype = rtype
            result = self.check_assign(node.operator, ltype, rtype, node)
            self.st.set(name, result)
            return result

        if isinstance(node.lvalue, AST.MatrixIndex):
            ltype = self.visit(node.lvalue)
            result = self.check_assign(node.operator, ltype, rtype, node)
            return result

        self.error("Invalid assignment target", node)

    def visit_Matrix(self, node: AST.Matrix):
        if node.rows is None or not node.rows or not node.rows[0]:
            return matrix_t("float", 0, 0)
        row_types = []
        for row in node.rows:
            elem_ts = [self.visit(e) for e in row]
            row_types.append(elem_ts)

        n_rows = len(row_types)
        n_cols = len(row_types[0])

        for r in row_types:
            if len(r) != n_cols:
                self.error("Jagged matrix literal (rows with different lengths)", node)

        elem_t = row_types[0][0]
        for r in row_types:
            for t in r:
                if t != elem_t:
                    self.error(
                        f"Inconsistent element types in matrix: {tstr(elem_t)} vs {tstr(t)}",
                        node,
                    )

        return matrix_t(elem_t, n_rows, n_cols)

    def visit_MatrixIndex(self, node: AST.MatrixIndex):
        mt = self.st.get(node.matrix.name)

        if not is_matrix(mt):
            self.error(
                f"Indexing only supported for matrices, got {tstr(mt)}",
                node,
            )
            return None

        shape = mat_shape(mt)
        indices = node.indices
        if len(indices) != len(shape):
            self.error(
                f"Wrong number of indices for matrix {node.matrix.name}: "
                f"expected {len(shape)}, got {len(indices)}",
                node,
            )

        for dim, (idx_expr, dim_size) in enumerate(zip(indices, shape)):
            idx_t = self.visit(idx_expr)
            if idx_t != "int":
                self.error(
                    f"Index {dim} for {node.matrix.name} must be int, "
                    f"got {tstr(idx_t)}",
                    idx_expr,
                )

            if isinstance(idx_expr, AST.Literal) and idx_expr.typename == "int":
                idx_val = idx_expr.value
                if dim_size is not None and idx_val >= dim_size:
                    self.error(
                        f"Index {idx_val} out of bounds for dimension {dim} "
                        f"of matrix {node.matrix.name} (size {dim_size})",
                        idx_expr,
                    )

        return base_elem(mt)

    def visit_Transpose(self, node: AST.Transpose):
        mt = self.visit(node.matrix)
        return self._transpose_type(mt, node)

    def visit_Range(self, node: AST.Range):
        st = self.visit(node.start)
        en = self.visit(node.end)
        sp = self.visit(node.step) if node.step is not None else None
        if st != en:
            self.error(
                f"Type mismatch in range bounds: {tstr(st)} vs {tstr(en)}",
                node,
            )
        if sp is not None and sp != st:
            self.error(
                f"Type mismatch in range step: {tstr(st)} vs {tstr(sp)}",
                node,
            )
        return range_t(st)

    def visit_For(self, node: AST.For):
        rng_t = self.visit(node._range)
        if not is_range(rng_t):
            self.error(f"FOR expects a range, got {tstr(rng_t)}", node)
        self.st.in_loop = True
        try:
            self.st.put(node.var.name, rng_t[1])
            return self.visit(node.statement)
        finally:
            self.st.in_loop = False

    def visit_While(self, node: AST.While):
        cond_t = self.visit(node.condition)
        self.expect_bool(cond_t, "while condition", node)
        self.st.in_loop = True
        try:
            return self.visit(node.block)
        finally:
            self.st.in_loop = False

    def visit_If(self, node: AST.If):
        cond_t = self.visit(node.condition)
        self.expect_bool(cond_t, "if condition", node)
        then_t = self.visit(node.block) if node.block else None
        else_t = self.visit(node._else) if node._else else None
        if else_t is None:
            return then_t
        return then_t if then_t == else_t else None

    def visit_Print(self, node: AST.Print):
        for e in node.printlist:
            _ = self.visit(e)
        return "void"

    def visit_Return(self, node: AST.Return):
        return self.visit(node.value) if node.value is not None else "void"

    def visit_Break(self, node: AST.Break):
        if not self.st.in_loop:
            self.error('Break outside of the "while" or "for" loop', node)
        return "void"

    def visit_Continue(self, node: AST.Continue):
        if not self.st.in_loop:
            self.error('Continue outside of the "while" or "for" loop', node)
        return "void"

    def visit_Apply(self, node: AST.Apply):
        fname = node.ref
        if fname not in self.functions and fname not in self.ttype.keys():
            self.error(f"Unknown function '{fname}'", node)
        if fname in self.functions:
            _, builder = self.functions[fname]

            if len(node.args) < 1 or len(node.args) > 2:
                self.error(
                    f"Function '{fname}' expects 1 or 2 args, got {len(node.args)}",
                    node,
                )

            arg_types = [self.visit(a) for a in node.args]
            for i, got in enumerate(arg_types):
                if got != "int":
                    self.error(
                        f"Argument {i} of '{fname}' expected int, got {tstr(got)}",
                        node.args[i],
                    )

            def _dim(a):
                return a.value if isinstance(a, AST.Literal) and a.typename == "int" else None
            args = [_dim(a) for a in node.args]

            if fname == "eye" and len(args) == 2:
                r, c = args
                if r is not None and c is not None and r != c:
                    self.error(
                        f"eye expects a square shape, got {r}x{c}",
                        node,
                    )

            if len(args) == 1:
                if fname == "eye":
                    return matrix_t("float", args[0], args[0])
                return matrix_t("float", args[0], 1)
            
            return builder(args[0], args[1])

        else:
            if len(node.args) != 2:
                self.error(f"Operator '{fname}' expects 2 args, got {len(node.args)}", node)
            lt = self.visit(node.args[0])
            rt = self.visit(node.args[1])
            return self.check_binop(fname, lt, rt, node)
