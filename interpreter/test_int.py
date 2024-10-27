from interpreterv1 import Interpreter
test_program = """
func main() {
    var x;
    var y;
    y = true;
    x = nil;
    print(y);
    print(x);
    x = !y;
}
"""

interpreter = Interpreter()
interpreter.run(test_program)
