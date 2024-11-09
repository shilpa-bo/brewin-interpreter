from intbase import InterpreterBase, ErrorType
from brewparse import parse_program
from env_v1 import EnvironmentManager
from type_v1 import Type, Value, create_value, get_printable

class Interpreter(InterpreterBase):

    # constants
    BIN_OPS = {"+", "-", "*", '/', '==', '!=', '&&', '||', '<=', '<', '>', '>='}
    UNARY_OPS = {'!', 'neg'}
    FUNCTION_FLAG = False

    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)   # call InterpreterBase's constructor
        self.trace_output = trace_output
        self.__setup_ops()
        self.return_value = None
        self.program_running = False

    def run(self, program):
        """
        Parses the program, finds the main function, and runs it.
        """
        ast = parse_program(program)   
        self.__set_up_function_table(ast)
        self.__get_func_by_name
        main_func = self.__get_func_by_name("main")
        self.program_running = True
        self.env = EnvironmentManager() # using environment manager to handle variables
        self.__run_statement(main_func.get("statements"))


    def __set_up_function_table(self, ast):
        self.func_name_to_ast = {}
        for func_def in ast.get("functions"):
            func_signature = self.__generate_function_signature(func_def)
            self.func_name_to_ast[func_signature] = func_def

    
    def __generate_function_signature(self, function_ast):
        func_signature = function_ast.get("name")
        for _ in range (len(function_ast.get("args"))):
            func_signature += "_*" 
        return func_signature

    def __get_func_by_name(self, name):
        if name not in self.func_name_to_ast:
            super().error(ErrorType.NAME_ERROR, f"Function {name} not found")
        return self.func_name_to_ast[name]
                
    def __run_statement(self, statements, function_flag=False):
        if function_flag: Interpreter.FUNCTION_FLAG = True
        for statement in statements:
            if self.return_value is not None:
                return  # Stop executing further statements

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
                self.__eval_for_loop(statement)
            elif statement_type == Interpreter.RETURN_NODE:
                self.__eval_return(statement)
                return 
            else:
                print("Invalid Statement Type Error")  # Error handling
        Interpreter.FUNCTION_FLAG = False
    
    def __do_definition(self, statement):
        """
        Add variable to dictionary once defined 
        """
        var_name = statement.get('name')
        if not self.env.create(var_name, Value(Type.INT, 0)):
            super().error(
                ErrorType.NAME_ERROR, f"Variable {var_name} has already been defined :("
            )

    def __do_assignment(self, statement):
        """
        Assigns a value to a variable if it exists.
        """
        var_name = statement.get('name')
        value_obj = self.__get_expression_node(statement.get("expression"))
        if not self.env.set(var_name, value_obj, Interpreter.FUNCTION_FLAG):
            super().error(
                ErrorType.NAME_ERROR, f"Undefined variable {var_name} in assignment"
            )

    def __get_expression_node(self, expression):
        """
        Evaluates an expression node and returns its value.
        """
        elem_type = expression.elem_type
        if elem_type == InterpreterBase.INT_NODE:
            return Value(Type.INT, expression.get("val"))
        if elem_type == InterpreterBase.STRING_NODE:
            return Value(Type.STRING, expression.get("val"))
        if elem_type == InterpreterBase.BOOL_NODE:
            return Value(Type.BOOL, expression.get("val"))
        if elem_type == InterpreterBase.NIL_NODE:
            return Value(Type.NIL, expression.get("val"))
        if elem_type == InterpreterBase.VAR_NODE:
            var_name = expression.get('name')
            val = self.env.get(var_name, Interpreter.FUNCTION_FLAG)
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
            return self.__eval_for_loop(expression)
        if elem_type == InterpreterBase.RETURN_NODE:
            return self.__eval_return(expression)
            
        
    def __eval_bin_op(self, expression):
        elem_type = expression.elem_type
        operand1 = self.__get_expression_node(expression.get('op1'))
        operand2 = self.__get_expression_node(expression.get('op2'))
        if elem_type != '==' and elem_type != '!=':
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
        Interpreter.FUNCTION_FLAG = False

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

    
    def __eval_for_loop(self, expression):
        elem_type = expression.elem_type
        Interpreter.FUNCTION_FLAG = False

        self.__do_assignment(expression.get('init'))

        condition = self.__get_expression_node(expression.get('condition'))
        if condition.type() != Type.BOOL: 
            super().error(
                ErrorType.TYPE_ERROR,
                f"{elem_type} statement condition must be a boolean"
            )

        while condition.value():
            self.env.push_scope()
            
            # Run the loop statements
            self.__run_statement(expression.get('statements'))
            
            # Pop the scope for this iteration, removing inner loop variables
            self.env.pop_scope()

            self.__do_assignment(expression.get('update'))
            condition = self.__get_expression_node(expression.get('condition'))

    def __eval_return(self, statement):
        expression = statement.get("expression")
        if not expression:
            self.return_value = Type.NIL
            return
        self.return_value = self.__get_expression_node(expression)
        
    def __do_func_call(self, statement):
        if statement.get('name') == 'print':
            self.__print_func(statement)
            return Value(Type.NIL)
        elif statement.get('name') == 'inputi' or statement.get('name') == 'inputs':
            return self.__input_func(statement)

        # Prepare for function call
        func_sig = self.__generate_function_signature(statement)
        if func_sig not in self.func_name_to_ast:
            super().error(ErrorType.NAME_ERROR, f"Function {func_sig} has not been defined")

        func_ast = self.func_name_to_ast[func_sig]
        args = statement.get("args")
        params = func_ast.get("args")

        # Set up a new function scope
        self.env.push_scope()
        # i need a return value per scope
        self.return_value = None

        # Assign arguments to parameters
        for param, arg_expr in zip(params, args):
            arg_value = self.__get_expression_node(arg_expr)
            param_name = param.get("name")
            self.env.create(param_name, arg_value)

        # Execute the function body
        self.__run_statement(func_ast.get("statements"))

        # Capture and return the return_value if set
        result = self.return_value if self.return_value is not None else Value(Type.NIL)
        self.return_value = None
        self.env.pop_scope()
        
        return result  # Pass result back to caller
    
    def __print_func(self, print_ast):
        args = print_ast.get('args')
        print_statement = [get_printable(self.__get_expression_node(arg)) for arg in args]
        output = ''.join(str(item) for item in print_statement)  
        super().output(output)

    def __input_func(self, call_ast):
        args = call_ast.get("args")
        if args is not None and len(args) == 1:
            result = self.__get_expression_node(args[0])
            super().output(get_printable(result))
        elif args is not None and len(args) > 1:
            super().error(
                ErrorType.NAME_ERROR, "No inputi() function that takes > 1 parameter"
            )
        inp = super().get_input()
        if call_ast.get("name") == "inputi":
            return Value(Type.INT, int(inp))
        if call_ast.get("name") == "inputs":
            return Value(Type.STRING, inp)
        
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

        # ADD STRICT EVALUATION
        self.op_to_lambda[Type.BOOL]["&&"] = lambda x, y: Value(x.type(), (x.value() and y.value()) and (y.value() and x.value()))
        self.op_to_lambda[Type.BOOL]["||"] = lambda x, y: Value(x.type(), (x.value() or y.value()) or (y.value() or x.value()))

        # Set up operations for nil
        self.op_to_lambda[Type.NIL] = {}
        self.op_to_lambda[Type.NIL]["=="] = lambda x, y: Value(Type.BOOL, y.type() == Type.NIL)
        self.op_to_lambda[Type.NIL]["!="] = lambda x, y: Value(Type.BOOL, y.type() != Type.NIL)
