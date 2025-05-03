## write a simple api to check if the user is focused or get (just return a random boolean``)

from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
import random
import json # Added import
import os   # Added import
from dotenv import load_dotenv
from openai import OpenAI, APIError, RateLimitError, AuthenticationError

# Load .env variables
load_dotenv()

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

    # --- OpenAI Call with Retry Logic --- 
    primary_key = os.getenv("OPENAI_API_KEY")
    secondary_key = os.getenv("OPENAI_API_KEY2")

    if not primary_key:
         # Log this error server-side
         print("Error: Primary OPENAI_API_KEY not set in environment.")
         return jsonify({'answer': 'Sorry, AI service is not configured correctly.'}), 500

    keys_to_try = [primary_key]
    if secondary_key:
        keys_to_try.append(secondary_key)

    last_exception_message = "AI service failed after trying all keys."

    system_prompt = (
        "You are a helpful assistant. Answer the user's question based ONLY on the provided focus log context. "
        "The log contains timestamped entries detailing user activities and focus state. "
        "Do not make assumptions or use external knowledge. If the answer isn't in the logs, say so."
    )
    user_prompt = (
        f"Log Context:\n{log_content}\n\n"
        f"User Question: {question}"
    )

    # Estimate token usage
    estimated_tokens = len(system_prompt.split()) + len(user_prompt.split())
    if estimated_tokens > 7500: # Adjust token limit based on model (e.g., gpt-4o allows more)
         print(f"Token estimate ({estimated_tokens}) exceeds limit.")
         return jsonify({'answer': 'Sorry, the log data is too long to process for this question.'}), 413

    for attempt, key in enumerate(keys_to_try):
        try:
            print(f"Attempting /ask OpenAI call with key #{attempt + 1}")
            client = OpenAI(api_key=key)
            resp = client.chat.completions.create(
                model="gpt-4o", # Or gpt-4o-mini
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500
            )
            ai_answer = resp.choices[0].message.content
            print(f"/ask OpenAI call successful with key #{attempt + 1}")
            return jsonify({'answer': ai_answer})

        except (APIError, RateLimitError, AuthenticationError) as e:
            print(f"/ask OpenAI API error with key #{attempt + 1}: {e}")
            last_exception_message = f"AI service error: {str(e)}"
            if attempt < len(keys_to_try) - 1:
                print("Trying next key for /ask...")
                continue
            else:
                print("All API keys failed for /ask.")
                break # Exit loop
        except Exception as e:
            print(f"Unexpected error during /ask OpenAI call (key #{attempt + 1}): {e}")
            last_exception_message = f"Unexpected AI service error: {str(e)}"
            break # Don't retry on unexpected errors

    # If loop finished without returning, return error based on last exception
    return jsonify({'answer': f'Sorry, failed to get answer. {last_exception_message}'}), 500
    # ------------------------------------

if __name__ == '__main__':
    # Note: Adjust host and port as needed for your environment
    app.run(debug=True, host='0.0.0.0', port=5000)



