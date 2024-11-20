# document that we won't have a return inside the init/update of a for loop

import copy
from enum import Enum

from brewparse import parse_program
from interpreter.v_3.env_v3 import EnvironmentManager
from intbase import InterpreterBase, ErrorType
from interpreter.v_3.type_v3 import Type, Value, create_value, get_printable


class ExecStatus(Enum):
    CONTINUE = 1
    RETURN = 2

class StructDefinition:
    def __init__(self, name, fields):
        self.name = name # Struct Name
        self.fields = fields # A dictionary of field names to types
        self.is_initialized = False  # Tracks whether the struct is initialized

# Main interpreter class
class Interpreter(InterpreterBase):
    # constants
    NIL_VALUE = create_value(InterpreterBase.NIL_DEF)
    TRUE_VALUE = create_value(InterpreterBase.TRUE_DEF)
    BIN_OPS = {"+", "-", "*", "/", "==", "!=", ">", ">=", "<", "<=", "||", "&&"}
    BUILT_IN_FUNCTIONS = {"inputi", "inputs"}
    # methods
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output
        self.__setup_ops()

    # run a program that's provided in a string
    # usese the provided Parser found in brewparse.py to parse the program
    # into an abstract syntax tree (ast)
    def run(self, program):
        ast = parse_program(program)
        self.__set_up_struct_table(ast)
        self.__set_up_function_table(ast)
        self.env = EnvironmentManager()
        self.__call_func_aux("main", [])

    def __set_up_struct_table(self, ast):
        self.struct_definitions = {}
        for struct_ast in ast.get("structs"):
            self.__define_struct(struct_ast)
    
    def __define_struct(self, struct_ast):
        struct_name = struct_ast.get("name")
        struct_fields = struct_ast.get("fields")

        # check for duplicate structs
        if struct_name in self.struct_definitions:
            super().error(ErrorType.NAME_ERROR, f"Struct {struct_name} is already defined")
        
        field_dict = {}
        for field in struct_fields:
            field_name = field.get("name")
            field_type = field.get("var_type")
            if field_name in field_dict:
                super().error(ErrorType.NAME_ERROR, f"Duplicate field {field_name} in struct {struct_name}")
            field_dict[field_name] = field_type
        
        self.struct_definitions[struct_name] = StructDefinition(struct_name, field_dict)
        

    def __set_up_function_table(self, ast):
        self.func_name_to_ast = {}
        for func_def in ast.get("functions"):
            func_name = func_def.get("name")
            num_params = len(func_def.get("args"))
            for arg in func_def.get("args"):
                if not self.__is_valid_type(arg.get("var_type")):
                    super().error(
                        ErrorType.TYPE_ERROR,
                        f"Invalid type {arg.get('var_type')} for argument {arg.get('name')}",
                    )
            if not self.__is_valid_type(func_def.get("return_type"), function=True):
                super().error(
                    ErrorType.TYPE_ERROR,
                    f"Invalid type {func_def.get('return_type')} for return type",
                )
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
            if status == ExecStatus.RETURN:
                self.env.pop_block()
                return (status, return_val)

        self.env.pop_block()
        return (ExecStatus.CONTINUE, Interpreter.NIL_VALUE)

    def __run_statement(self, statement):
        status = ExecStatus.CONTINUE
        return_val = None
        if statement.elem_type == InterpreterBase.FCALL_NODE:
            self.__call_func(statement)
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
        return (status, return_val)
    
    def __call_func(self, call_node):
        func_name = call_node.get("name")
        actual_args = call_node.get("args")
        return self.__call_func_aux(func_name, actual_args)


    def __call_func_aux(self, func_name, actual_args):
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
        # helper function?
        args = {}
        for formal_ast, actual_ast in zip(formal_args, actual_args):
            result = copy.copy(self.__eval_expr(actual_ast))
            arg_name = formal_ast.get("name")
            arg_type = formal_ast.get("var_type")
            # check if var is initialized if not, let the type be the name of the struct
            result = self.__coerce_value(arg_type, result)
            if arg_type in self.struct_definitions and result.type() == Type.NIL:
                pass
            # check if the actual arg has the same type as the formal
            elif arg_type != result.type() and arg_type != result.struct_name():
                super().error(
                    ErrorType.TYPE_ERROR,
                    f"Parameter {arg_name} has type {arg_type} but actual arg has type {result.type()}",
                )
            args[arg_name] = result
        # helper function?

        # then create the new activation record 
        self.env.push_func()
        # and add the formal arguments to the activation record
        for arg_name, value in args.items():
          self.env.create(arg_name, value, value.type())
        _, return_val = self.__run_statements(func_ast.get("statements"))
        self.env.pop_func()

        # helper function: get default return types:
        func_return_type = func_ast.get("return_type")
        # DEFAULT RETURN TYPES:
        if not return_val.value() and func_return_type != Type.VOID:
            return_val = self.__get_default_value(func_return_type)
        if func_return_type == Type.VOID:
            func_return_type = Type.NIL
        return_val = self.__coerce_value(func_return_type, return_val)
        if func_return_type != return_val.type() and func_return_type != return_val.struct_name():
            super().error(
                ErrorType.TYPE_ERROR,
                f"Function {func_ast.get('name')} has return type {func_return_type} but actual return type is {return_val.type()}",
            )
        return return_val

    def __call_print(self, args):
        output = ""
        for arg in args:
            result = self.__eval_expr(arg)  # result is a Value object
            result_type = result.type()

            if result_type in self.struct_definitions:
                # If it's a struct, check if it's nil
                if result.value() == "nil":
                    output += "nil"
            else:
                # Handle non-struct types
                output += get_printable(result)
    
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
        value_obj = self.__eval_expr(assign_ast.get("expression"))
        if "." in var_name:
            # Handle struct field assignment
            return self.__assign_field(var_name, value_obj)
        else:
            expected_type, var_obj = self.env.get(var_name)
            if not var_obj:  # var obj not in struct definitions?
                super().error(
                    ErrorType.NAME_ERROR, f"Undefined variable {var_name} in assignment"
                )
            if value_obj.type() == Type.NIL and var_obj in self.struct_definitions:
                struct_def = self.struct_definitions[var_obj]
                if not struct_def.is_initialized:
                    self.env.set(var_name, value_obj)
                    return
                else:
                    super().error(
                        ErrorType.FAULT_ERROR, f"Cannot assign nil to initialized struct {var_name}"
                    )
            if var_obj in self.struct_definitions:
                struct_def = self.struct_definitions[var_obj]
                if not struct_def.is_initialized and value_obj.type() == Type.STRUCT:
                    self.env.set(var_name, value_obj)
                    struct_def.is_initialized = True
                    return

            value_obj = self.__coerce_value(expected_type, value_obj)
            if not self.env.set(var_name, value_obj):
                if expected_type.type() != value_obj.type() and expected_type != value_obj.struct_name():
                    super().error(
                        ErrorType.TYPE_ERROR,
                        f"Type mismatch: expected {expected_type.type()}, got {value_obj.type()} for {var_name}",
                    )
                super().error(
                    ErrorType.NAME_ERROR, f"Undefined variable {var_name} in assignment"
                )
    def __assign_field(self, var_name, value_obj):
        field_chain = var_name.split(".")
        struct_symbol = field_chain[0]
        struct_value = self.env.get(struct_symbol)[0]

        # Check if the struct is nil
        if struct_value.value() == "nil":
            super().error(ErrorType.FAULT_ERROR, f"Struct instance {struct_symbol} is nil")
        
        curr_struct_value = struct_value
        parent_struct_value = None
        field_to_update = None

        # Traverse the field chain, keeping track of the parent and field to update
        for field_name in field_chain[1:]:
            if curr_struct_value.struct_name() not in self.struct_definitions:
                super().error(ErrorType.TYPE_ERROR, f"Variable {struct_symbol} is not a valid struct")
            if field_name not in curr_struct_value.value():
                super().error(
                    ErrorType.NAME_ERROR, f"Field {field_name} not found in struct {curr_struct_value.type()}"
                )

            parent_struct_value = curr_struct_value
            field_to_update = field_name
            curr_struct_value = curr_struct_value.value()[field_name]

        # Coerce the value and validate types
        expected_type = curr_struct_value.type()
        value_obj = self.__coerce_value(expected_type, value_obj)
        if expected_type != value_obj.type():
            super().error(
                ErrorType.TYPE_ERROR,
                f"Type mismatch for field '{field_to_update}': expected {expected_type}, got {value_obj.type()}",
            )

        # Assign the field value in the parent struct
        parent_struct_value.value()[field_to_update] = value_obj

    
    def __var_def(self, var_ast):
        var_name = var_ast.get("name")
        var_type = var_ast.get("var_type")  

        # might be redundant? 
        if not self.__is_valid_type(var_type):
            super().error(
                ErrorType.TYPE_ERROR, f"Invalid type {var_type} for variable {var_name}"
            )
        is_struct = var_type in self.struct_definitions
        if is_struct:
            default_value = self.__get_default_value(var_type)
        else:
            try:
                default_value = self.__get_default_value(var_type)
            except ValueError:
                super().error(
                    ErrorType.TYPE_ERROR, f"No default value for type {var_type}"
                )
        if not self.env.create(var_name, default_value, var_type):
            super().error(
                ErrorType.NAME_ERROR, f"Duplicate definition for variable {var_name}"
            )

    def __assign_struct(self, struct_ast):
        # Get the struct type from the AST
        struct_type = struct_ast.get("var_type")
        # Validate the struct type
        if struct_type not in self.struct_definitions:
            super().error(ErrorType.TYPE_ERROR, f"Invalid struct type '{struct_type}'")

        # Retrieve the struct definition
        struct_definition = self.struct_definitions[struct_type]

        # Initialize all fields with default values
        instance = {}
        for field_name, field_type in struct_definition.fields.items():
            instance[field_name] = self.__get_default_value(field_type)
        
        struct_definition.is_initialized = True

        # Return a struct Value object with initialized fields
        return Value(Type.STRUCT, instance, struct_type)

    def __eval_expr(self, expr_ast):

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
            if "." in var_name:
                return self.__handle_dot_operator(var_name)
            val = self.env.get(var_name)[0]
            if val.type() == Type.STRUCT and val.value() == Type.NIL: # unitialized struct
                return Value(Type.STRUCT, "nil", val.struct_name())
            
            if val is None:
                super().error(ErrorType.NAME_ERROR, f"Variable {var_name} not found")
            return val
        if expr_ast.elem_type == InterpreterBase.NEW_NODE:
            return self.__assign_struct(expr_ast) # this will return a value object with the struct
        if expr_ast.elem_type == InterpreterBase.FCALL_NODE:
            # void is not allowed as an argument 
            # helper function?
            func_name = expr_ast.get("name")
            if func_name not in Interpreter.BUILT_IN_FUNCTIONS:
                actual_args = expr_ast.get("args")
                func_ast = self.func_name_to_ast[func_name][len(actual_args)]
                return_type = func_ast.get("return_type")
                if return_type == Type.VOID:
                    super().error(
                        ErrorType.TYPE_ERROR, "Void not allowed as argument"
                    )
                
            return self.__call_func(expr_ast)
        if expr_ast.elem_type in Interpreter.BIN_OPS:
            return self.__eval_op(expr_ast)
        if expr_ast.elem_type == Interpreter.NEG_NODE:
            return self.__eval_unary(expr_ast, Type.INT, lambda x: -1 * x)
        if expr_ast.elem_type == Interpreter.NOT_NODE:
            return self.__eval_unary(expr_ast, Type.BOOL, lambda x: not x)

    def __eval_op(self, arith_ast):
        left_value_obj = self.__eval_expr(arith_ast.get("op1"))
        right_value_obj = self.__eval_expr(arith_ast.get("op2"))
        operator = arith_ast.elem_type
        left_value_obj, right_value_obj = self.__coerce_bin_operands(operator, left_value_obj, right_value_obj)

        if operator in {"==", "!="}:
            if left_value_obj.value() == "nil" or right_value_obj.value() == "nil":
                if left_value_obj.value() == "nil" and left_value_obj.type() == Type.STRUCT and right_value_obj.type() == "nil":
                    return Value(Type.BOOL, operator == "==")
                elif right_value_obj.value() == "nil" and right_value_obj.type() == Type.STRUCT and  left_value_obj.type() == "nil":
                    return Value(Type.BOOL, operator == "==")

        if not self.__compatible_types(arith_ast.elem_type, left_value_obj, right_value_obj):
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible types for {arith_ast.elem_type} operation",
            )

        if arith_ast.elem_type not in self.op_to_lambda[left_value_obj.type()]:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible operator {operator} for type {left_value_obj.type()}",
            )

        f = self.op_to_lambda[left_value_obj.type()][operator]
        return f(left_value_obj, right_value_obj)

    def __compatible_types(self, oper, obj1, obj2):
        obj1_t = obj1.type()
        obj2_t = obj2.type()
        if (obj1_t == Type.STRUCT and obj2_t == Type.NIL) or (obj2_t==Type.STRUCT and obj1_t == Type.NIL):
            return True
        return obj1_t == obj2_t

    def __eval_unary(self, arith_ast, t, f):
        value_obj = self.__eval_expr(arith_ast.get("op1"))
        operator = arith_ast.elem_type
        value_obj = self.__coerce_unary_operand(operator, value_obj)
        if value_obj.type() != t:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible type for {operator} operation",
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
            x.type(), x.value() and y.value()
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
            Type.BOOL,
            not ((x.type() == y.type() and x.value() == y.value()) or (x.value() == "nil" and y.value() == "nil")),
        )

        
        # Set up operations on structs
        self.op_to_lambda[Type.STRUCT] = {}
        self.op_to_lambda[Type.STRUCT]["=="] = lambda x, y: Value(
            Type.BOOL,
            (x.type() == y.type() and x.value() == y.value()) or (x.value() == "nil" and y.value() == "nil"),
        )
        self.op_to_lambda[Type.STRUCT]["!="] = lambda x, y: Value(
            Type.BOOL,
            not ((x.type() == y.type() and x.value() == y.value()) or (x.value() == "nil" and y.value() == "nil")),
        )


    def __do_if(self, if_ast):
        cond_ast = if_ast.get("condition")
        result = self.__eval_expr(cond_ast)
        result = self.__coerce_value(Type.BOOL, result)
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
        while run_for.value():
            run_for = self.__coerce_value(Type.BOOL, self.__eval_expr(cond_ast)) # check for-loop condition
            if run_for.type() != Type.BOOL:
                super().error(
                    ErrorType.TYPE_ERROR,
                    "Incompatible type for for condition",
                )
            if run_for.value():
                statements = for_ast.get("statements")
                status, return_val = self.__run_statements(statements)
                if status == ExecStatus.RETURN:
                    return status, return_val
            self.__run_statement(update_ast)  # update counter variable

        return (ExecStatus.CONTINUE, Interpreter.NIL_VALUE)

    def __do_return(self, return_ast):
        expr_ast = return_ast.get("expression")
        if expr_ast is None:
            return (ExecStatus.RETURN, Interpreter.NIL_VALUE)
        value_obj = copy.copy(self.__eval_expr(expr_ast))
        return (ExecStatus.RETURN, value_obj)
    
    def __get_default_value(self, var_type):
        if var_type == Type.INT:
            return create_value(0)
        if var_type == Type.BOOL:
            return create_value(InterpreterBase.FALSE_DEF)
        if var_type == Type.STRING:
            return create_value("")
        if var_type == Type.NIL:
            return create_value(InterpreterBase.NIL_DEF)
        if var_type in self.struct_definitions:  # Struct support CHANGE THIS
            return Value(Type.STRUCT, "nil", var_type)
        if var_type == Type.STRUCT: # change this???
            return Value(Type.STRUCT, "nil")
        raise ValueError(f"No default value for type {var_type}") # maybe change this??

    def __is_valid_type(self, type, function=False):
        # extend to structs
        # but for now this works
        if function:
            return type in ([Type.INT, Type.STRING, Type.BOOL, Type.NIL,Type.VOID] + list(self.struct_definitions.keys()))
        return type in [Type.INT, Type.STRING, Type.BOOL, Type.NIL] + list(self.struct_definitions.keys())

    def __coerce_value(self, expected_type, actual_val):
        if expected_type == actual_val.type():
            return actual_val
        if expected_type == actual_val.struct_name() and actual_val.type() == Type.STRUCT:
            if expected_type in self.struct_definitions:
                if actual_val.struct_name() != expected_type:
                    super().error(
                        ErrorType.TYPE_ERROR,
                        f"Expected struct type {expected_type} but got {actual_val.struct_name}",
                    )
                return actual_val
        if expected_type == Type.BOOL and actual_val.type() == Type.INT:
            coerced_value = Value(Type.BOOL, actual_val.value() != 0)
            return coerced_value
        return actual_val
        # can't coerce anything else
    
    def __coerce_unary_operand(self, operator, op1):
        if operator == "!":
            return self.__coerce_value(Type.BOOL, op1)
        return op1
    
    def __coerce_bin_operands(self, operator, op1, op2):
        if operator in {"==", "!=", "&&", "||"}:
            return self.__coerce_value(Type.BOOL, op1), self.__coerce_value(Type.BOOL, op2)
        if op1.type() != op2.type():
            raise ErrorType.TYPE_ERROR(
                f"Incompatible types {op1.type()} and {op2.type()} for operator {operator}"
            )
        return op1, op2
    
    def __handle_dot_operator(self, var_name):
        field_chain = var_name.split(".")
        struct_symbol = field_chain[0]
        struct_value = self.env.get(struct_symbol)[0]
        struct_name = self.env.get(struct_symbol)[1]
        # struct_symbol, field_name = var_name.split(".")
        # struct_value = self.env.get(struct_symbol)[0]
        # Check if the struct is nil
        if struct_value.value() == "nil":
            super().error(ErrorType.FAULT_ERROR, f"Struct instance {struct_symbol} is nil")

        # Ensure the struct is valid
        # print(struct_value.value(), struct_value.type())
        # for key, val in struct_value.value().items():
        #     print(key, val.type(), val.value())
        curr_struct_value = struct_value
        for field_name in field_chain[1:]:
            if curr_struct_value.struct_name() not in self.struct_definitions:
                super().error(
                    ErrorType.TYPE_ERROR,
                    f"Variable {curr_struct_value.struct_name()} is not a valid struct",
                )
            if field_name not in curr_struct_value.value():
                super().error(
                    ErrorType.NAME_ERROR, f"Field {field_name} not found in struct {curr_struct_value.struct_name()}"
                )
            curr_struct_value = curr_struct_value.value()[field_name]

        return curr_struct_value
