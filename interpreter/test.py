from brewparse import parse_program


# Call the function on the AST

program = """
func foo(x:int, y:string)  : int{
  x = 10;
}

func main(): void {
   foo(9);
}
"""
ast = parse_program(program)
print(ast)
print("***PARSING***")
# Assuming 'ast' contains the parsed AST structure
for func in ast.get('functions'):
    print(f"Current Function: {func.get('name')}")
    for statement in func.get('statements'):
        print(statement)
        if statement.elem_type == 'vardef':
            vardef = statement
            print(statement.get("var_type"))
#         print("\nFunction 'main' statements:")
#         for statement in main.get('statements'):
#             pretty_print_ast(statement)
#             if statement.elem_type == 'if':
#                 if_statement = statement
#                 print("\nFunction 'if' statements:")
#                 # condition = statement.get('condition')
#                 # print("Condition: ", condition)
#                 # print("Statements: ")
#                 for statement in if_statement.get('statements'):
#                     print("Statement", statement)
#                 for statement in if_statement.get('else_statements'):
#                     print("Else Statement", statement)

# # for func in ast.get('functions'):
# #     if func.get('name') == 'main':
# #         main = func
# # print(main.get('args'))
# # for statement in main.get('statements'):
# #     print(statement)
# # for func in ast.get('functions'):
# #     if func.get('name') == 'main':
# #         main = func
# # for statement in main.get('statements'):
# #     print(statement)
# #     expression = statement.get('expression')
# #     print(expression)
# #     if expression:
# #         print(expression.get('op1'))
# #         op1 = expression.get('op1')

# # for statement in main.get('statements'):   
# #     print(statement)     
# #     if statement.elem_type == 'fcall':
# #         function_name = statement.get('name')  # Get the function name
# #         args = statement.get('args')  # Get the arguments (list)
# #         print(function_name)
# #         print(len(args))
# #         for arg in args:
# #             if arg.elem_type == 'string':
# #                 print("String Arg:", arg.get('val'))
# #             if arg.elem_type == 'int':
# #                 print("Integer Arg:", arg.get('val'))

#     # expression = (statement.get('expression'))
#     # print
#     # if expression:
#     #     print("Expression", f'({expression.elem_type})', expression)
#     #     print(expression.get('op1'))
#     #     print(expression.get('op2'))
#     # else:
#     #     print("No expression in this statement.")

# # # Access the 'functions' key in the dictionary of the Program node
# # for func in ast.get('functions'):
# #             if func.get('name') == 'main':
# #                 main_func = func
# #                 break
# # print('Func', func)
# # print("STATEMENTS")
# # for statements in func.get('statements'):
# #         # print(f"statement: {statements}")
# #         print(statements)
# #         expression = statements.get('expression')
    
# #         if expression:
# #             print("Expression", f'({expression.elem_type})', expression)
# #             print(expression.get('val'))
# #         else:
# #             print("No expression in this statement.")