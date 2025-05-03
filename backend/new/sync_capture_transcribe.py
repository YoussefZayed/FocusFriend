#!/usr/bin/env python3
import threading
import time
import os
from datetime import datetime
import pyautogui
import cv2
import openai
from pinecone import Pinecone
from dotenv import load_dotenv
from ConnectAI import analyze_and_assess

# Load environment variables from .env
load_dotenv()

# OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Please set OPENAI_API_KEY in your .env")

# Pinecone init
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "focus-analysis")

if not (PINECONE_API_KEY and PINECONE_ENV):
    raise ValueError("Please set PINECONE_API_KEY and PINECONE_ENV in your .env")

pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if needed (1536 dims for ada-002 embeddings)
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric="cosine"
    )

index = pc.Index(INDEX_NAME)

# Directory paths
screenshot_dir = "device_screenshots"
camera_capture_dir = "camera_captures"
os.makedirs(screenshot_dir, exist_ok=True)
os.makedirs(camera_capture_dir, exist_ok=True)


def capture_screenshot():
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    fn = os.path.join(screenshot_dir, f"device_screenshot_{ts}.png")
    pyautogui.screenshot().save(fn)
    print(f"Screenshot saved as {fn}")
    return fn


def capture_camera_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera.")
        return None
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("Failed to capture image")
        return None
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    fn = os.path.join(camera_capture_dir, f"camera_capture_{ts}.png")
    cv2.imwrite(fn, frame)
    print(f"Camera capture saved as {fn}")
    return fn


def store_in_pinecone(result: dict, id: str):
    """
    result: { "analysis": {"activities": ...}, "state": "focused"|"distracted" }
    id: unique string for this record (e.g. timestamp or filename)
    """
    activities = result["analysis"].get("activities", "")
    state = result.get("state", "")
    text = f"{activities}. State: {state}"

    # 1) Create embedding
    emb_resp = openai.Embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    vector = emb_resp.data[0].embedding

    # 2) Upsert to Pinecone
    metadata = {
        "activities": activities,
        "state": state,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    index.upsert([(id, vector, metadata)])
    print(f"Upserted vector to Pinecone with id={id}")


def transcribe_and_store(screen_path, camera_path):
    # 1) Call your two-step analysis
    result = analyze_and_assess(screen_path, camera_path)
    print(f"Analysis result: {result}")

    # 2) Build an ID (here, use the screen filename minus extension)
    rec_id = os.path.splitext(os.path.basename(screen_path))[0]

    # 3) Store in Pinecone
    store_in_pinecone(result, rec_id)


if __name__ == "__main__":
    try:
        while True:
            screen = capture_screenshot()
            cam = capture_camera_image()
            if screen and cam:
                transcribe_and_store(screen, cam)
            time.sleep(5)
    except KeyboardInterrupt:
        print("Stopping capture loop.")
