import win32gui
import win32con
import pyautogui
import time
import threading
import os

window_name = "Garry's Mod (x64)"
images_to_search = [r"C:\Users\PC GAMER\Desktop\gmod_lbrp\seau_plein.png"]
imageOffset = 25

def find_and_bring_to_front(window_name):
    hwnd = win32gui.FindWindow(None, window_name)

    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        print(f"La fenêtre '{window_name}' a été mise en avant.")
        return True
    else:
        print(f"La fenêtre '{window_name}' n'a pas été trouvée.")
        return False

def check_images():
    while True:
        for image_path in images_to_search:
            try:
                pos = pyautogui.locateOnScreen(image_path, confidence=0.7)
                if pos:
                    pyautogui.moveTo(pos[0] + imageOffset, pos[1] + imageOffset)
                    pyautogui.click()
                    print(f"JE CLIQUE SUR : {image_path} !")
                    os._exit(0)
            except:
                print(f"{image_path} n'est pas là !")
                time.sleep(1)

def simulate_left_clicks(duration):
    end_time = time.time() + duration
    while time.time() < end_time:
        pyautogui.click()
        time.sleep(0.1)

def main():
    image_thread = threading.Thread(target=check_images)
    image_thread.daemon = True
    image_thread.start()

    while True:
        if find_and_bring_to_front(window_name):
            time.sleep(5)
            simulate_left_clicks(3 * 60)
        else:
            time.sleep(5)

if __name__ == "__main__":
    main()
