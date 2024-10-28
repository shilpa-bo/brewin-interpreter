from interpreterv1 import Interpreter
test_program = """
func main() {
    var x;
    var y;
    x = 9;
    print("x");
    print(x);
  
}
"""

interpreter = Interpreter()
interpreter.run(test_program)
