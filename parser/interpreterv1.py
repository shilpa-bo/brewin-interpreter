from intbase import InterpreterBase, ErrorType
from brewparse import parse_program

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)   # call InterpreterBase's constructor
        self.trace_output = trace_output
        self.variables = {}

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
        # why are we only running statements here?
        # Execution starts on the very first statement inside of main() and proceeds from top to bottom
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
        # definition
        # add variable to the dictionary holding all variables
        # un initialized, so value should be None
        self.variables[statement.get('name')] = None

    def do_assignment(self, statement):

        if statement.get('name') in self.variables:
            expression = statement.get('expression') # get expression node, variable, or value
            source_node = self.get_expression_node(expression) # parse the expression node accordingly
            self.variables[statement.get('name')] = source_node
        else:
            super().error(ErrorType.NAME_ERROR, f"Variable {statement.get('name')} is not defined")
        
        print("Assignment84", statement, self.variables)

    def get_expression_node(self, expression):
        print('87', expression.elem_type)

        # Handling variable expression
        if expression.elem_type ==  'var':
            variable = expression.get('name')
            if variable not in self.variables:
                super().error(ErrorType.NAME_ERROR, f"Variable {variable} is not defined")
            variable_value = self.variables[variable]
            # Recursively evaluate the variable's value if it's an expression (This line is from ChatGPT)
            return self.get_expression_node(variable_value) if isinstance(variable_value, dict) else variable_value
        
        # Handling values
        elif expression.elem_type == 'int' or expression.elem_type == 'string':
            return expression.get('val')
        
        # Handling operations
        elif expression.elem_type == '+' or expression.elem_type == '-':
            operand1 = self.get_expression_node(expression.get('op1'))
            operand2 = self.get_expression_node(expression.get('op2'))
            if expression.elem_type == '+':
                return operand1 + operand2
            else:
                return operand1 - operand2
        elif expression.elem_type == 'fcall':
            return self.do_func_call(expression)       
        else:
            print(expression.elem_type)
            raise ValueError(f"Unsupported expression type: {expression.elem_type}") 


    def do_func_call(self, statement):
        print("Function Call108", statement)
        """
        If name is print then do something? 
        then call print_func
        """
        function_name = statement.get('name')
        if function_name == 'print':
            self.print_func(statement.get('args'))
        elif function_name == 'inputi':
            return self.input_func(statement.get('args'))
        else:
            super().error(ErrorType.NAME_ERROR, f"Function {function_name} has not been defined")
        
    def print_func(self, args):
        # Do something
        # do we care if elem_type is var or should we have already dealt with this?
        # do we differentiate between strings, int, var?
        print_statement = [self.get_expression_node(arg) for arg in args]
        sentence = ' '.join(str(item) for item in print_statement)
        print("121", sentence)
        super().output(sentence)

    def input_func(self, args):
        # only integers are inputted- need to convert to an int
        # we return user input?
        if len(args) == 0:
            user_input = int(super().get_input())
        elif len(args) == 1:
            super().output(self.get_expression_node(args[0]))
            user_input = int(super().get_input())
        else:
            super().error(ErrorType.NAME_ERROR, f"No inputi() function found that takes > 1 parameter")
        return user_input