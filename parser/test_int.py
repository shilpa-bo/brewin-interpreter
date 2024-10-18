from interpreterv1 import Interpreter
test_program = """
func main() {
    var x;
    x = "hi";
    print("hi", x);
    x = inputi("Enter Num");
    print("h", x);
}
"""

interpreter = Interpreter()
interpreter.run(test_program)
