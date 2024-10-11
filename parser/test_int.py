from interpreterv1 import Interpreter
test_program = """
func main() {
    var x;
    x = 5 + 6;
    print("The sum is ", x);
}
"""

interpreter = Interpreter()
interpreter.run(test_program)
