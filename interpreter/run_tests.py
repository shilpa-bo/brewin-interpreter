import os
import re
from interpreterv4DEBUG import Interpreter

# Initialize the interpreter
interpreter = Interpreter()

# Base directory for test cases
base_directory = os.path.join(os.getcwd(), "Unit_Tests_V4")

# Function to extract the expected output from the test file
def extract_expected_output(content):
    match = re.search(r"/\*\s*\*OUT\*\s*(.*?)\s*\*OUT\*\s*\*/", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""
# Function to run all tests in a specified directory
def run_tests(test_file):
    directory = os.path.join(base_directory, test_file)
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            print("")
            print(f"Processing file: {filename}")
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    # Extract the expected output
                    expected_output = extract_expected_output(content)
                    
                    # Redirect interpreter output (you might need to adjust this based on how your interpreter outputs results)
                    from io import StringIO
                    import sys
                    old_stdout = sys.stdout
                    sys.stdout = captured_output = StringIO()
                    
                    try:
                        # Run the interpreter on the file content
                        interpreter.run(content)
                    finally:
                        sys.stdout = old_stdout
                    
                    # Get the actual output from the interpreter
                    actual_output = captured_output.getvalue().strip()
                    
                    # Compare outputs
                    print("Expected Output:")
                    print(expected_output)
                    print("Actual Output:")
                    print(actual_output)
                    
                    if actual_output == expected_output:
                        print(f"Test {filename} passed.")
                    else:
                        print(f"Test {filename} failed.")
            except Exception as e:
                print(f"Test {filename} failed with error: {e}")

# Function to run a single test file by specifying the subdirectory and filename
def run_single_test(test_file="tests"):
    test_name = input("Enter the file name: ")
    file_name = os.path.join(base_directory, test_file, test_name)
    try:
        with open(file_name, 'r') as file:
            content = file.read()
            expected_output = extract_expected_output(content)
            
            # Redirect interpreter output
            from io import StringIO
            import sys
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            try:
                interpreter.run(content)
            finally:
                sys.stdout = old_stdout
            
            # Get actual output
            actual_output = captured_output.getvalue().strip()
            
            print("Expected Output:")
            print(expected_output)
            print("Actual Output:")
            print(actual_output)
            
            if actual_output == expected_output:
                print(f"Test {test_name} passed.")
            else:
                print(f"Test {test_name} failed.")
    except Exception as e:
        print(f"Test {test_name} failed with error:")
        print(e)

if __name__ == "__main__":
    print("Running Fails:")
    run_tests("fails")
    print("")
    print("************************************************************************************************************")
    print("")
    print("Running Tests:")
    run_tests("tests")
    # Uncomment the next line to run a single test
    # run_single_test("tests")
