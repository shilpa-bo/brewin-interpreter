from interpreterv4 import Interpreter
from interpreterv4DEBUG import Interpreter as DEBUGInterpreter
program3 = """

func main() {
    print("hello");
    var y;
    if (y==nil){
        var x;
        x = 5;
        y = 7 + x;
    }
    print(y);
}
"""
program4 = """
func f(x) {
  print("f is running");
  var y;
  y = 2 * x;
  return y;
}

func main() {
  var x; 
  var result;
  x = f(3);
  result = x + 10;
  print(x);
  x = 4;
  print(x);
  print(result);
}

"""

n = input("Enter D for Debug, N for Normal: ")
if n.upper() == "D":
  debug_int = DEBUGInterpreter()
  debug_int.run(program4)
else:
  interpreter = Interpreter()
  interpreter.run(program4)
