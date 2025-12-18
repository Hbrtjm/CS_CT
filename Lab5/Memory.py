"""
Memory management for the interpreter.
Provides Memory and MemoryStack classes for managing variable scopes.
"""


class Memory:
    """
    EXAMPLE: Represents a single memory scope/frame.
    Stores variable names and their values in a dictionary.
    """

    def __init__(self, name): # memory name
        self.name = name
        self.values = {}  # FIXED BUG: was missing 'self.' prefix

    def has_key(self, name):  # variable name
        """Check if a variable exists in this memory scope."""
        
        # print(f"{self} {self.values.keys()}")
        return name in self.values.keys()

    def get(self, name):         # gets from memory current value of variable <name>
        """
        EXAMPLE: Get the value of a variable from this memory scope.
        Raises exception if variable is not defined.
        """
        # print(f"Getting {name} from {self.name}")
        if not self.has_key(name):
            raise Exception(f"Variable '{name}' not defined")
        return self.values[name]

    def put(self, name, value):  # puts into memory current value of variable <name>
        """EXAMPLE: Store a variable and its value in this memory scope."""
        # print(f"Putting {name} into {self.name}")
        self.values[name] = value

class MemoryStack:
    """
    EXAMPLE: Manages a stack of memory scopes for nested blocks/functions.
    The stack allows for proper variable scoping.
    """

    def __init__(self, memory=None): # initialize memory stack with memory <memory>
        """EXAMPLE: Initialize the memory stack with optional initial memory."""
        self.stack = [memory] if memory is not None else []

    def get(self, name):             # gets from memory stack current value of variable <name>
        """
        EXAMPLE: Get a variable's value from the memory stack.
        Searches from the top of the stack (current scope) downwards.
        """
        # Search from top to bottom of stack
        for memory in self.stack:
            if memory.has_key(name):
                return memory.get(name)
        raise Exception(f"Variable '{name}' not defined in any scope")

    def insert(self, name, value): # inserts into memory stack variable <name> with value <value>
        """
        EXAMPLE: Insert a new variable into the current (top) scope.
        This creates a NEW variable in the current scope.
        """
        if not self.stack:
            raise Exception("No memory scope available")
        self.stack[-1].put(name, value)

    def set(self, name, value): # sets variable <name> to value <value>
        """
        TODO: Update an existing variable's value.

        This should search for the variable from top to bottom and update it
        in the scope where it's found. If not found, raise an exception.

        Steps:
        1. Iterate through self.stack in reverse order (from top to bottom)
        2. For each memory, check if it has_key(name)
        3. If found, call memory.put(name, value) and return
        4. If not found in any scope, raise Exception

        Example implementation:
            for memory in reversed(self.stack):
                if memory.has_key(name):
                    memory.put(name, value)
                    return
            raise Exception(f"Variable '{name}' not defined in any scope")
        """
        # TODO: Implement variable update logic
        # Current implementation only checks top scope - you need to search all scopes
        for i, memory in enumerate(self.stack):
            if memory.has_key(name):
                self.stack[i].put(name, value)
                return
        raise Exception(f"Variable '{name}' not defined")

    def push(self, memory): # pushes memory <memory> onto the stack
        """EXAMPLE: Push a new memory scope onto the stack."""
        self.stack.append(memory)


    def pop(self):          # pops the top memory from the stack
        """
        EXAMPLE: Pop the top memory scope from the stack.
        Returns the popped Memory object.
        """
        if not self.stack:
            raise Exception("Cannot pop from empty memory stack")
        return self.stack.pop()