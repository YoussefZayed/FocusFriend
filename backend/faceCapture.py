import cv2
import time
import os
from datetime import datetime

# Create a directory to save face captures
face_capture_dir = "face_captures"
os.makedirs(face_capture_dir, exist_ok=True)

# Initialize the main camera (index 0)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open the main camera.")
else:
    try:
        while True:
            # Capture a frame from the camera
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                break

            # Get the current time for the filename
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            # Define the image filename
            image_filename = os.path.join(face_capture_dir, f"face_{timestamp}.png")
            
            # Save the captured frame
            cv2.imwrite(image_filename, frame)
            print(f"Face capture saved as {image_filename}")

            # Wait for 5 seconds
            time.sleep(5)
    except KeyboardInterrupt:
        print("Face capture stopped.")
    finally:
        # Release the camera
        cap.release()
        cv2.destroyAllWindows()
