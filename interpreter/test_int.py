from interpreterv4 import Interpreter
from interpreterv4DEBUG import Interpreter as DEBUGInterpreter
program3 = """

func main(){
var x;
x = "hi";
print(x);
print(x);
}
"""
program4 = """
func main() {
var result;
  result =f(3);
  print(result);
  }

func f(x) {
  print("in f(x)");
  return 2*x;
}

"""

n = input("Enter D for Debug, N for Normal: ")
if n.upper() == "D":
  debug_int = DEBUGInterpreter()
  debug_int.run(program4)
else:
  interpreter = Interpreter()
  interpreter.run(program4)
