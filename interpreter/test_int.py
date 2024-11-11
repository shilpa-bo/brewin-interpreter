from interpreterv3 import Interpreter

program = """
func main(): void {
    if(9==true){
        print("yeehaw");
    }
    else{
        print("need an error bitches");
    }
}

"""
interpreter = Interpreter()
interpreter.run(program)