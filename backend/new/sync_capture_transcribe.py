import threading
import time
import os
from datetime import datetime
import pyautogui
import cv2
from ConnectAI import analyze_and_assess

# Directory paths
screenshot_dir = "device_screenshots"
camera_capture_dir = "camera_captures"

# Ensure directories exist
os.makedirs(screenshot_dir, exist_ok=True)
os.makedirs(camera_capture_dir, exist_ok=True)

# Function to capture a screenshot

def capture_screenshot():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    screenshot_filename = os.path.join(screenshot_dir, f"device_screenshot_{timestamp}.png")
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
    image_filename = os.path.join(camera_capture_dir, f"camera_capture_{timestamp}.png")
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
        time.sleep(5)
except KeyboardInterrupt:
    print("Process stopped.") 