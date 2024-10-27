from intbase import InterpreterBase, ErrorType
from brewparse import parse_program
from env_v1 import EnvironmentManager
from type_v1 import Type, Value, create_value, get_printable


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)   # call InterpreterBase's constructor
        self.trace_output = trace_output
        self.variables = {}

    def run(self, program):
        """
        Parses the program, finds the main function, and runs it.
        """
        ast = parse_program(program)   
        self.__set_up_function_table(ast)
        self.__get_func_by_name
        main_func = self.__get_func_by_name("main")
        self.__run_statement(main_func.get("statements"))


    def __set_up_function_table(self, ast):
        self.func_name_to_ast = {}
        for func_def in ast.get("functions"):
            self.func_name_to_ast[func_def.get("name")] = func_def
    
    def __get_func_by_name(self, name):
        if name not in self.func_name_to_ast:
            super().error(ErrorType.NAME_ERROR, f"Function {name} not found")
        return self.func_name_to_ast[name]
                
    def __run_statement(self, statements):
        """
        Interprets different types of statements: variable definition, assignment, or function call.
        """
        for statement in statements:
            statement_type = statement.elem_type
            if self.trace_output:
                print(statement)
            if statement_type == InterpreterBase.VAR_DEF_NODE:
                self.do_definition(statement)
            elif statement_type == '=':
                self.do_assignment(statement)
            elif statement_type == InterpreterBase.FCALL_NODE:
                self.do_func_call(statement)
            else:
                print("Invalid Statement Type Error") # SO WHAT HERE?
    
    def do_definition(self, statement):
        """
        Add variable to dictionary once defined 
        """
        var_name = statement.get('name')
        if var_name in self.variables:
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} has already been defined :(")
        self.variables[var_name] = None

    def do_assignment(self, statement):
        """
        Assigns a value to a variable if it exists.
        """
        var_name = statement.get('name')
        if var_name in self.variables:
            expression = statement.get('expression')
            source_node = self.get_expression_node(expression) 
            self.variables[var_name] = source_node
        else:
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} is not defined")
        
    def get_expression_node(self, expression):
        """
        Evaluates an expression node and returns its value.
        """
        elem_type = expression.elem_type

        # Handling variable expression
        if elem_type ==  'var':
            variable = expression.get('name')
            if variable not in self.variables:
                super().error(ErrorType.NAME_ERROR, f"Variable {variable} is not defined")
            variable_value = self.variables[variable]
            # Recursively evaluate the variable's value if it's an expression (This line is from ChatGPT)
            return self.get_expression_node(variable_value) if isinstance(variable_value, dict) else variable_value
        
        # Handling values
        elif elem_type == 'int' or expression.elem_type == 'string':
            return expression.get('val')
        
        # Handling operations
        elif elem_type == '+' or elem_type == '-' or elem_type == '*' or elem_type == '/':
            operand1 = self.get_expression_node(expression.get('op1'))
            operand2 = self.get_expression_node(expression.get('op2'))
            if isinstance(operand1, int) and isinstance(operand2, int):
                if elem_type == '+':
                    return operand1 + operand2
                elif elem_type == '-':
                    return operand1 - operand2
                elif elem_type == '*':
                    return operand1 * operand2
                elif elem_type == '/':
                    return operand1 // operand2
                else:
                    super().error(ErrorType.NAME_ERROR, f"Operand {elem_type} is not defined")
            else:
                    super().error(ErrorType.TYPE_ERROR, f"Invalid Types")
        # Handling Functions
        elif elem_type == 'fcall':
            return self.do_func_call(expression)       
        else:
            raise ValueError(f"Unsupported expression type: {elem_type}") 


    def do_func_call(self, statement):
        """
        Handles function calls for built-in functions.
        """
        function_name = statement.get('name')
        if function_name == 'print':
            self.print_func(statement.get('args'))
        elif function_name == 'inputi':
            return self.input_func(statement.get('args'))
        else:
            super().error(ErrorType.NAME_ERROR, f"Function {function_name} has not been defined")
        
    def print_func(self, args):
        """
        Prints a concatenated string of arguments to the console.
        """
        print_statement = [self.get_expression_node(arg) for arg in args]
        sentence = ''.join(str(item) for item in print_statement) 
        sentence += '\n'
        super().output(sentence)

    def input_func(self, args):
        """
        Simulates user input and returns the user input as an integer.
        """
        if len(args) == 0:
            user_input = int(super().get_input())
        elif len(args) == 1:
            super().output(self.get_expression_node(args[0]))
            user_input = int(super().get_input())
        else:
            super().error(ErrorType.NAME_ERROR, f"Input function accepts at most one parameter")
        return user_input