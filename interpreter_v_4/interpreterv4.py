# document that we won't have a return inside the init/update of a for loop
from enum import Enum
from parser.brewparse import parse_program
from interpreter_v_4.env_v4 import EnvironmentManager
from intbase import InterpreterBase, ErrorType
from interpreter_v_4.type_v4 import Type, Value, create_value, get_printable


class ExecStatus(Enum):
    CONTINUE = 1
    RETURN = 2
    RAISE = 3

class LazyObject:
    def __init__(self, expr_ast, captured_env, eval_func):
        self.expr_ast = expr_ast
        self.captured_env = captured_env
        self.eval_func = eval_func
        self._evaluated = False
        self._value = None

    def evaluate(self):
        if not self._evaluated:
            self._value = self.eval_func(self.expr_ast, self.captured_env)
            if isinstance(self._value, tuple) and self._value[0] == ExecStatus.RAISE:
                return self._value
            self._evaluated = True
        return self._value

    def value(self):
        return self.evaluate().value()

    def type(self):
        return self.evaluate().type()


# Main interpreter class
class Interpreter(InterpreterBase):
    # constants
    NIL_VALUE = create_value(InterpreterBase.NIL_DEF)
    TRUE_VALUE = create_value(InterpreterBase.TRUE_DEF)
    BIN_OPS = {"+", "-", "*", "/", "==", "!=", ">", ">=", "<", "<=", "||", "&&"}

    # methods
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output
        self.__setup_ops()

    def run(self, program):
        ast = parse_program(program)
        self.__set_up_function_table(ast)
        self.env = EnvironmentManager()
        result = self.__call_func_aux("main", [])
        if isinstance(result, tuple) and result[0] == ExecStatus.RAISE:
            self.error(ErrorType.FAULT_ERROR, f"Unhandled exception: {result[1].value()}")


    def __set_up_function_table(self, ast):
        self.func_name_to_ast = {}
        for func_def in ast.get("functions"):
            func_name = func_def.get("name")
            num_params = len(func_def.get("args"))
            if func_name not in self.func_name_to_ast:
                self.func_name_to_ast[func_name] = {}
            self.func_name_to_ast[func_name][num_params] = func_def

    def __get_func_by_name(self, name, num_params):
        if name not in self.func_name_to_ast:
            super().error(ErrorType.NAME_ERROR, f"Function {name} not found")
        candidate_funcs = self.func_name_to_ast[name]
        if num_params not in candidate_funcs:
            super().error(
                ErrorType.NAME_ERROR,
                f"Function {name} taking {num_params} params not found",
            )
        return candidate_funcs[num_params]

    def __run_statements(self, statements):
        self.env.push_block()
        for statement in statements:
            if self.trace_output:
                print(statement)
            status, return_val = self.__run_statement(statement)
            if status == ExecStatus.RETURN or status == ExecStatus.RAISE:
                self.env.pop_block()
                return status, return_val
        self.env.pop_block()
        return (ExecStatus.CONTINUE, Interpreter.NIL_VALUE)

    def __run_statement(self, statement, env=None):
        status = ExecStatus.CONTINUE
        return_val = None
        if statement.elem_type == InterpreterBase.FCALL_NODE:
            result = self.__call_func(statement)
            if isinstance(result, tuple) and result[0] == ExecStatus.RAISE:
                status, return_val = result
        elif statement.elem_type == "=":
            self.__assign(statement)
        elif statement.elem_type == InterpreterBase.VAR_DEF_NODE:
            self.__var_def(statement)
        elif statement.elem_type == InterpreterBase.RETURN_NODE:
            status, return_val = self.__do_return(statement)
        elif statement.elem_type == Interpreter.IF_NODE:
            status, return_val = self.__do_if(statement)
        elif statement.elem_type == Interpreter.FOR_NODE:
            status, return_val = self.__do_for(statement)
        elif statement.elem_type == Interpreter.TRY_NODE:
            status, return_val = self.__do_try(statement)
        elif statement.elem_type == Interpreter.RAISE_NODE:
            status, return_val = self.__do_raise(statement)
        return (status, return_val)
    
    def __call_func(self, call_node, env=None):
        if env is None:
            env = self.env
        func_name = call_node.get("name")
        actual_args = call_node.get("args")
        return self.__call_func_aux(func_name, actual_args, env)

    def __call_func_aux(self, func_name, actual_args, env=None):
        if env is None:
            env = self.env
        if func_name == "print":
            return self.__call_print(actual_args)
        if func_name == "inputi" or func_name == "inputs":
            return self.__call_input(func_name, actual_args)

        func_ast = self.__get_func_by_name(func_name, len(actual_args))
        formal_args = func_ast.get("args")
        if len(actual_args) != len(formal_args):
            super().error(
                ErrorType.NAME_ERROR,
                f"Function {func_ast.get('name')} with {len(actual_args)} args not found",
            )

        # first evaluate all of the actual parameters and associate them with the formal parameter names
        args = {}
        for formal_ast, actual_ast in zip(formal_args, actual_args):
            # lazy evaluate parameters
            result = LazyObject(actual_ast, env.custom_copy(), self.__eval_expr)
            if isinstance(result, tuple) and result[0] == ExecStatus.RAISE:
                return result
            arg_name = formal_ast.get("name")
            args[arg_name] = result
        
        # then create the new activation record 
        self.env.push_func()
        # and add the formal arguments to the activation record
        for arg_name, value in args.items():
          self.env.create(arg_name, value)
        status, return_val = self.__run_statements(func_ast.get("statements"))
        self.env.pop_func()
        if status == ExecStatus.RAISE:
            return (status, return_val)
        return return_val

    def __call_print(self, args):
        output = ""
        for arg in args:
            result = self.__eval_expr(arg)  # result is a Value object
            # if isinstance(result, LazyObject):
            #     result = result.evaluate()
            if isinstance(result, tuple) and result[0] == ExecStatus.RAISE:
                return result
            output = output + get_printable(result)
        super().output(output)
        return Interpreter.NIL_VALUE

    def __call_input(self, name, args):
        if args is not None and len(args) == 1:
            result = self.__eval_expr(args[0])
            super().output(get_printable(result))
        elif args is not None and len(args) > 1:
            super().error(
                ErrorType.NAME_ERROR, "No inputi() function that takes > 1 parameter"
            )
        inp = super().get_input()
        if name == "inputi":
            return Value(Type.INT, int(inp))
        if name == "inputs":
            return Value(Type.STRING, inp)

    def __assign(self, assign_ast):
        var_name = assign_ast.get("name")
        # Don't want to evaluate here (lazy eval)- create a lazy obj with captured env instead
        value_obj = LazyObject(assign_ast.get("expression"), self.env.custom_copy(), self.__eval_expr)
        if not self.env.set(var_name, value_obj):
            super().error(
                ErrorType.NAME_ERROR, f"Undefined variable {var_name} in assignment"
            )
    
    def __var_def(self, var_ast):
        var_name = var_ast.get("name")
        if not self.env.create(var_name, Interpreter.NIL_VALUE):
            super().error(
                ErrorType.NAME_ERROR, f"Duplicate definition for variable {var_name}"
            )

    def __eval_expr(self, expr_ast, env=None):
        # DOCUMENT: Pass in captured environment if evaluating lazily, otherwise use self.env
        if env is None:
            env = self.env
        if expr_ast.elem_type == InterpreterBase.NIL_NODE:
            return Interpreter.NIL_VALUE
        if expr_ast.elem_type == InterpreterBase.INT_NODE:
            return Value(Type.INT, expr_ast.get("val"))
        if expr_ast.elem_type == InterpreterBase.STRING_NODE:
            return Value(Type.STRING, expr_ast.get("val"))
        if expr_ast.elem_type == InterpreterBase.BOOL_NODE:
            return Value(Type.BOOL, expr_ast.get("val"))
        if expr_ast.elem_type == InterpreterBase.VAR_NODE:
            var_name = expr_ast.get("name")
            val = env.get(var_name)
            while isinstance(val, LazyObject):
                val = val.evaluate()
            if val is None:
                super().error(ErrorType.NAME_ERROR, f"Variable {var_name} not found")
            return val
        if expr_ast.elem_type == InterpreterBase.FCALL_NODE:
            return self.__call_func(expr_ast, env)
        if expr_ast.elem_type in Interpreter.BIN_OPS:
            try:
                return self.__eval_op(expr_ast, env)
            except ZeroDivisionError as e:
                return ExecStatus.RAISE, Value(Type.STRING, "div0")
        if expr_ast.elem_type == Interpreter.NEG_NODE:
            return self.__eval_unary(expr_ast, Type.INT, lambda x: -1 * x, env)
        if expr_ast.elem_type == Interpreter.NOT_NODE:
            return self.__eval_unary(expr_ast, Type.BOOL, lambda x: not x, env)

    def __eval_op(self, arith_ast, env=None):
        if env is None:
            env = self.env
        left_value_obj = self.__eval_expr(arith_ast.get("op1"), env)
        if isinstance(left_value_obj, tuple) and left_value_obj[0] == ExecStatus.RAISE:
            return left_value_obj
        if isinstance(left_value_obj, LazyObject):
            left_value_obj = left_value_obj.evaluate()
        if arith_ast.elem_type in ["&&", "||"]:
            return self.__short_circuit(arith_ast.elem_type, left_value_obj, arith_ast.get("op2"), env)
        right_value_obj = self.__eval_expr(arith_ast.get("op2"), env)
        if isinstance(right_value_obj, tuple) and right_value_obj[0] == ExecStatus.RAISE:
            return right_value_obj
        if isinstance(right_value_obj, LazyObject):
            right_value_obj = right_value_obj.evaluate()
        if not self.__compatible_types(
            arith_ast.elem_type, left_value_obj, right_value_obj
        ):
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible types for {arith_ast.elem_type} operation",
            )
        if arith_ast.elem_type not in self.op_to_lambda[left_value_obj.type()]:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible operator {arith_ast.elem_type} for type {left_value_obj.type()}",
            )
        f = self.op_to_lambda[left_value_obj.type()][arith_ast.elem_type]
        return f(left_value_obj, right_value_obj)

    def __compatible_types(self, oper, obj1, obj2):
        # DOCUMENT: allow comparisons ==/!= of anything against anything
        if oper in ["==", "!="]:
            return True
        return obj1.type() == obj2.type()

    def __eval_unary(self, arith_ast, t, f, env=None):
        if env is None:
            env = self.env
        value_obj = self.__eval_expr(arith_ast.get("op1"), env)
        if value_obj.type() != t:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible type for {arith_ast.elem_type} operation",
            )
        return Value(t, f(value_obj.value()))

    def __setup_ops(self):
        self.op_to_lambda = {}
        # set up operations on integers
        self.op_to_lambda[Type.INT] = {}
        self.op_to_lambda[Type.INT]["+"] = lambda x, y: Value(
            x.type(), x.value() + y.value()
        )
        self.op_to_lambda[Type.INT]["-"] = lambda x, y: Value(
            x.type(), x.value() - y.value()
        )
        self.op_to_lambda[Type.INT]["*"] = lambda x, y: Value(
            x.type(), x.value() * y.value()
        )
        self.op_to_lambda[Type.INT]["/"] = lambda x, y: Value(
            x.type(), x.value() // y.value()
        )
        self.op_to_lambda[Type.INT]["=="] = lambda x, y: Value(
            Type.BOOL, x.type() == y.type() and x.value() == y.value()
        )
        self.op_to_lambda[Type.INT]["!="] = lambda x, y: Value(
            Type.BOOL, x.type() != y.type() or x.value() != y.value()
        )
        self.op_to_lambda[Type.INT]["<"] = lambda x, y: Value(
            Type.BOOL, x.value() < y.value()
        )
        self.op_to_lambda[Type.INT]["<="] = lambda x, y: Value(
            Type.BOOL, x.value() <= y.value()
        )
        self.op_to_lambda[Type.INT][">"] = lambda x, y: Value(
            Type.BOOL, x.value() > y.value()
        )
        self.op_to_lambda[Type.INT][">="] = lambda x, y: Value(
            Type.BOOL, x.value() >= y.value()
        )
        #  set up operations on strings
        self.op_to_lambda[Type.STRING] = {}
        self.op_to_lambda[Type.STRING]["+"] = lambda x, y: Value(
            x.type(), x.value() + y.value()
        )
        self.op_to_lambda[Type.STRING]["=="] = lambda x, y: Value(
            Type.BOOL, x.value() == y.value()
        )
        self.op_to_lambda[Type.STRING]["!="] = lambda x, y: Value(
            Type.BOOL, x.value() != y.value()
        )
        #  set up operations on bools
        self.op_to_lambda[Type.BOOL] = {}
        self.op_to_lambda[Type.BOOL]["&&"] = lambda x, y: Value(
            x.type(), 
            x.value() and y.value()
        )
        self.op_to_lambda[Type.BOOL]["||"] = lambda x, y: Value(
            x.type(), x.value() or y.value()
        )
        self.op_to_lambda[Type.BOOL]["=="] = lambda x, y: Value(
            Type.BOOL, x.type() == y.type() and x.value() == y.value()
        )
        self.op_to_lambda[Type.BOOL]["!="] = lambda x, y: Value(
            Type.BOOL, x.type() != y.type() or x.value() != y.value()
        )

        #  set up operations on nil
        self.op_to_lambda[Type.NIL] = {}
        self.op_to_lambda[Type.NIL]["=="] = lambda x, y: Value(
            Type.BOOL, x.type() == y.type() and x.value() == y.value()
        )
        self.op_to_lambda[Type.NIL]["!="] = lambda x, y: Value(
            Type.BOOL, x.type() != y.type() or x.value() != y.value()
        )
    
    def __short_circuit(self, op, left_value_obj, right_expr_ast, env):
        if isinstance(left_value_obj, tuple) and left_value_obj[0] == ExecStatus.RAISE:
            return left_value_obj
        if left_value_obj.type() != Type.BOOL:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible type",
            )
        if op == "&&":
            if not left_value_obj.value():  # If False, no need to evaluate the right operand
                return Value(Type.BOOL, False)
        elif op == "||":
            if left_value_obj.value():  # If True, no need to evaluate the right operand
                return Value(Type.BOOL, True)

        right_value_obj = self.__eval_expr(right_expr_ast, env)
        if isinstance(right_value_obj, tuple) and right_value_obj[0] == ExecStatus.RAISE:
            return right_value_obj

        f = self.op_to_lambda[left_value_obj.type()][op]
        return f(left_value_obj, right_value_obj)


    def __do_if(self, if_ast):
        cond_ast = if_ast.get("condition")
        result = self.__eval_expr(cond_ast)
        if isinstance(result, tuple):
            if result[0] == ExecStatus.RAISE:
                return result
        if result.type() != Type.BOOL:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible type for if condition",
            )
        if result.value():
            statements = if_ast.get("statements")
            status, return_val = self.__run_statements(statements)
            return (status, return_val)
        else:
            else_statements = if_ast.get("else_statements")
            if else_statements is not None:
                status, return_val = self.__run_statements(else_statements)
                return (status, return_val)

        return (ExecStatus.CONTINUE, Interpreter.NIL_VALUE)

    def __do_for(self, for_ast):
        init_ast = for_ast.get("init") 
        cond_ast = for_ast.get("condition")
        update_ast = for_ast.get("update") 

        self.__run_statement(init_ast)  # initialize counter variable

        run_for = Interpreter.TRUE_VALUE
    
        if isinstance(run_for, tuple) and run_for[0] == ExecStatus.RAISE:
            return run_for
    
        while run_for.value():
            run_for = self.__eval_expr(cond_ast)  # check for-loop condition

            if isinstance(run_for, tuple) and run_for[0] == ExecStatus.RAISE:
                return run_for
            
            if run_for.type() != Type.BOOL:
                super().error(
                    ErrorType.TYPE_ERROR,
                    "Incompatible type for for condition",
                )
            if run_for.value():
                statements = for_ast.get("statements")
                status, return_val = self.__run_statements(statements)
                if status in [ExecStatus.RETURN, ExecStatus.RAISE]:
                    return status, return_val
                self.__run_statement(update_ast)  # update counter variable

        return (ExecStatus.CONTINUE, Interpreter.NIL_VALUE)
    

    def __do_try(self, try_ast):
        try_statements = try_ast.get("statements")
        status, return_val = self.__run_statements(try_statements)
        if status != ExecStatus.RAISE:
            return (status, return_val)
        exception_value = return_val
        catchers = try_ast.get("catchers")
        for catcher in catchers:
            if exception_value.value() == catcher.get("exception_type"):
                catch_statements = catcher.get("statements")
                return self.__run_statements(catch_statements)
            
        # no catchers matched, propagate the exception
        return (status, exception_value)
    def __do_return(self, return_ast):
        expr_ast = return_ast.get("expression")
        if expr_ast is None:
            return (ExecStatus.RETURN, Interpreter.NIL_VALUE)
        # lazy evaluate the return expression
        return_val = LazyObject(expr_ast, self.env.custom_copy(), self.__eval_expr)
        return (ExecStatus.RETURN, return_val)
    
    def __do_raise(self, raise_ast):
        expr_ast = raise_ast.get("exception_type")
        value_obj = self.__eval_expr(expr_ast)
        if isinstance(value_obj, tuple) and value_obj[0] == ExecStatus.RAISE:
            value_obj = value_obj[1]
        if value_obj.type() != Type.STRING:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible type for raise exception type",
            )
        return (ExecStatus.RAISE, value_obj)