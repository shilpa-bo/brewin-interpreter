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
func error_function() {
  raise "error";
  print("after raise");
  return 0;
}

func main() {
  var x;
  x = error_function() + 10;
  try {
    print(x); 
  }
  catch "error" {
    print("Caught an error during evaluation of x");
  }
}
"""

n = input("Enter D for Debug, N for Normal: ")
if n.upper() == "D":
  debug_int = DEBUGInterpreter()
  debug_int.run(program4)
else:
  interpreter = Interpreter()
  interpreter.run(program4)
