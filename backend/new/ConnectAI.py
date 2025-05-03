#!/usr/bin/env python3
import os
import json
import argparse
import base64
from dotenv import load_dotenv
from openai import OpenAI
import datetime  # Added import

# Load .env
load_dotenv()

# Determine the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "focus_log.json") # Define log file name relative to script dir

def init_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable")
    return OpenAI(api_key=api_key)

def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def analyze_and_assess(img1_path: str, img2_path: str) -> dict:
    """
    Given two image paths, analyze overall activities and assess focus using a single API call.
    Returns a dict:
      {
        "analysis": { "activities": "…" },
        "state":   "focused" | "distracted"
      }
    """
    client = init_openai()
    b64_1 = encode_image(img1_path)
    b64_2 = encode_image(img2_path)

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": (
                    "Analyze the two attached images. "
                    "Reply with exactly one JSON object containing two keys: 'activities' and 'state'. "
                    "For 'activities', provide a detailed text value describing what the user is doing overall: "
                    "what they are looking at, and the specific content/applications on the screen(s). If they are looking infront of them then assume they are looking at the screen. be genrous with giving the user credit for looking at the screen even if they are  more than 1 person"
                    "Ignore the astronaut figure sometimes visible on the right. Only describe the user based on the front camera and the screen content. "
                    "For 'state', the value must be either 'focused' or 'distracted'. "
                    "The user is 'focused' ONLY IF they are looking directly at the screen AND the screen displays content relevant to work or study (e.g., code editor, document, educational website or if they are doing the taks on their todo list).  "
                    "Otherwise, they are 'distracted' (e.g., looking away, phone use, social media, games, unrelated websites, REDDIT MEANS DISTRACTION). "
                    "Output only the JSON object, no markdown, no fences, no extra text."
                    "be generous with saying they are focused if they are looking at the screen and doing something relevant to work or study"
                )
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze both images and return a JSON object with 'activities' and 'state'."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_1}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_2}"}}
                ]
            }
        ],
        max_tokens=600 # Adjusted max_tokens for combined analysis
    )

    try:
        combined_result = json.loads(resp.choices[0].message.content)
        # Ensure the response has the expected keys
        if "activities" not in combined_result or "state" not in combined_result:
            raise ValueError(f"OpenAI response missing expected keys ('activities', 'state').\nRaw response: {combined_result}")

        # Reconstruct the desired output format
        return {
            "analysis": {"activities": combined_result.get("activities")},
            "state": combined_result.get("state")
        }
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse combined analysis/focus JSON: {e}\nRaw was:\n{resp.choices[0].message.content}")
    except AttributeError as e:
        raise ValueError(f"Unexpected response structure from OpenAI API: {e}\nResponse: {resp}")
    except Exception as e:
        # Catch any other potential errors during processing
        raise ValueError(f"Error processing OpenAI response: {e}\nRaw content: {resp.choices[0].message.content if resp.choices else 'No choices found'}")

def main():
    parser = argparse.ArgumentParser(description="Single-call image analysis for focus.") # Updated description
    parser.add_argument("img1", help="Path to first image (e.g. screen)")
    parser.add_argument("img2", help="Path to second image (e.g. desk)")
    args = parser.parse_args()

    # Perform analysis and assessment in one step
    result = analyze_and_assess(args.img1, args.img2)

    # The main function here can just print the result for testing
    print("Analysis result (not saved to log by this script):")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
