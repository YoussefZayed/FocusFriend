from flask import Flask, request, jsonify
import subprocess
import os
from datetime import datetime

app = Flask(__name__)

# Directory to save screenshots
screenshot_dir = "screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

def capture_screenshot():
    # Capture a screenshot using pyautogui
    import pyautogui
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    screenshot_filename = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_filename)
    return screenshot_filename

def capture_face():
    # Call the faceCapture.py script to capture a face image
    subprocess.run(["python", "faceCapture.py"], check=True)
    # Assuming the latest image is the one we need
    face_capture_dir = "face_captures"
    latest_face_capture = max(
        [os.path.join(face_capture_dir, f) for f in os.listdir(face_capture_dir)],
        key=os.path.getctime
    )
    return latest_face_capture

def transcribe(screenshot_path, face_capture_path):
    # Placeholder for the transcribe function
    # Implement your transcription logic here
    print(f"Transcribing {screenshot_path} and {face_capture_path}")
    return "Transcription result"

@app.route('/check_focus', methods=['GET'])
def check_focus():
    try:
        # Capture screenshot and face image
        screenshot_path = capture_screenshot()
        face_capture_path = capture_face()

        # Call the transcribe function
        result = transcribe(screenshot_path, face_capture_path)

        return jsonify({"status": "success", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
