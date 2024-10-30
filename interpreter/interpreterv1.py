from intbase import InterpreterBase, ErrorType
from brewparse import parse_program
from env_v1 import EnvironmentManager
from type_v1 import Type, Value, create_value, get_printable
import copy

class Interpreter(InterpreterBase):

    # constants
    BIN_OPS = {"+", "-", "*", '/', '==', '!=', '&&', '||', '<=', '<', '>', '>='}
    UNARY_OPS = {'!', 'neg'}

    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)   # call InterpreterBase's constructor
        self.trace_output = trace_output
        self.__setup_ops()

    def run(self, program):
        """
        Parses the program, finds the main function, and runs it.
        """
        ast = parse_program(program)   
        self.__set_up_function_table(ast)
        self.__get_func_by_name
        main_func = self.__get_func_by_name("main")
        self.env = EnvironmentManager() # using environment manager to handle variables
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
                self.__do_definition(statement)
            elif statement_type == '=':
                self.__do_assignment(statement)
            elif statement_type == InterpreterBase.FCALL_NODE:
                self.__do_func_call(statement)
            elif statement_type == InterpreterBase.IF_NODE:
                self.__eval_if(statement)
            elif statement_type == Interpreter.FOR_NODE:
                self.__eval_4loop(statement)
            else:
                print("Invalid Statement Type Error") # SO WHAT HERE?
    
    def __do_definition(self, statement):
        """
        Add variable to dictionary once defined 
        """
        var_name = statement.get('name')
        if not self.env.create(var_name, Value(Type.INT, 0)):
            super().error(
                ErrorType.NAME_ERROR, f"Variable {var_name} has already been defined :("
            )
        # print(f"Debug: Defined variable '{var_name}' with initial value 0")

    def __do_assignment(self, statement):
        """
        Assigns a value to a variable if it exists.
        """
        var_name = statement.get('name')
        value_obj = self.__get_expression_node(statement.get("expression"))
        if not self.env.set(var_name, value_obj):
            super().error(
                ErrorType.NAME_ERROR, f"Undefined variable {var_name} in assignment"
            )

    def __get_expression_node(self, expression):
        """
        Evaluates an expression node and returns its value.
        """
        elem_type = expression.elem_type
        if elem_type == InterpreterBase.INT_NODE:
            # print(f"Debug: Evaluated INT_NODE, result={Value(Type.INT, expression.get("val"))}")
            return Value(Type.INT, expression.get("val"))
        if elem_type == InterpreterBase.STRING_NODE:
            # print(f"Debug: Evaluated STRING_NODE, result={Value(Type.STRING, expression.get("val"))}")
            return Value(Type.STRING, expression.get("val"))
        if elem_type == InterpreterBase.BOOL_NODE:
            return Value(Type.BOOL, expression.get("val"))
        if elem_type == InterpreterBase.NIL_NODE:
            return Value(Type.NIL)
        if elem_type == InterpreterBase.VAR_NODE:
            var_name = expression.get('name')
            val = self.env.get(var_name)
            if not val:
                super().error(ErrorType.NAME_ERROR, f"Variable {var_name} is not defined")
            return val
        if elem_type in Interpreter.BIN_OPS:
            return self.__eval_bin_op(expression)
        if elem_type in Interpreter.UNARY_OPS:
            return self.__eval_unary_op(expression)
        if elem_type == InterpreterBase.FCALL_NODE:
            return self.__do_func_call(expression)        
        if elem_type == InterpreterBase.IF_NODE:
            return self.__eval_if(expression)
        if elem_type == InterpreterBase.FOR_NODE:
            return self.__eval_4loop(expression)

    def __eval_bin_op(self, expression):
        elem_type = expression.elem_type
        operand1 = self.__get_expression_node(expression.get('op1'))
        operand2 = self.__get_expression_node(expression.get('op2'))
        if operand1.type() != operand2.type():
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible types for {elem_type} operation",
            )
        if elem_type not in self.op_to_lambda[operand1.type()]:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible operator {elem_type} for type {operand1.type()}",
            )
        f = self.op_to_lambda[operand1.type()][elem_type]
        return f(operand1, operand2)
    
    def __eval_unary_op(self, expression):
        elem_type = expression.elem_type
        operand = self.__get_expression_node(expression.get('op1'))
        if elem_type not in self.op_to_lambda[operand.type()]:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible operator {elem_type} for type {operand.type()}",
            )
        f = self.op_to_lambda[operand.type()][elem_type]
        return f(operand)

    def __eval_if(self, expression):
        # Create new environment
        self.env.push_scope()

        elem_type = expression.elem_type 
        condition = self.__get_expression_node(expression.get('condition')) # maybe function?
        if condition.type() != Type.BOOL: 
            super().error(
                ErrorType.TYPE_ERROR,
                f"{elem_type} statement condition must be a boolean"
            )
        if condition.value():
            self.__run_statement(expression.get('statements'))
        else:
            if expression.get('else_statements'):
                self.__run_statement(expression.get('else_statements'))
        
        # reset environment
        self.env.pop_scope()

    
    def __eval_4loop(self, expression):
        elem_type = expression.elem_type # if

        # initialize
        self.__do_assignment(expression.get('init'))

        # check condition initially
        condition = self.__get_expression_node(expression.get('condition'))

        if condition.type() != Type.BOOL: 
            super().error(
                ErrorType.TYPE_ERROR,
                f"{elem_type} statement condition must be a boolean"
        )
        self.env.push_scope()
        while condition.value():
            self.__run_statement(expression.get('statements'))
            
            self.__do_assignment(expression.get('update'))
            
            condition = self.__get_expression_node(expression.get('condition'))
        self.env.pop_scope()


    def __do_func_call(self, statement):
        """
        Handles function calls for built-in functions.
        """
        function_name = statement.get('name')
        if function_name == 'print':
            self.__print_func(statement)
        elif function_name == 'inputi':
            return self.__input_func(statement)
        else:
            super().error(ErrorType.NAME_ERROR, f"Function {function_name} has not been defined")
        
    def __print_func(self, print_ast):
        args = print_ast.get('args')
        print_statement = [get_printable(self.__get_expression_node(arg)) for arg in args]
        output = ''.join(str(item) for item in print_statement)  
        super().output(output)

    def __input_func(self, call_ast):
        args = call_ast.get("args")
        if args is not None and len(args) == 1:
            result = self.__eval_expr(args[0])
            super().output(get_printable(result))
        elif args is not None and len(args) > 1:
            super().error(
                ErrorType.NAME_ERROR, "No inputi() function that takes > 1 parameter"
            )
        inp = super().get_input()
        if call_ast.get("name") == "inputi":
            return Value(Type.INT, int(inp))

    def __setup_ops(self):
        self.op_to_lambda = {}
        
        # Set up operations for integers
        self.op_to_lambda[Type.INT] = {}
        self.op_to_lambda[Type.INT]["+"] = lambda x, y: Value(x.type(), x.value() + y.value())
        self.op_to_lambda[Type.INT]["-"] = lambda x, y: Value(x.type(), x.value() - y.value())
        self.op_to_lambda[Type.INT]["*"] = lambda x, y: Value(x.type(), x.value() * y.value())
        self.op_to_lambda[Type.INT]["/"] = lambda x, y: Value(x.type(), x.value() // y.value())
        self.op_to_lambda[Type.INT]["=="] = lambda x, y: Value(Type.BOOL, x.value() == y.value())
        self.op_to_lambda[Type.INT]["!="] = lambda x, y: Value(Type.BOOL, x.value() != y.value())
        self.op_to_lambda[Type.INT][">"] = lambda x, y: Value(Type.BOOL, x.value() > y.value())
        self.op_to_lambda[Type.INT][">="] = lambda x, y: Value(Type.BOOL, x.value() >= y.value())
        self.op_to_lambda[Type.INT]["<"] = lambda x, y: Value(Type.BOOL, x.value() < y.value())
        self.op_to_lambda[Type.INT]["<="] = lambda x, y: Value(Type.BOOL, x.value() <= y.value())
        self.op_to_lambda[Type.INT]["neg"] = lambda x: Value(x.type(), -x.value())

        # Set up operations for strings
        self.op_to_lambda[Type.STRING] = {}
        self.op_to_lambda[Type.STRING]["+"] = lambda x, y: Value(x.type(), x.value() + y.value())
        self.op_to_lambda[Type.STRING]["=="] = lambda x, y: Value(Type.BOOL, x.value() == y.value())
        self.op_to_lambda[Type.STRING]["!="] = lambda x, y: Value(Type.BOOL, x.value() != y.value())

        # Set up operations for booleans
        self.op_to_lambda[Type.BOOL] = {}
        self.op_to_lambda[Type.BOOL]["!"] = lambda x: Value(x.type(), not x.value())
        self.op_to_lambda[Type.BOOL]["=="] = lambda x, y: Value(Type.BOOL, x.value() == y.value())
        self.op_to_lambda[Type.BOOL]["!="] = lambda x, y: Value(Type.BOOL, x.value() != y.value())
        self.op_to_lambda[Type.BOOL]["&&"] = lambda x, y: Value(x.type(), x.value() and y.value())
        self.op_to_lambda[Type.BOOL]["||"] = lambda x, y: Value(x.type(), x.value() or y.value())
