import threading
import time
import os
from datetime import datetime, timezone
import pyautogui
import cv2
import json

from dotenv import load_dotenv
import openai
import pinecone

from ConnectAI import analyze_and_assess

# load credentials
load_dotenv()
openai.api_key          = os.getenv("OPENAI_API_KEY")
pinecone_api_key        = os.getenv("PINECONE_API_KEY")
pinecone_environment    = os.getenv("PINECONE_ENVIRONMENT")
pinecone_index_name     = os.getenv("PINECONE_INDEX_NAME")

# initialize Pinecone client once
pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
pinecone_index = pinecone.Index(pinecone_index_name)

# Directory paths
screenshot_dir     = "../device_screenshots"
camera_capture_dir = "../camera_captures"
LOG_FILE           = os.path.join(os.path.dirname(os.path.abspath(__file__)), "focus_log.json")

os.makedirs(os.path.join(os.path.dirname(__file__), screenshot_dir), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), camera_capture_dir), exist_ok=True)

def capture_screenshot():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename  = os.path.join(os.path.dirname(__file__),
                             screenshot_dir,
                             f"device_screenshot_{timestamp}.png")
    pyautogui.screenshot().save(filename)
    return filename

def capture_camera_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename  = os.path.join(os.path.dirname(__file__),
                             camera_capture_dir,
                             f"camera_capture_{timestamp}.png")
    cv2.imwrite(filename, frame)
    return filename

def transcribe(screenshot_path, camera_image_path):
    return analyze_and_assess(camera_image_path, screenshot_path)

try:
    while True:
        ss_path = capture_screenshot()
        cam_path = capture_camera_image()
        if not ss_path or not cam_path:
            time.sleep(5)
            continue

        result = transcribe(ss_path, cam_path)
        # add to local JSON log…
        timestamp_utc = datetime.now(timezone.utc).isoformat()
        log_entry = {
            "id": timestamp_utc,
            "analysis": result.get("analysis", {}),
            "state": result.get("state")
        }
        # (code to append log_entry into focus_log.json…)

        # ——— NEW: turn `result` into an embedding + upsert into Pinecone ———
        payload_text = json.dumps(result)
        emb_resp = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=payload_text
        )
        vector = emb_resp["data"][0]["embedding"]

        # use the timestamp as unique ID (or any other scheme)
        pinecone_index.upsert([
            (
                timestamp_utc,   # unique ID
                vector,          # your embedding
                {
                  "screenshot": os.path.basename(ss_path),
                  "camera_img":  os.path.basename(cam_path),
                  **result        # you can store the full result as metadata if you like
                }
            )
        ])

        print(f"Upserted embedding for {timestamp_utc} into Pinecone index '{pinecone_index_name}'")
        time.sleep(5)

except KeyboardInterrupt:
    print("Process stopped.")
