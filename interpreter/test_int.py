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
func f(){
print("i will go");
return false;
}

func g(){
print("i wont go");
return true;
}

func main(){
var x;
x = f() && g();
print("short circuit");
print(x);
}
"""

n = input("Enter D for Debug, N for Normal: ")
if n.upper() == "D":
  debug_int = DEBUGInterpreter()
  debug_int.run(program4)
else:
  interpreter = Interpreter()
  interpreter.run(program4)
