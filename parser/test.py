from brewparse import parse_program

program = """
func main() {
    var x;
    x = 5 + 6; 
    print("The sum is ", x);

}
"""

ast = parse_program(program)
print(ast)

# Access the 'functions' key in the dictionary of the Program node
for func in ast.get('functions'):
            if func.get('name') == 'main':
                main_func = func
                break
print('Func', func)
print("STATEMENTS")
for statements in func.get('statements'):
        # print(f"statement: {statements}")
        print(statements.elem_type, statements)