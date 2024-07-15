import numpy as np
import win32gui, win32ui, win32con
from PIL import Image
from time import sleep, time
import cv2 as cv
import os
from pynput.mouse import Button, Controller
import random


class WindowCapture:
    w = 0
    h = 0
    hwnd = None

    def __init__(self, window_name):
        self.hwnd = win32gui.FindWindow(None, window_name)
        if not self.hwnd:
            raise Exception('Window not found: {}'.format(window_name))

        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        border_pixels = 8
        titlebar_pixels = 30
        self.w = self.w - (border_pixels * 2)
        self.h = self.h - titlebar_pixels - border_pixels
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

    def get_screenshot(self):
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        img = img[..., :3]
        img = np.ascontiguousarray(img)

        return img

    def generate_image_dataset(self):
        if not os.path.exists("images"):
            os.mkdir("images")
        while (True):
            img = self.get_screenshot()
            im = Image.fromarray(img[..., [2, 1, 0]])
            im.save(f"./images/img_{len(os.listdir('images'))}.jpeg")
            sleep(1)

    def get_window_size(self):
        return (self.w, self.h)


class ImageProcessor:
    W = 0
    H = 0
    net = None
    ln = None
    classes = {}
    colors = []

    def __init__(self, img_size, cfg_file, weights_file):
        np.random.seed(42)
        self.net = cv.dnn.readNetFromDarknet(cfg_file, weights_file)
        self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
        self.ln = self.net.getLayerNames()
        self.ln = [self.ln[i - 1] for i in self.net.getUnconnectedOutLayers()]
        self.W = img_size[0]
        self.H = img_size[1]

        with open('yolov4-tiny/obj.names', 'r') as file:
            lines = file.readlines()
        for i, line in enumerate(lines):
            self.classes[i] = line.strip()

        self.colors = [
            (0, 255, 0),
            (0, 0, 255),
            (255, 0, 0),
            (255, 255, 0),
            (255, 0, 255),
            (0, 255, 255)
        ]

    def proccess_image(self, img):

        blob = cv.dnn.blobFromImage(img, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.ln)
        outputs = np.vstack(outputs)

        coordinates = self.get_coordinates(outputs, 0.5)

        self.draw_identified_objects(img, coordinates)

        return coordinates

    def get_coordinates(self, outputs, conf):

        boxes = []
        confidences = []
        classIDs = []

        for output in outputs:
            scores = output[5:]

            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > conf:
                x, y, w, h = output[:4] * np.array([self.W, self.H, self.W, self.H])
                p0 = int(x - w // 2), int(y - h // 2)
                boxes.append([*p0, int(w), int(h)])
                confidences.append(float(confidence))
                classIDs.append(classID)

        indices = cv.dnn.NMSBoxes(boxes, confidences, conf, conf - 0.1)

        if len(indices) == 0:
            return []

        coordinates = []
        for i in indices.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            coordinates.append(
                {'x': x, 'y': y, 'w': w, 'h': h, 'class': classIDs[i], 'class_name': self.classes[classIDs[i]]})
        return coordinates

    def draw_identified_objects(self, img, coordinates):
        for coordinate in coordinates:
            x = coordinate['x']
            y = coordinate['y']
            w = coordinate['w']
            h = coordinate['h']
            classID = coordinate['class']

            color = self.colors[classID]

            cv.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv.putText(img, self.classes[classID], (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv.imshow('DETECTED OBJECTS', img)


from pynput.mouse import Button, Controller

mouse = Controller()

window_name = "BlueStacks App Player"
cfg_file_name = "./yolov4-tiny/yolov4-tiny-custom.cfg"
weights_file_name = "yolov4-tiny-custom_last.weights"

wincap = WindowCapture(window_name)
improc = ImageProcessor(wincap.get_window_size(), cfg_file_name, weights_file_name)

screen_height = 560
border_pixels = 8
titlebar_pixels = 33
velocity_multiplyer = 2

previous_coordinates = []
new_coordinates = []

sleep(4)

while (True):

    ss = wincap.get_screenshot()
    previous_coordinates = improc.proccess_image(ss)
    previous_coordinates = [c for c in previous_coordinates if c["class_name"] == "fruit"]

    ss = wincap.get_screenshot()
    new_coordinates = improc.proccess_image(ss)
    new_coordinates = [c for c in new_coordinates if c["class_name"] == "fruit"]

    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

    if len(previous_coordinates) == 0 or len(new_coordinates) == 0:
        continue

    coordinates_to_hit = []

    for new_fruit in new_coordinates:
        center_x = new_fruit['x'] + (new_fruit['w'] // 2) + border_pixels
        center_y = new_fruit['y'] + (new_fruit['h'] // 2) + titlebar_pixels
        for previous_fruit in previous_coordinates:
            if not previous_fruit['x'] < center_x < (previous_fruit['x'] + previous_fruit['w']):
                continue
            if not previous_fruit['y'] < center_y < (previous_fruit['y'] + previous_fruit['h']):
                continue
            previous_center_x = previous_fruit['x'] + (previous_fruit['w'] // 2) + border_pixels
            previous_center_y = previous_fruit['y'] + (previous_fruit['h'] // 2) + titlebar_pixels
            coordinates_to_hit.append({
                "x": center_x + (center_x - previous_center_x) * velocity_multiplyer,
                "y": center_y + (center_y - previous_center_y) * velocity_multiplyer
            })
            break

    if len(coordinates_to_hit) == 0:
        continue

    if len(coordinates_to_hit) == 1:
        coordinates_to_hit = coordinates_to_hit[0]

        initial_x = coordinates_to_hit["x"]
        initial_y = min(screen_height, coordinates_to_hit["y"]) - 70
        movement_x = 0
        movement_y = 140

    else:
        leftmost_fruit = min(coordinates_to_hit, key=lambda x: x['x'])
        rightmost_fruit = max(coordinates_to_hit, key=lambda x: x['x'])

        initial_x = max(30, leftmost_fruit["x"])
        initial_y = max(100, leftmost_fruit["y"])
        movement_x = rightmost_fruit["x"] - initial_x
        movement_y = rightmost_fruit["y"] - initial_y

    mouse.position = (initial_x, initial_y)
    mouse.press(Button.left)
    sleep(0.05)
    mouse.move(movement_x, movement_y)
    sleep(0.05)
    mouse.move(-movement_x, -movement_y)
    sleep(0.05)
    mouse.release(Button.left)

print('Finished.')
