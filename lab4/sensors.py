import argparse
import threading
import time
import cv2
import logging
import sys
import queue

logging.basicConfig(filename='app.log', level=logging.INFO)
flag = True

class Sensor:
    def get(self):
        raise NotImplementedError("Subclasses must implement method get()")

class SensorX(Sensor):
    """Sensor X"""
    def __init__(self, delay: float):
        self._delay = delay
        self._data = 0

    def get(self, frame=None) -> int:
        time.sleep(self._delay)
        self._data += 1
        return self._data

class SensorCam(Sensor):
    def __init__(self, cam, res):
        if cam == 'default':
            self.cap = cv2.VideoCapture(0)
        else:
            self.cap = cv2.VideoCapture(int(cam))
        self.cap.set(3, res[0])
        self.cap.set(4, res[1])

    def get(self):
        ret, frame = self.cap.read()
        return frame, ret

    def release(self):
        self.cap.release()

class WindowImage:
    def __init__(self, freq):
        self.freq = freq
        cv2.namedWindow("window")

    def show(self, img, s1, s2, s3):
        x = 50
        y = 50
        text1 = f"Sensor 1: {s1}"
        text2 = f"Sensor 2: {s2}"
        text3 = f"Sensor 3: {s3}"
        cv2.putText(img, text1, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(img, text2, (x, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(img, text3, (x, y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("window", img)

    def close(self):
        cv2.destroyWindow("window")

def process_sensor(que, sensor):
    global flag
    while flag:
        frame = que.get()
        new_sens = sensor.get(frame)
        que.put(frame)  # Put the frame back after processing

def main(args):
    global flag
    shapes = (int(args.res.split('*')[0]), int(args.res.split('*')[1]))
    sensor1 = SensorX(1)
    sensor2 = SensorX(0.1)
    sensor3 = SensorX(0.01)
    window = WindowImage(args.freq)
    camera = SensorCam(args.cam, shapes)

    if not camera.cap.isOpened():
        logging.info('The camera is turned off.')
        print('The camera is turned off.')
        camera.release()
        window.close()
        sys.exit()

    frame_queue = queue.Queue(maxsize=1)
    frame_queue.put(None)  # Initializing the queue with None

    thread1 = threading.Thread(target=process_sensor, args=(frame_queue, sensor1))
    thread2 = threading.Thread(target=process_sensor, args=(frame_queue, sensor2))
    thread3 = threading.Thread(target=process_sensor, args=(frame_queue, sensor3))

    thread1.start()
    thread2.start()
    thread3.start()

    while True:
        frame, ret = camera.get()
        if not ret or not camera.cap.isOpened() or not camera.cap.grab():
            logging.info('The camera had turned off.')
            print('The camera had turned off.')
            camera.release()
            window.close()
            flag = False
            sys.exit()

        frame_queue.put(frame)  # Put the frame in the queue for sensors to process

        sensor1_data = sensor1.get(frame)
        sensor2_data = sensor2.get(frame)
        sensor3_data = sensor3.get(frame)

        window.show(frame, sensor1_data, sensor2_data, sensor3_data)
        time.sleep(1 / window.freq)

        if cv2.waitKey(1) == ord('q'):
            camera.release()
            window.close()
            flag = False
            sys.exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cam', type=str, default='default', help='Camera name')
    parser.add_argument('--res', type=str, default='1280*720', help='Camera resolution')
    parser.add_argument('--freq', type=int, default=60, help='Output frequency')
    args = parser.parse_args()
    main(args)
