from interpreterv2 import Interpreter

program = """
func foo(x:int, y:string)  : int{
  x = 10;
  return x+1;
}

func main(): void {
var x : int;
x = 5;
foo(x, "0");
print(x);
}
"""
interpreter = Interpreter()
interpreter.run(program)