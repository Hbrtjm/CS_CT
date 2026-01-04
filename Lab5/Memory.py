class Memory:
    def __init__(self, name):
        self.name = name
        self.values = {}

    def has_key(self, name):
        return name in self.values.keys()

    def get(self, name):
        if not self.has_key(name):
            raise Exception(f"Variable '{name}' not defined")
        return self.values[name]

    def put(self, name, value):
        self.values[name] = value

class MemoryStack:
    def __init__(self, memory=None):
        self.stack = [memory] if memory is not None else []

    def get(self, name):
        for memory in self.stack:
            if memory.has_key(name):
                return memory.get(name)
        raise Exception(f"Variable '{name}' not defined in any scope")

    def insert(self, name, value):
        if not self.stack:
            raise Exception("No memory scope available")
        self.stack[-1].put(name, value)

    def set(self, name, value):
        for i, memory in enumerate(self.stack):
            if memory.has_key(name):
                self.stack[i].put(name, value)
                return
        raise Exception(f"Variable '{name}' not defined")

    def push(self, memory):
        self.stack.append(memory)


    def pop(self):
        if not self.stack:
            raise Exception("Cannot pop from empty memory stack")
        return self.stack.pop()