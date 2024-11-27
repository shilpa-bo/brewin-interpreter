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
func t() {
 print("t");
 return true;
}

func f() {
 print("f");
 return false;
}

func main() {
  print(t() || f());
  print("---");
  print(f() || t()); 
}

/*
*OUT*
t
true
---
f
t
true
*OUT*
*/
"""
n = input("Enter D for Debug, N for Normal: ")
if n.upper() == "D":
  debug_int = DEBUGInterpreter()
  debug_int.run(program4)
else:
  interpreter = Interpreter()
  interpreter.run(program4)
