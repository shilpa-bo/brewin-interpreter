from interpreterv2 import Interpreter
test_program = """
func fib(x){
  if (x == 0 || x == 1){
    print( x);
  }
  else{
    print(x-1);
    return 9;
  }
  print("This shouldn't print");
  return;
}

func main() {    
    var x;
    x = 8;
    var y;
    y = 7;
    fib(x);
    print("hello",fib(x));
}
    """

interpreter = Interpreter()
interpreter.run(test_program)
