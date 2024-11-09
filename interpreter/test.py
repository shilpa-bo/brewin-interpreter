from brewparse import parse_program

def pretty_print_ast(node, indent=0):
    """ Recursively prints the AST with indentation. """
    indent_str = ' ' * indent
    if isinstance(node, dict):
        for key, value in node.items():
            print(f"{indent_str}{key}:")
            pretty_print_ast(value, indent + 4)
    elif isinstance(node, list):
        for item in node:
            pretty_print_ast(item, indent)
    else:
        print(f"{indent_str}{node}")


# Call the function on the AST

program = """
func main() {
    var z;
    var y;
    z = 9;
    if (z>=1) {return 1;}
    else {return 0;}
    var z;
    x = -z;
    y = !true;
    
return x;
}
func foo(){
return (10);
}
"""
ast = parse_program(program)
pretty_print_ast(ast)
print("***PARSING***")
# Assuming 'ast' contains the parsed AST structure
for func in ast.get('functions'):
    if func.get('name') == 'main':
        main = func
        print("Function 'main' arguments:")
        pretty_print_ast(main.get('args'))
        
        print("\nFunction 'main' statements:")
        for statement in main.get('statements'):
            pretty_print_ast(statement)
            if statement.elem_type == 'if':
                if_statement = statement
                print("\nFunction 'if' statements:")
                # condition = statement.get('condition')
                # print("Condition: ", condition)
                # print("Statements: ")
                for statement in if_statement.get('statements'):
                    print("Statement", statement)
                for statement in if_statement.get('else_statements'):
                    print("Else Statement", statement)

# for func in ast.get('functions'):
#     if func.get('name') == 'main':
#         main = func
# print(main.get('args'))
# for statement in main.get('statements'):
#     print(statement)
# for func in ast.get('functions'):
#     if func.get('name') == 'main':
#         main = func
# for statement in main.get('statements'):
#     print(statement)
#     expression = statement.get('expression')
#     print(expression)
#     if expression:
#         print(expression.get('op1'))
#         op1 = expression.get('op1')

# for statement in main.get('statements'):   
#     print(statement)     
#     if statement.elem_type == 'fcall':
#         function_name = statement.get('name')  # Get the function name
#         args = statement.get('args')  # Get the arguments (list)
#         print(function_name)
#         print(len(args))
#         for arg in args:
#             if arg.elem_type == 'string':
#                 print("String Arg:", arg.get('val'))
#             if arg.elem_type == 'int':
#                 print("Integer Arg:", arg.get('val'))

    # expression = (statement.get('expression'))
    # print
    # if expression:
    #     print("Expression", f'({expression.elem_type})', expression)
    #     print(expression.get('op1'))
    #     print(expression.get('op2'))
    # else:
    #     print("No expression in this statement.")

# # Access the 'functions' key in the dictionary of the Program node
# for func in ast.get('functions'):
#             if func.get('name') == 'main':
#                 main_func = func
#                 break
# print('Func', func)
# print("STATEMENTS")
# for statements in func.get('statements'):
#         # print(f"statement: {statements}")
#         print(statements)
#         expression = statements.get('expression')
    
#         if expression:
#             print("Expression", f'({expression.elem_type})', expression)
#             print(expression.get('val'))
#         else:
#             print("No expression in this statement.")