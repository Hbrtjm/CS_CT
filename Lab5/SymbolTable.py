#!/usr/bin/python

from AST import Node

class VariableSymbol(Node):
    def __init__(self, name, _type):
        self.name = name
        self._type = _type
        self.value = None

class SymbolTable(object):
    def __init__(self, depth=0, in_loop=False, parent=None, name="global"):
        self.symbol_table = {}
        self.depth = depth
        self.in_loop = in_loop
        self.parent = parent
        self.name = name

    def put(self, name, symbol):
        self.symbol_table[name] = symbol

    def get(self, name):
        if name in self.symbol_table:
            return self.symbol_table[name]
        if self.parent is not None:
            return self.parent.get(name)
        return None

    def set(self, name, value):
        self.symbol_table[name] = value

    def getParentScope(self):
        return self.parent

    def pushScope(self, name):
        return SymbolTable(self, name)

    def popScope(self):
        return self.parent

    def fork(self, in_loop=False):
        return SymbolTable(self.depth + 1, in_loop, self, self.name)
    
    def namedFork(self, name, in_loop=False):
        return SymbolTable(self.depth + 1, self, name)