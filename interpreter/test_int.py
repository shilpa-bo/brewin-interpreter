from interpreterv1 import Interpreter
test_program = """
func main() {
    var x;
    for (x = 5; x>0; x=x-1){
        print(x);
    }    
}
"""

interpreter = Interpreter()
interpreter.run(test_program)
