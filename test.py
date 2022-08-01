import win32con
import win32api
import win32com.client
import time


def main():
    shell = win32com.client.Dispatch('WScript.Shell')
    time.sleep(3)
    cmd = "Akash"
    for c in cmd:
        shell.SendKeys("^c")
        time.sleep(.3)

    '''
    x, y = 0, 0
    while True:
        win32api.SetCursorPos((x, y))
        x += 1
        y += 1
        x = x % 1920
        y = y % 1080
        time.sleep(0.01)
    '''


if __name__ == "__main__":
    main()
