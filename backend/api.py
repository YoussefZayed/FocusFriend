## write a simple api to check if the user is focused or get (just return a random boolean``)

from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
import random
import json # Added import
import os   # Added import
from new.ConnectAI import init_openai # Import the initializer

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

# New RAG endpoint
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({'error': 'No question provided.'}), 400

    if not os.path.exists(LOG_FILE):
        return jsonify({'answer': 'Sorry, I cannot answer as the focus log file was not found.'}), 404

    try:
        with open(LOG_FILE, "r") as f:
            # WARNING: Loading the entire log can exceed token limits for large files!
            # A real implementation should filter/retrieve relevant parts.
            log_data = json.load(f)
            log_content = json.dumps(log_data) # Pass the whole log as context for now

    except json.JSONDecodeError:
        return jsonify({'answer': 'Sorry, I could not read the focus log data.'}), 500
    except Exception as e:
        return jsonify({'answer': f'Sorry, an error occurred reading the log: {str(e)}'}), 500

    try:
        client = init_openai() # Initialize OpenAI client

        system_prompt = (
            "You are a helpful assistant. Answer the user's question based ONLY on the provided focus log context. "
            "The log contains a list of timestamped entries detailing user activities and focus state (focused/distracted). "
            "Do not make assumptions or use external knowledge. If the answer isn't in the logs, say so."
        )

        user_prompt = (
            f"Log Context:\n{log_content}\n\n" # Embed the log content
            f"User Question: {question}"
        )

        # Estimate token usage - very rough check
        # A proper check would use a tokenizer
        estimated_tokens = len(system_prompt.split()) + len(user_prompt.split())
        # print(f"Estimated tokens for prompt: {estimated_tokens}") # Optional: for debugging
        if estimated_tokens > 3500: # Leave ~500 tokens for response with gpt-4o-mini (or similar)
             return jsonify({'answer': 'Sorry, the log data is too long to process for this question.'}), 413 # Payload Too Large

        resp = client.chat.completions.create(
            # Consider using a cheaper/faster model if feasible e.g. gpt-4o-mini
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500 # Adjust as needed
        )

        ai_answer = resp.choices[0].message.content
        return jsonify({'answer': ai_answer})

    except Exception as e:
        # Log the actual error for debugging on the server
        print(f"Error calling OpenAI or processing response: {e}")
        return jsonify({'answer': f'Sorry, an error occurred while trying to get an answer from the AI: {str(e)}'}), 500

if __name__ == '__main__':
    # Note: Adjust host and port as needed for your environment
    app.run(debug=True, host='0.0.0.0', port=5000)



