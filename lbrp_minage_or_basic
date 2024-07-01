import time
import win32api
import win32con
import win32gui


def find_window(title):
    hwnd = win32gui.FindWindow(None, title)
    if hwnd == 0:
        raise Exception(f"{title} n'a pas été trouvé ! Tu l'as sûrement mal écrit ! ")
    return hwnd


def hold_left_click(hwnd, x, y, duration):
    l_param = (y << 16) | x
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l_param)
    time.sleep(duration)
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, l_param)


if __name__ == "__main__":
    window_title = "Garry's Mod (x64)"
    hwnd = find_window(window_title)
    pos_actu = win32api.GetCursorPos()
    x, y = pos_actu
    temps = 4 * 60
    hold_left_click(hwnd, x, y, temps)
