from interpreterv1 import Interpreter
test_program = """
func main() {
    var y;
    var x;
    var z;
    x = "hi";
    z=x;
    y = x;
}
"""

interpreter = Interpreter()
interpreter.run(test_program)
