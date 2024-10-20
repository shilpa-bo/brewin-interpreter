from interpreterv1 import Interpreter
test_program = """
func main() {
    var x;
    var y;
    y = 8 + 9 - 9;
    print(y, y, y);
}
"""

interpreter = Interpreter()
interpreter.run(test_program)
