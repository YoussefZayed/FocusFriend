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

def strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return text

def analyze_overall(client: OpenAI, img1: str, img2: str) -> dict:
    """
    Returns a JSON object describing what the user is doing overall.
    """
    b64_1 = encode_image(img1)
    b64_2 = encode_image(img2)

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict JSON generator. Analyze the two attached images "
                    "and reply with exactly one JSON object describing what the user "
                    "is doing overall. Use the key \"activities\" with a brief text value—"
                    "no markdown, no fences, no extra text."
                )
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Please analyze both images and return a JSON object."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_1}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_2}"}}
                ]
            }
        ],
        max_tokens=300
    )

    raw = strip_fences(resp.choices[0].message.content)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse overall analysis JSON: {e}\nRaw was:\n{raw}")

def assess_focus(client: OpenAI, analysis: dict) -> dict:
    """
    Given the overall analysis, returns {"state": "focused"} or {"state": "distracted"}.
    """
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict JSON generator. Given the following JSON analysis, "
                    "reply with exactly one JSON object with key \"state\" whose value "
                    "is either \"focused\" or \"distracted\"—no markdown or extra text. if they are looking at the screen and the screen has relevant programs then they are focused. If they are not or the programs are distracted then they are not focused"
                )
            },
            {"role": "user", "content": json.dumps(analysis)}
        ],
        max_tokens=10
    )

    raw = strip_fences(resp.choices[0].message.content)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse focus state JSON: {e}\nRaw was:\n{raw}")


def analyze_and_assess(img1_path: str, img2_path: str) -> dict:
    """
    Given two image paths, analyze overall activities and assess focus.
    Returns a dict:
      {
        "analysis": { "activities": "…" },
        "state":   "focused" | "distracted"
      }
    """
    client = init_openai()
    overall = analyze_overall(client, img1_path, img2_path)
    focus   = assess_focus(client, overall)
    return {
        "analysis": overall,
        "state":    focus.get("state")
    }


def main():
    parser = argparse.ArgumentParser(description="Two-step image analysis for focus.")
    parser.add_argument("img1", help="Path to first image (e.g. screen)")
    parser.add_argument("img2", help="Path to second image (e.g. desk)")
    args = parser.parse_args()

    client = init_openai()

    # Step 1: overall activity analysis
    overall = analyze_overall(client, args.img1, args.img2)

    # Step 2: focus/distracted decision
    focus = assess_focus(client, overall)

    # Combine result with timestamp
    # timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat() # Timestamping now handled by caller
    result = {
        # "timestamp": timestamp,
        "analysis": overall,
        "state": focus.get("state")
    }

    # File writing logic moved to sync_capture_transcribe.py
    # The main function here can just print the result for testing
    print("Analysis result (not saved to log by this script):")
    print(json.dumps(result, indent=2))

    # # Read existing log data, append new result, and write back
    # log_data = []
    # if os.path.exists(LOG_FILE):
    #     try:
    #         with open(LOG_FILE, "r") as f:
    #             log_data = json.load(f)
    #         if not isinstance(log_data, list): # Ensure it's a list
    #             print(f"Warning: {LOG_FILE} does not contain a list. Starting new log.")
    #             log_data = []
    #     except json.JSONDecodeError:
    #         print(f"Warning: Could not decode JSON from {LOG_FILE}. Starting new log.")
    #         log_data = []
    #     except Exception as e:
    #          print(f"Warning: Could not read {LOG_FILE}: {e}. Starting new log.")
    #          log_data = []
    #
    #
    # log_data.append(result)
    #
    # # Explicitly log before attempting to write
    # print(f"Attempting to write to log file: {LOG_FILE}")
    # try:
    #     with open(LOG_FILE, "w") as f:
    #         json.dump(log_data, f, indent=2)
    #     # Explicitly log after successful write
    #     print(f"Successfully wrote {len(log_data)} entries to {LOG_FILE}")
    # except Exception as e:
    #     # Log any error during file writing
    #     print(f"Error writing to log file {LOG_FILE}: {e}")
    #
    # #print(f"Appended result to {LOG_FILE}") # This is now redundant with the success message above
    # #print(json.dumps(result, indent=2)) # Keep this commented out or remove

if __name__ == "__main__":
    main()
