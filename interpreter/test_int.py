from interpreterv3 import Interpreter

program = """
func main() : void {
  var n : int;
  print(n);
  n = inputi("hi");

  }

func fact(n : int) : int {
  if (n <= 1) { return 1; }
  return n * fact(n-1);
}

"""
interpreter = Interpreter()
interpreter.run(program)