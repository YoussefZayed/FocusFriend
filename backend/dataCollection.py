import pyautogui
import time
import os
from datetime import datetime

# Create a directory to save screenshots
screenshot_dir = "screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

try:
    while True:
        # Get the current time for the filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # Define the screenshot filename
        screenshot_filename = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")
        # Take a screenshot
        screenshot = pyautogui.screenshot()
        # Save the screenshot
        screenshot.save(screenshot_filename)
        print(f"Screenshot saved as {screenshot_filename}")
        # Wait for 5 seconds
        time.sleep(5)
except KeyboardInterrupt:
    print("Screenshot capture stopped.")