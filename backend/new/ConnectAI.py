#!/usr/bin/env python3
import os
import json
import argparse
import base64
from dotenv import load_dotenv
from openai import OpenAI, APIError, RateLimitError, AuthenticationError
import datetime  # Added import

# Load .env
load_dotenv()

# Determine the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "focus_log.json") # Define log file name relative to script dir

def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def analyze_and_assess(img1_path: str, img2_path: str) -> dict:
    """
    Given two image paths, analyze overall activities and assess focus.
    Tries primary OpenAI key, then secondary key on failure.
    Returns a dict: {"analysis": ..., "state": ...}
    """
    primary_key = os.getenv("OPENAI_API_KEY")
    secondary_key = os.getenv("OPENAI_API_KEY2") # Load secondary key

    if not primary_key:
        raise ValueError("Primary OPENAI_API_KEY environment variable not set.")

    b64_1 = encode_image(img1_path)
    b64_2 = encode_image(img2_path)

    keys_to_try = [primary_key]
    if secondary_key:
        keys_to_try.append(secondary_key)

    last_exception = None

    for attempt, key in enumerate(keys_to_try):
        try:
            print(f"Attempting OpenAI call with key #{attempt + 1}")
            client = OpenAI(api_key=key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini", # Consider keeping mini for speed/cost
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system", # Updated system prompt below
                        "content": (
                            "Analyze the two attached images. Reply with exactly one JSON object containing two keys: 'activities' and 'state'. NO SUB OBJECTS!!! "
                            "For 'activities', describe in detail what the user is doing, looking at, their posture, and specific content/apps on screen. If they are looking forward, assume they are looking at the screen. Note if multiple people are present. "
                            "Ignore the astronaut figure. Base description only on camera and screen content. "
                            "For 'state', value must be 'focused' or 'distracted'. User is 'focused' if looking at screen AND screen shows relevant work/study (e.g., code, docs, relevant website, task from todo list). "
                            "User is 'distracted' if looking away, on phone, social media, games, unrelated sites (e.g., Reddit).  WRITE VERY LITTLE ABOUT THE SELFIE IMAGE AND MORE ABOUT THE SCREEN IMAGE. "
                            "Be slightly generous towards 'focused' if user is looking at screen and content is plausibly work-related. Output ONLY the JSON object."
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
                max_tokens=600
            )

            # --- Successful Call --- 
            try:
                combined_result = json.loads(resp.choices[0].message.content)
                if "activities" not in combined_result or "state" not in combined_result:
                    raise ValueError(f"OpenAI response missing expected keys. Raw: {combined_result}")
                print(f"OpenAI call successful with key #{attempt + 1}")
                return {
                    "analysis": {"activities": combined_result.get("activities")},
                    "state": combined_result.get("state")
                }
            except (json.JSONDecodeError, AttributeError, IndexError, KeyError) as parse_error:
                 # If parsing fails even after successful API call, treat as failure for this key
                 print(f"Error parsing successful response (key #{attempt+1}): {parse_error}")
                 last_exception = ValueError(f"Could not parse analysis JSON: {parse_error}\nRaw was:\n{resp.choices[0].message.content if resp.choices else 'No choices found'}")
                 continue # Try next key if available

        # --- API Call Failed --- 
        except (APIError, RateLimitError, AuthenticationError) as e:
            print(f"OpenAI API error with key #{attempt + 1}: {e}")
            last_exception = e
            # If it was the last key or another key exists, continue to next iteration/end loop
            if attempt < len(keys_to_try) - 1:
                print("Trying next key...")
                continue
            else:
                print("All API keys failed.")
                break # Exit loop after last key fails
        except Exception as e:
            # Catch other unexpected errors during API call
            print(f"Unexpected error during OpenAI call (key #{attempt + 1}): {e}")
            last_exception = e
            break # Don't retry on unexpected errors

    # If loop finished without returning, raise the last known exception
    raise last_exception if last_exception else RuntimeError("OpenAI call failed for unknown reasons after trying all keys.")

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
