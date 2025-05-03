import pyautogui
import os
from datetime import datetime

# Create a directory to save device screenshots
screenshot_dir = "device_screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

# Capture a screenshot of the entire device screen
screenshot = pyautogui.screenshot()

# Get the current time for the filename
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# Define the screenshot filename
screenshot_filename = os.path.join(screenshot_dir, f"device_screenshot_{timestamp}.png")

# Save the screenshot
screenshot.save(screenshot_filename)
print(f"Device screenshot saved as {screenshot_filename}") 