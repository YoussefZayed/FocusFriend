import threading
import time
import os
from datetime import datetime, timezone
import pyautogui
import cv2
from ConnectAI import analyze_and_assess
import json
from pinecone import Pinecone

# Pinecone init
PINECONE_API_KEY   = os.getenv("PINECONE_API_KEY")
PINECONE_ENV       = os.getenv("PINECONE_ENV")
INDEX_NAME         = os.getenv("PINECONE_INDEX_NAME", "focus-analysis")
if not (PINECONE_API_KEY and PINECONE_ENV):
    raise ValueError("Please set PINECONE_API_KEY and PINECONE_ENV in your .env")

pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if needed (1536 dims for text-embedding-ada-002)
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric="cosine"
    )

index = pc.Index(INDEX_NAME)
    

# Directory paths
screenshot_dir = "../device_screenshots"
camera_capture_dir = "../camera_captures"
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "focus_log.json")

# Ensure directories exist
os.makedirs(os.path.join(os.path.dirname(__file__), screenshot_dir), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), camera_capture_dir), exist_ok=True)

# Function to capture a screenshot

def capture_screenshot():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    screenshot_filename = os.path.join(os.path.dirname(__file__), screenshot_dir, f"device_screenshot_{timestamp}.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_filename)
    print(f"Screenshot saved as {screenshot_filename}")
    return screenshot_filename

# Function to capture an image from the camera

def capture_camera_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open the main camera.")
        return None
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("Failed to capture image")
        return None
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    image_filename = os.path.join(os.path.dirname(__file__), camera_capture_dir, f"camera_capture_{timestamp}.png")
    cv2.imwrite(image_filename, frame)
    print(f"Camera capture saved as {image_filename}")
    return image_filename

# Transcribe function

def transcribe(screenshot_path, camera_image_path):
    # Placeholder for the transcribe function
    result = analyze_and_assess(camera_image_path, screenshot_path)
    print(f"Transcribing {screenshot_path} and {camera_image_path}")
    return result

# Synchronize captures and transcription every 5 seconds
try:
    while True:
        screenshot_path = capture_screenshot()
        camera_image_path = capture_camera_image()
        if screenshot_path and camera_image_path:
            result = transcribe(screenshot_path, camera_image_path)
            print(f"Transcription result: {result}")

            # Add timestamp to the result
            timestamp = datetime.now(timezone.utc).isoformat()
            log_entry = {
                "timestamp": timestamp,
                "analysis": result.get("analysis", {}),
                "state": result.get("state")
            }

            # Read existing log data, append new result, and write back
            log_data = []
            if os.path.exists(LOG_FILE):
                try:
                    with open(LOG_FILE, "r") as f:
                        content = f.read()
                        if content: # Check if file is not empty
                           log_data = json.loads(content)
                    if not isinstance(log_data, list): # Ensure it's a list
                        print(f"Warning: {LOG_FILE} does not contain a list. Starting new log.")
                        log_data = []
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON from {LOG_FILE}. Starting new log.")
                    log_data = []
                except Exception as e:
                     print(f"Warning: Could not read {LOG_FILE}: {e}. Starting new log.")
                     log_data = []

            log_data.append(log_entry)

            # Write updated log data back to the file
            print(f"Attempting to write to log file: {LOG_FILE}")
            try:
                with open(LOG_FILE, "w") as f:
                    json.dump(log_data, f, indent=2)
                print(f"Successfully wrote {len(log_data)} entries to {LOG_FILE}")
            except Exception as e:
                print(f"Error writing to log file {LOG_FILE}: {e}")

        time.sleep(5)
except KeyboardInterrupt:
    print("Process stopped.") 