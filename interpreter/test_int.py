from interpreterv3 import Interpreter
program3 = """
struct animal {
  name: string;
  extinct: bool;
}
func foo(a : animal) : animal{
print("FOO");
return a;
}
func main() : void{
var a : animal;
foo(nil);
}
"""
program4 = """
struct a {
  inner : int;
}

func main() : void {
  var a : a;
  print(nil == a);
}
"""

interpreter = Interpreter()
interpreter.run(program3)