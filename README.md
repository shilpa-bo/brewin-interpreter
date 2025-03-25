## Brewin Interpreter

This project is an interpreter for a C++-like language called Brewin, built in Python. It includes a simple web-based interface (using Flask) that allows users to write and execute Brewin code directly in the browser.

There are 4 versions, each building off the other, adding new features.

Each Version has 3 parts:
- Interpreter file- implementing the actual interpreter logic
- Envionment manager- manages different function scopes and the environment
- Type manager- handles different types, all values have a type and a value

Each Version (except for v1) also has all the test cases used to test the interpreter

To run interpreter:
```
git clone https://github.com/shilpa-bo/brewin-interpreter.git
cd brewin-interpreter (navigate to project directory)
python3 app.py
```
Then visit http://localhost:5000 in your browser to access the web interface.


Here are examples of what each version can do with the specified output:

#### Brewin Version 1
```
func main(){
  print("This is Version 1!");
  var x;
  var y;
  x = 3;
  x = y;
  print(x);
}
/**
OUTPUT:
This is Version 1!
3
**/
```

#### Brewin Version 2
Notable Features:
- Functions (Recursion!)
- Lexical Scoping
```
func fib(n){
  if (n==0 || n==1){
    return 1;
  }
  return fib(n-1) + fib(n-2);
}

func main(){
  print("Brewin Version 2");
  var i;
  for (i = 0; i<5; i = i+1){
    print(fib(i));
  }
}

/**
OUTPUT:
Brewin Version 2
1
1
2
3
5
**/
```

#### Brewin Version 3
Notable Features: 
- Struct Implementations as Object References
- Static Typing
- Function Return Types
```
struct dog {
 bark: int;
 bite: int;
}

func foo(d: dog) : dog { 
  d.bark = 10;
  return d;
}

 func main() : void {
  print("This is Version 3");
  var koda: dog;
  var ashy: dog;
  koda = new dog;
  ashy = foo(koda);
  ashy.bite = 20;
  print(koda.bark, " ", koda.bite);
}
/**
OUTPUT:
This is Version 3
10 20
**/
```

#### Brewin Version 4
*Note: This is built off of V2 not V3*

Notable Features:
- Lazy Evaluation
- Try-Catch Exceptions (Error Handling)
```
func foo(x){
  print("In func foo");
  print(x);
}
func main(){
  var x;
  var y;
  y = 9/0;
  x = foo(y); /* foo doesn't run yet (lazy eval!) */
  print("In Version 4"); /* Prints first because of Lazy Evaluation */
  try{
    if(x==1){ /* Eagerly evaluating x here */
      print("I won't go here");
    }
  }
  catch "div0"{
    print("Caught div0!");
  }
}
/**
OUTPUT:
In Version 4
In func foo
Caught div0!
**/
```
