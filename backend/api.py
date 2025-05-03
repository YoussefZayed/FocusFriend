## write a simple api to check if the user is focused or get (just return a random boolean``)

from flask import Flask, jsonify
from flask_cors import CORS  # Import CORS
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for the app

@app.route('/is-focused')
def is_focused():
    return jsonify({'focused': random.choice([True,False])})

if __name__ == '__main__':
    app.run(debug=True)



