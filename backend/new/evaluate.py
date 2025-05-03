from flask import Flask, request, jsonify
import openai
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize Pinecone using the new Pinecone class
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/evaluate', methods=['POST'])
def evaluate_chat():
    # Get the chat from the request
    chat = request.json.get('chat')
    if not chat:
        return jsonify({'error': 'No chat provided'}), 400

    # Perform semantic search using Pinecone
    query_vector = get_query_vector(chat)  # Assume this function converts chat to a vector
    search_results = index.query(query_vector, top_k=10)

    # Extract relevant information from search results
    relevant_info = """You are an expert productivity analyst. You have access to timeline data that
    reflects a user's activities, behaviors, and interactions across a given period. 
    This data has been semantically enriched and retrieved via Pinecone,
    ensuring that the most contextually relevant segments are included.
    Given the following timeline data:""" +  extract_relevant_info(search_results)  # Assume this function processes search results

    # Generate a response using OpenAI
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"{relevant_info}",
        max_tokens=150
    )

    return jsonify({'response': response.choices[0].text.strip()})

# Helper functions (to be implemented)
def get_query_vector(chat):
    # Convert chat to a vector
    pass

def extract_relevant_info(search_results):
    # Process search results to extract relevant information
    pass

if __name__ == '__main__':
    app.run(debug=True)
