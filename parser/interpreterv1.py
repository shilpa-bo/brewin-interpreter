from intbase import InterpreterBase, ErrorType
from brewparse import parse_program

# I must use the base class some how
# Each Node contains a elem_type object indicating the type of node
class Node:
    def __init__(self, elem_type):
        self.elem_type = elem_type

# A Program node represents the overall program
class Program(Node):
    def __init__(self, functions):
        super().__init__('program')
        self.dict = {'functions' : functions}
        # self.dict which holds a single key 'functions' which maps to a list of Function Definition nodes
class Function(Node):
    def __init__(self, name, statements):
        super().__init__('func')
        self.dict = {'name' : name, 'statements' : statements}

# A Statement node represents an individual statement
# Variable, Definition, an Assignment, or a Function Call
class Statement(Node):
    def __init__(self, elem_type):
        super().__init__(elem_type)

class Variable(Statement):
    def __init__(self, name):
        super().__init__('vardef')
        self.dict = {'name': name}
    
class Assignment(Statement):
    def __init__(self, name, expression):
        super().__init__('=')
        self.dict = {'name' : name, 'expression': expression}

class Function(Statement):
    def __init__(self, name, args):
        super().__init__('fcall')
        self.dict = {'name' : name, 'args': args}

# An Expression node represents an individual expression
# Two types: binary operation, function call
class Expression(Node):
    def __init__(self, elem_type):
        super().__init__(elem_type)

class BinaryOp(Expression):
    def __init__(self, elem_type, op1, op2):
        super().__init__(elem_type)
        self.dict = {'op1': op1, 'op2': op2}
        # should I pass self.dict down?
class SumOp(BinaryOp):
    def __init__(self, op1, op2):
        super().__init__('+', op1, op2) 
class DiffOp(BinaryOp):
    def __init__(self, op1, op2):
        super().__init__('-', op1, op2)

# can change to Function once I modulize
class ExpFunction(Expression):
    def __init__(self, name, args):
        super().__init__('fcall')
        self.dict = {'name' : name, 'args' : args}

# A Variable node represents an individual variable that's refferred to in an expression
class Variable(Node):
    def __init__(self, name):
        super().__init__('var')
        self.dict = {'name' : name}

# Value nodes: represent integers or string values
class Value(Node):
    def __init__(self, elem_type, val):
        super().__init__(elem_type)
        self.dict = {'val' : val}
class Int(Node):
    def __init__(self, val):
        super().init('int', val)
class Str(Node):
    def __init__(self, val):
        super().__init__('string', val)

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)   # call InterpreterBase's constructor

    def interpret_statement(self, statement):
        if self.trace_output == True:
            print(statement)

    def get_main_func_node(self, ast):
        """
        Gets main func node if exists else returns error
        """
        for func in ast.get('functions'):
            if func.get('name') == 'main':
                return func
        # function will only come here if we didn't find a main
        super().error(
            ErrorType.NAME_ERROR,
            "No main() function was found"
        )
        
    def run(self, program):
        ast = parse_program(program)   
        # Get the list of functions from the AST- main, make this shorter
        main_func_node = self.get_main_func_node(ast)
        self.run_func(main_func_node)
        # need some dict to hold variables
        
    def run_func(self, func_node):
        for statement in func_node.get('statements'):
            self.run_statement(statement)

    def run_statement(self, statement):
        # depending on the statement call: do something else
        """
        Statements can be:
            variable definition: vardef
            assignment: =
            function call: fcall
        """
        statement_type = statement.elem_type
        if statement_type == 'vardef':
            self.do_definition(statement)
        elif statement_type == '=':
            self.do_assignment(statement)
        elif statement_type == 'fcall':
            self.do_func_call(statement)
        else:
            print("Invalid Statement Type Error") # most likely
    
    def do_definition(self, statement):
        print("Defintition", statement)

    def do_assignment(self, statement):
        print("Assignment", statement)

    def do_func_call(self, statement):
        print("Function Call", statement)

    