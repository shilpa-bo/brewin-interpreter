# The EnvironmentManager class keeps a mapping between each variable (aka symbol)
# in a brewin program and the value of that variable - the value that's passed in can be
# anything you like. In our implementation we pass in a Value object which holds a type
# and a value (e.g., Int, 10).
class EnvironmentManager:
    def __init__(self):
        self.variables_stack = []
        self.variables_stack.append({})
    
    def push_scope(self):
        # print(f"Debug Stack before push: {self.variables_stack}")
        self.variables_stack.append({})
        # print(f"Debug Stack after push: {self.variables_stack}")
    
    def pop_scope(self):
        # print(f"Debug Stack before pop: {self.variables_stack}")
        self.variables_stack.pop()
        # print(f"Debug Stack when pop: {self.variables_stack}")

    # Gets the data associated a variable name
    def get(self, symbol, function_flag=False):
        # print(f"Debug Stack before pop: {self.variables_stack}")
        if function_flag:
            env = self.variables_stack[-1]
            if symbol in env:
                return env[symbol]
            return None
        # want to start looking from the top down:
        for env in reversed(self.variables_stack):
            if symbol in env:
                return env[symbol]
        return None

    # Sets the data associated with a variable name
    def set(self, symbol, value, function_flag=False):
        if function_flag:
            env = self.variables_stack[-1]
            if symbol in env:
                env[symbol] = value
                return True
            return False # symbol is not in env

        for env in reversed(self.variables_stack):
            if symbol in env:
                env[symbol] = value
                return True
        return False # symbol is not in env

    # do i make new ones for functions- where it only checks in curr scope

    def create(self, symbol, start_val):
        # print(f"Debug: in create {symbol} and {start_val.value()}")
        env = self.variables_stack[-1] # want to create variables in the innermost/current environment
        if symbol not in env: 
          env[symbol] = start_val 
          return True
        return False
