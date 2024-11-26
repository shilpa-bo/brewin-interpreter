# The EnvironmentManager class keeps a mapping between each variable name (aka symbol)
# in a brewin program and the Value object, which stores a type, and a value.
class EnvironmentManager:
    def __init__(self):
        self.environment = []
    
    def custom_copy(self):
        # DOCUMENT: Deep copy outer structure but keep references for inner scopes
        copied_env = EnvironmentManager() # create new environment (outer)
        copied_env.environment = [
            [{key: value for key, value in scope.items()} for scope in stack] for stack in self.environment
        ]
        return copied_env
    
    # DOCUMENT: Weird List comprehension:
    # Dictionary Comprehension: {key: value for key, value in scope.items()}
        # Creating a new dictionary with new key that reference to the same values objects (shallow copied dictionaries)
    # Inner List Comprehension: [{key: value for key, value in scope.items()} for scope in stack]
        # New list of shallow copied dictionaries for each stack
    # Outer List Comprehension:
        # New list of stacks which hold ^

    # returns a VariableDef object
    def get(self, symbol):
        cur_func_env = self.environment[-1]
        for env in reversed(cur_func_env):
            if symbol in env:
                return env[symbol]
        return None

    def set(self, symbol, value):
        cur_func_env = self.environment[-1]
        for env in reversed(cur_func_env):
            if symbol in env:
                env[symbol] = value
                return True
        return False

    # create a new symbol in the top-most environment, regardless of whether that symbol exists
    # in a lower environment
    def create(self, symbol, value):
        cur_func_env = self.environment[-1]
        if symbol in cur_func_env[-1]:   # symbol already defined in current scope
            return False
        cur_func_env[-1][symbol] = value
        return True

    # used when we enter a new function - start with empty dictionary to hold parameters.
    def push_func(self):
        self.environment.append([{}])  # [[...]] -> [[...], [{}]]

    def push_block(self):
        cur_func_env = self.environment[-1]
        cur_func_env.append({})  # [[...],[{....}] -> [[...],[{...}, {}]]

    def pop_block(self):
        cur_func_env = self.environment[-1]
        cur_func_env.pop() 

    # used when we exit a nested block to discard the environment for that block
    def pop_func(self):
        self.environment.pop()

    def return_env(self):
        return self.environment
