## write a simple api to check if the user is focused or get (just return a random boolean``)

from flask import Flask, jsonify
from flask_cors import CORS  # Import CORS
import random
import json # Added import
import os   # Added import

app = Flask(__name__)
CORS(app)  # Enable CORS for the app

# Determine the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "new", "focus_log.json") # Define log file path relative to api.py's dir

@app.route('/is-focused')
def is_focused():
    if not os.path.exists(LOG_FILE):
        return jsonify({'focused': None, 'error': 'Log file not found.'}), 404

    try:
        with open(LOG_FILE, "r") as f:
            log_data = json.load(f)

        if not isinstance(log_data, list) or not log_data:
            return jsonify({'focused': None, 'error': 'Log file is empty or invalid.'})

        # Get the latest entry (last element in the list)
        latest_entry = log_data[-1]

        state = latest_entry.get("state")

        if state == "focused":
            return jsonify({'focused': True})
        elif state == "distracted":
            return jsonify({'focused': False})
        else:
            # Handle unexpected state value
            return jsonify({'focused': None, 'error': 'Unknown focus state in latest log entry.'})

    except json.JSONDecodeError:
        return jsonify({'focused': None, 'error': 'Error decoding log file.'}), 500
    except Exception as e:
        return jsonify({'focused': None, 'error': f'An error occurred: {str(e)}'}), 500


if __name__ == '__main__':
    # Note: Adjust host and port as needed for your environment
    app.run(debug=True, host='0.0.0.0', port=5000)



