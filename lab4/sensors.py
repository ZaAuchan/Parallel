import argparse
import threading
import time
import cv2
import logging
import sys

logging.basicConfig(filename='app.log', level=logging.INFO)

class Sensor:
    def get(self, frame=None):
        raise NotImplementedError("Subclasses must implement method get()")

class SensorX(Sensor):
    """Sensor X"""
    def __init__(self, delay: float):
        self._delay = delay
        self._data = 0

    def get(self, frame=None) -> int:
        time.sleep(self._delay)  # Симуляция задержки получения данных
        self._data += 1
        return self._data

class FastSensorX(SensorX):
    """Fast Sensor X"""
    def get(self, frame=None) -> int:
        # Уменьшение задержки для ускорения работы сенсора
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
        text2 = f"Sensor 2: {s2 // 10}"
        text3 = f"Sensor 3: {s3}"
        cv2.putText(img, text1, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(img, text2, (x, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(img, text3, (x, y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("window", img)

    def close(self):
        cv2.destroyWindow("window")

def process_sensor(sensor, interval, result_list, index, stop_event):
    while not stop_event.is_set():
        result_list[index] = sensor.get()
        time.sleep(interval)

def main(args):
    shapes = (int(args.res.split('*')[0]), int(args.res.split('*')[1]))
    sensor1 = SensorX(1)                # Интервал 1 секунда
    sensor2 = FastSensorX(0.1)          # Интервал 0.1 секунда, ускоренный сенсор
    sensor3 = FastSensorX(0.01)         # Интервал 0.01 секунда
    window = WindowImage(args.freq)
    camera = SensorCam(args.cam, shapes)

    if not camera.cap.isOpened():
        logging.info('The camera is turned off.')
        print('The camera is turned off.')
        camera.release()
        window.close()
        sys.exit()

    sensor_data = [0, 0, 0]  # Shared list to store sensor data
    stop_event = threading.Event()

    thread1 = threading.Thread(target=process_sensor, args=(sensor1, 1, sensor_data, 0, stop_event))
    thread2 = threading.Thread(target=process_sensor, args=(sensor2, 0.01, sensor_data, 1, stop_event))
    thread3 = threading.Thread(target=process_sensor, args=(sensor3, 0.01, sensor_data, 2, stop_event))

    thread1.start()
    thread2.start()
    thread3.start()

    try:
        while True:
            start_time = time.time()
            frame, ret = camera.get()
            if not ret:
                logging.info('The camera had turned off.')
                print('The camera had turned off.')
                break

            window.show(frame, sensor_data[0], sensor_data[1], sensor_data[2])

            if cv2.waitKey(1) == ord('q'):
                break

            # Ensure the loop runs at the specified frequency
            elapsed_time = time.time() - start_time
            sleep_time = max(1 / window.freq - elapsed_time, 0)
            time.sleep(sleep_time)
    finally:
        stop_event.set()
        camera.release()
        window.close()
        thread1.join()
        thread2.join()
        thread3.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cam', type=str, default='default', help='Camera name')
    parser.add_argument('--res', type=str, default='1280*720', help='Camera resolution')
    parser.add_argument('--freq', type=int, default=60, help='Output frequency')
    args = parser.parse_args()
    main(args)
