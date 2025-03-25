from flask import Flask, render_template, request, jsonify
import sys
import io
import os

# Add interpreter directories to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'interpreter_v_1'))
sys.path.append(os.path.join(current_dir, 'interpreter_v_2'))
sys.path.append(os.path.join(current_dir, 'interpreter_v_3'))
sys.path.append(os.path.join(current_dir, 'interpreter_v_4'))

# Import all intepreter versions
from interpreter_v_1.interpreterv1 import Interpreter as Interpreter1
from interpreter_v_2.interpreterv2 import Interpreter as Interpreter2
from interpreter_v_3.interpreterv3 import Interpreter as Interpreter3
from interpreter_v_4.interpreterv4 import Interpreter as Interpreter4

app = Flask(__name__)

INTERPRETERS = {
    "1": Interpreter1,
    "2": Interpreter2,
    "3": Interpreter3,
    "4": Interpreter4
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get('code', '')
    version = request.json.get('version', '2')  # Default to v2 if not specified
    
    if not code.strip():
        return jsonify({'error': 'No code provided'}), 400

    try:
        # Get the appropriate interpreter class
        InterpreterClass = INTERPRETERS.get(version)
        if not InterpreterClass:
            return jsonify({'error': f'Invalid interpreter version: {version}'}), 400

        # Capture stdout to get the interpreter's output
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        interpreter = InterpreterClass()
        interpreter.run(code)

        # Restore stdout and get the captured output
        sys.stdout = old_stdout
        output = redirected_output.getvalue()

        return jsonify({'output': output})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
