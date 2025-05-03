import threading
import time
import os
from datetime import datetime, timezone
import pyautogui
import cv2
import json
from pinecone import Pinecone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import openai
import pinecone
from ConnectAI import analyze_and_assess

# Load .env file variables *before* they are accessed
load_dotenv()

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
    

# OpenAI key (now loaded by load_dotenv above)
openai.api_key          = os.getenv("OPENAI_API_KEY")

# Pinecone vars (already loaded by load_dotenv above)
# pinecone_api_key        = os.getenv("PINECONE_API_KEY")
# pinecone_environment    = os.getenv("PINECONE_ENVIRONMENT")
pinecone_index_name     = os.getenv("PINECONE_INDEX_NAME")

# initialize Pinecone client once
# Ensure keys are loaded before initializing
# if not (PINECONE_API_KEY and PINECONE_ENV):
#     # This check should ideally be done earlier, but keeping the logic flow
#     # The earlier check on lines 17-18 should now pass if .env is correct.
#     # Re-checking here just in case, though redundant if the first check passed.
#     raise ValueError("Pinecone API Key or Environment not found after loading .env")

# pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
# pinecone_index = pinecone.Index(pinecone_index_name)

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
            time.sleep(1)
            continue

        result = transcribe(ss_path, cam_path)
        
        # --- Timestamp in EST --- 
        # Get current time and convert to America/New_York timezone
        try:
            est_tz = ZoneInfo("America/New_York")
            now_est = datetime.now(est_tz)
            log_timestamp = now_est.isoformat()
        except Exception as tz_error:
            print(f"Error getting EST timestamp: {tz_error}. Falling back to UTC.")
            # Fallback to UTC if ZoneInfo fails
            now_utc = datetime.now(timezone.utc)
            log_timestamp = now_utc.isoformat()
        # -------------------------

        # add to local JSON log…
        log_entry = {
            "id": log_timestamp, # Use the new timestamp
            "analysis": result.get("analysis", {}),
            "state": result.get("state")
        }

        # --- Append to local JSON log --- (Adding the file writing logic here)
        log_data = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r") as f:
                    content = f.read()
                    if content:
                        log_data = json.loads(content)
                if not isinstance(log_data, list):
                    print(f"Warning: {LOG_FILE} invalid content. Starting new log.")
                    log_data = []
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {LOG_FILE}. Starting new log.")
                log_data = []
            except Exception as e:
                 print(f"Warning: Could not read {LOG_FILE}: {e}. Starting new log.")
                 log_data = []

        log_data.append(log_entry)

        try:
            with open(LOG_FILE, "w") as f:
                json.dump(log_data, f, indent=2)
            print(f"Successfully wrote log entry {log_timestamp} to {LOG_FILE}")
        except Exception as e:
            print(f"Error writing to log file {LOG_FILE}: {e}")
        # ---------------------------------

        # ——— NEW: turn `result` into an embedding + upsert into Pinecone ———
        payload_text = json.dumps(result)
        # try: # Add try-except around embedding/upsert
        #     # emb_resp = openai.Embedding.create(
        #     #     model="text-embedding-ada-002",
        #     #     input=payload_text
        #     # )
        #     # vector = emb_resp["data"][0]["embedding"]

        #     # # use the timestamp as unique ID (or any other scheme)
        #     # pinecone_index.upsert([
        #     #     (
        #     #         log_timestamp,   # Use the new timestamp as ID
        #     #         vector,
        #     #         {
        #     #           "screenshot": os.path.basename(ss_path),
        #     #           "camera_img":  os.path.basename(cam_path),
        #     #           **result
        #     #         }
        #     #     )
        #     # ])
        #     print(f"Upserted embedding for {log_timestamp} into Pinecone index '{pinecone_index_name}'")
        # except Exception as pinecone_error:
        #     print(f"Error embedding or upserting to Pinecone: {pinecone_error}")


except KeyboardInterrupt:
    print("Process stopped.")
