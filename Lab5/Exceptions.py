class ReturnValueException(Exception):
    def __init__(self, value):
        self.value = value

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class RuntimeError(Exception):
    def __init__(self, message, line=None):
        self.message = message
        self.line = line
        super().__init__(self.format_message())

    def format_message(self):
        if self.line is not None:
            return f"[line {self.line}] Runtime error: {self.message}"
        return f"Runtime error: {self.message}"


class DimensionError(RuntimeError):
    pass


class TypeError(RuntimeError):
    pass


class IndexError(RuntimeError):
    pass


class UnknownOperatorError(RuntimeError):
    pass


class UnknownFunctionError(RuntimeError):
    pass


class DivisionByZeroError(RuntimeError):
    pass
