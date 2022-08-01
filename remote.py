import win32gui
import win32ui
import win32con
import win32api
import win32com.client
from PIL import Image
import io
import requests
import time
import argparse

global host
host = "http://192.168.0.241:5000"


def main(key, secret):
    r = requests.post(host+'/new_session',
                      json={'_key': key, '_secret': secret})
    if r.status_code != 200:
        print('Server not avaliable.')
        return
    else:
        print('Connected to Server. Awating remote commands.......')

    shell = win32com.client.Dispatch('WScript.Shell')
    PREV_IMG = None
    while True:
        mem_dc, screenshot = handle_video_feed(PREV_IMG, host, key)
        # events
        handle_events(host, key, mem_dc, screenshot, shell)
        time.sleep(0.2)


def handle_video_feed(PREV_IMG, host, key):
    hdesktop = win32gui.GetDesktopWindow()

    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    # device context
    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)

    # memory context
    mem_dc = img_dc.CreateCompatibleDC()

    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(img_dc, width, height)
    mem_dc.SelectObject(screenshot)

    bmpinfo = screenshot.GetInfo()

    # copy into memory
    mem_dc.BitBlt((0, 0), (width, height), img_dc,
                  (left, top), win32con.SRCCOPY)

    bmpstr = screenshot.GetBitmapBits(True)

    pillow_img = Image.frombytes('RGB',
                                 (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                                 bmpstr, 'raw', 'BGRX')

    with io.BytesIO() as image_data:
        pillow_img.save(image_data, 'PNG')
        image_data_content = image_data.getvalue()

    if image_data_content != PREV_IMG:
        files = {}
        filename = str(round(time.time()*1000))+'_'+key
        files[filename] = ('img.png', image_data_content,
                           'multipart/form-data')

        try:
            requests.post(host+'/capture_post', files=files)
        except Exception:
            pass

        PREV_IMG = image_data_content
    else:
        # print('no desktop change')
        pass
    return mem_dc, screenshot


def handle_events(host, key, mem_dc, screenshot, shell):
    try:
        r = requests.post(host+'/events_get', json={'_key': key})
        data = r.json()
        for e in data['events']:
            print(e)

            if e['type'] == 'click':
                win32api.SetCursorPos((e['x'], e['y']))
                time.sleep(0.1)
                win32api.mouse_event(
                    win32con.MOUSEEVENTF_LEFTDOWN, e['x'], e['y'], 0, 0)
                time.sleep(0.02)
                win32api.mouse_event(
                    win32con.MOUSEEVENTF_LEFTUP, e['x'], e['y'], 0, 0)

            if e['type'] == 'keydown':
                cmd = ''

                if e['shiftKey']:
                    cmd += '+'

                if e['ctrlKey']:
                    cmd += '^'

                if e['altKey']:
                    cmd += '%'

                if len(e['key']) == 1:
                    cmd += e['key'].lower()
                else:
                    cmd += '{'+e['key'].upper()+'}'

                print(cmd)
                shell.SendKeys(cmd)

    except Exception as err:
        print(err)

    # screenshot.SaveBitmapFile(mem_dc, 'screen.bmp')
    # free
    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='pyRD')
    parser.add_argument('key', help='access key', type=str)
    parser.add_argument('secret', help='acess pass', type=str)
    args = parser.parse_args()
    main(args.key, args.secret)
