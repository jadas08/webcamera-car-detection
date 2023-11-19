from django.db import models
import cv2
import os
from carcounter import settings
from urllib.parse import quote
from .constants import *
from .live_detection import detect_cars
import uuid
import time

def generate_unique_filename(prefix):
    """Generate a unique filename using UUID."""
    return f"{prefix}_{uuid.uuid4()}.jpg"

class ImageRecord(models.Model):
    time_created = models.DateTimeField(auto_now_add=True)
    raw_image = models.ImageField(upload_to='raw/')
    processed_image = models.ImageField(upload_to='processed/', null=True, blank=True)
    raw_name = models.CharField(default=generate_unique_filename("Capture"), max_length=255)
    processed_name = models.CharField(default=generate_unique_filename("Processed_Capture"), max_length=255)
    success_capture = models.BooleanField(default=False)
    success_detection = models.BooleanField(default=False)
    detection_count = models.CharField(null=True, blank=True, max_length=255)
    image_path_quoted = models.CharField(null=True, max_length=1000)

    def __str__(self):
        return f"Image taken at {self.time_created.strftime('%Y-%m-%d %H:%M:%S')}"

    def capture_and_detect(self):
        cap = cv2.VideoCapture(1)
        time.sleep(1)
        success, frame = cap.read()
        cap.release()
        if success:
            self.success_capture = True
            raw_folder_path = os.path.join(settings.MEDIA_ROOT, 'raw')
            image_path = os.path.join(raw_folder_path, self.raw_name)
            cv2.imwrite(image_path, frame)
            self.raw_image = os.path.relpath(image_path, settings.MEDIA_ROOT)  # Set the relative path
            self.image_path_quoted = quote(os.path.join('raw', self.raw_name).replace('\\', '/'))
            self.save()
        else:
            print("Error: Unable to capture image.")

    def find_cars(self, file_location):
        try:
            net = cv2.dnn.readNet(str(MODELS_PATH / 'yolov3.weights'), str(MODELS_PATH / 'yolov3.cfg'))
            with open(str(MODELS_PATH / "coco.names"), "r") as f:
                classes = [line.strip() for line in f.readlines()]
            frame = cv2.imread(file_location)
            if frame is not None:
                current_car_detection = detect_cars(frame, net, classes)
                processed_frame = current_car_detection[0]
                detection_count = current_car_detection[1]
                processed_folder_path = os.path.join(settings.MEDIA_ROOT, 'processed')
                filename = self.processed_name
                processed_image_path = os.path.join(processed_folder_path, filename)
                cv2.imwrite(processed_image_path, processed_frame)
                self.success_detection = True
                image_path = os.path.join(processed_folder_path, self.processed_name)
                self.processed_image = os.path.relpath(image_path, settings.MEDIA_ROOT)
                self.detection_count = detection_count
                self.save()
            else:
                print(f"Error: Unable to load image at {file_location}")
        except Exception as e:
            print(f"Error in find_cars: {e}")
        return detection_count

""" 

class ImageAnalyzer:
    def __init__(self) -> None:
        self.time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.raw_name = f"Capture_{self.time}.jpg"
        self.processed_name = f"Processed_Capture_{self.time}.jpg"
        self.success_capture = False
        self.success_detection = False
        self.result = None
    def capture_image(self):
        cap = cv2.VideoCapture(0)
        success, frame = cap.read()
        if success:
            self.success_capture = True
            #filename = f"Capture_{timestamp}.jpg"
            raw_folder_path = os.path.join(settings.MEDIA_ROOT, 'raw')
            #os.makedirs(raw_folder_path, exist_ok=True)  # Create the raw folder if it doesn't exist
            image_path = os.path.join(raw_folder_path, self.raw_name)
            cv2.imwrite(image_path, frame)
        cap.release()
        self.image_path_quoted = quote(os.path.join('raw', self.raw_name).replace('\\', '/'))
        return self
    def find_cars(self, file_location):
        net = cv2.dnn.readNet(str(MODELS_PATH / 'yolov3.weights'), str(MODELS_PATH / 'yolov3.cfg'))
        with open(str(MODELS_PATH / "coco.names"), "r") as f:
            classes = [line.strip() for line in f.readlines()]
        frame = cv2.imread(file_location)
        if frame is not None:
            current_car_detection = detect_cars(frame, net, classes)
            processed_frame = current_car_detection[0]
            detection_count = current_car_detection[1]
            processed_folder_path = os.path.join(settings.MEDIA_ROOT, 'processed')
            filename = f'Processed_{os.path.splitext(os.path.basename(file_location))[0]}.jpg'
            filename = self.processed_name
            processed_image_path = os.path.join(processed_folder_path, filename)
            cv2.imwrite(processed_image_path, processed_frame)
            self.success_detection = True
        else:
            print(f"Error: Unable to load image at {file_location}")
        self.result = detection_count
        return os.path.join('processed', filename).replace('\\', '/'), detection_count

 """