from flask import Flask, render_template, request
from qa_pipeline import answer_query

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def process_input():
    user_input = request.form['user_input']
    generated_output = answer_query(user_input)
    generated_output = generated_output.replace('\n', '<br>')
    return render_template('index.html', user_input=user_input, output=generated_output)

if __name__ == '__main__':
    app.run(debug=True)
