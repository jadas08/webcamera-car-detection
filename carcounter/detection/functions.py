import cv2
import datetime
import os
from .constants import PICTURE_OUTPUT, MODELS_PATH
from pathlib import Path
import matplotlib.pyplot as plt
from .live_detection import detect_cars
from carcounter import settings

def capture_image():
    cap = cv2.VideoCapture(0)
    success, frame = cap.read()
    if success:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Capture_{timestamp}.jpg"
        raw_folder_path = os.path.join(settings.MEDIA_ROOT, 'raw')
        os.makedirs(raw_folder_path, exist_ok=True)  # Create the raw folder if it doesn't exist
        image_path = os.path.join(raw_folder_path, filename)
        cv2.imwrite(image_path, frame)
    cap.release()
    return os.path.join('raw', filename).replace('\\', '/')
####
def find_cars(file_location):
    print('here2')
    net = cv2.dnn.readNet(str(MODELS_PATH / 'yolov3.weights'), str(MODELS_PATH / 'yolov3.cfg'))
    layer_names = net.getLayerNames()

    with open(str(MODELS_PATH / "coco.names"), "r") as f:
        classes = [line.strip() for line in f.readlines()]
    frame = cv2.imread(file_location)
    if frame is not None:
        current_car_detection = detect_cars(frame, net, classes)
        processed_frame = current_car_detection[0]
        detection_count = current_car_detection[1]
        # Create the processed folder if it doesn't exist
        processed_folder_path = os.path.join(settings.MEDIA_ROOT, 'processed')
        #os.makedirs(processed_folder_path, exist_ok=True)
        # Save the processed image in the processed folder
        filename = f'Processed_{os.path.splitext(os.path.basename(file_location))[0]}.jpg'
        processed_image_path = os.path.join(processed_folder_path, filename)
        cv2.imwrite(processed_image_path, processed_frame)
    else:
        print(f"Error: Unable to load image at {file_location}")

    # Return the path for processed image relative to MEDIA_ROOT
    #return os.path.join('processed', filename)
    return os.path.join('processed', filename).replace('\\', '/'), detection_count
