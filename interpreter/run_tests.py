import os
from interpreterv4 import Interpreter

# Initialize the interpreter
interpreter = Interpreter()

# Base directory for test cases
# Test case directories should be in a directory called "test_cases"
base_directory = os.path.join(os.getcwd(), "test_cases_v3")

# Function to run all tests in a specified directory
def run_tests(test_file):
    directory = os.path.join(base_directory, test_file)
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            print(f"Processing file: {filename}")
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    # Run the interpreter on the file content
                    interpreter.run(content)
            except Exception as e:
                print(f"Test {filename} failed with error: {e}")

# Function to run a single test file by specifying the subdirectory and filename
def run_1(test_file, test_name):
    file_name = os.path.join(base_directory, test_file, test_name)
    try:
        with open(file_name, 'r') as file:
            content = file.read()
            interpreter.run(content)
    except Exception as e:
        print(f"Test {test_name} failed with error:")
        print(e)

# Main block
if __name__ == "__main__":
    print("Running Fails")
    run_tests("fails")

    print("Running Tests")
    run_tests("tests")
