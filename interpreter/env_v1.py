# The EnvironmentManager class keeps a mapping between each variable (aka symbol)
# in a brewin program and the value of that variable - the value that's passed in can be
# anything you like. In our implementation we pass in a Value object which holds a type
# and a value (e.g., Int, 10).
class EnvironmentManager:
    def __init__(self):
        self.variables_stack = []
        self.variables_stack.append({})
    
    def push_scope(self):
        self.variables_stack.append({})
    
    def pop_scope(self):
        self.variables_stack.pop()

    # Gets the data associated a variable name
    def get(self, symbol):
        # want to start looking from the top down:
        for env in reversed(self.variables_stack):
            if symbol in env:
                return env[symbol]
        return None

    # Sets the data associated with a variable name
    def set(self, symbol, value):
        for env in reversed(self.variables_stack):
            if symbol in env:
                env[symbol] = value
                return True
        return False # symbol is not in env

    
    def create(self, symbol, start_val):
        env = self.variables_stack[-1] # want to create variables in the innermost/current environment
        if symbol not in env: 
          env[symbol] = start_val 
          return True
        return False
