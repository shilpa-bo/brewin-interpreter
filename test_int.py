# from interpreter_v_4.interpreterv4 import Interpreter
from interpreter_v_3.interpreterv3 import Interpreter

program3 = """
struct person{
    name : string;
}
func main() : void{
    var p : person;
    print(p);
    p = new person;
    p.name = "Shilpa";
    print(p.name);
}

"""
program4 = """
func main(){
    print("Hello World");
}
"""

interpreter = Interpreter()
interpreter.run(program3)