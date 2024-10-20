from brewparse import parse_program

program = """
func main() {
    inputi();
    inputi("hello");
}
"""
ast = parse_program(program)
print(ast)

for func in ast.get('functions'):
    if func.get('name') == 'main':
        main = func

for statement in main.get('statements'):   
    print(statement)     
    if statement.elem_type == 'fcall':
        function_name = statement.get('name')  # Get the function name
        args = statement.get('args')  # Get the arguments (list)
        print(function_name)
        print(len(args))
        for arg in args:
            if arg.elem_type == 'string':
                print("String Arg:", arg.get('val'))
            if arg.elem_type == 'int':
                print("Integer Arg:", arg.get('val'))

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