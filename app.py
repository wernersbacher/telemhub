from flask import Flask, render_template
import os

CURPATH = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    if os.name == 'nt':
        app.run(debug=True, port=5100)  # windows
    else:
        app.run(debug=True, host='0.0.0.0', port=5100)
