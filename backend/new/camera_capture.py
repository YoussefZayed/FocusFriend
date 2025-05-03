import cv2
import os
from datetime import datetime

# Create a directory to save camera captures
camera_capture_dir = "camera_captures"
os.makedirs(camera_capture_dir, exist_ok=True)

# Initialize the main camera (index 0)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open the main camera.")
else:
    try:
        # Capture a frame from the camera
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
        else:
            # Get the current time for the filename
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            # Define the image filename
            image_filename = os.path.join(camera_capture_dir, f"camera_capture_{timestamp}.png")
            
            # Save the captured frame
            cv2.imwrite(image_filename, frame)
            print(f"Camera capture saved as {image_filename}")
    finally:
        # Release the camera
        cap.release()
        cv2.destroyAllWindows() 