from django.shortcuts import render, redirect, HttpResponse
#from .functions import capture_image, find_cars
from django.conf import settings
from django.urls import reverse
from urllib.parse import quote, unquote
from django.http import Http404
import os
import cv2
from .constants import *
import datetime
from .live_detection import detect_cars

""" def take_picture(request):
    if request.method == 'POST':
        relative_image_path = capture_image()
        image_path_quoted = quote(relative_image_path)
        picture_taken_url = reverse('picture_taken', kwargs={'image_path': image_path_quoted})
        return redirect(picture_taken_url)
    else:
        return render(request, 'take_picture.html') """

""" def take_picture(request):
    if request.method == 'POST':
        current_detection = ImageAnalyzer()
        current_detection.capture_image()
        if current_detection.success_capture:
            # Store the necessary data in the session
            request.session['image_path_quoted'] = current_detection.image_path_quoted
            # Redirect to the next view
            return redirect('picture_taken')
    else:
        return render(request, 'take_picture.html')



def picture_taken(request, image_path):
    image_path_decoded = unquote(image_path).replace('\\', '/')
    file_system_path = convert_to_file_system_path(image_path_decoded).replace('\\', '/')
    print(f"image_path_decoded:{image_path_decoded}")
    print(f"file_system_path:{file_system_path}")
    try:
        detection_results = find_cars(file_system_path)
        processed_image_relative_path = detection_results[0]
        processed_image_web_path = settings.MEDIA_URL + processed_image_relative_path.replace('\\', '/')
    except FileNotFoundError:
        raise Http404(f"The image file was not found at the expected path: {file_system_path}")
    except IndexError as e:
        raise Http404(f"An error occurred during processing.{e}")

    return render(request, 'picture_display.html', {
        'image_path': processed_image_web_path,
        'car_detection_result': detection_results[1]
    }) """

from .models import ImageRecord
from django.shortcuts import get_object_or_404

def take_picture(request):
    if request.method == 'POST':
        image_record = ImageRecord()
        image_record.capture_and_detect()  # Capture and process the image
        if image_record.success_capture:
            # Redirect to the 'picture_taken' view with the ID of the ImageRecord instance
            return redirect('picture_taken', image_record_id=image_record.id)
    else:
        return render(request, 'take_picture.html')

def picture_taken(request, image_record_id):
    image_record = get_object_or_404(ImageRecord, id=image_record_id)
    # Assuming find_cars method updates the model after detecting cars
    detection_count = image_record.find_cars(image_record.raw_image.path)
    formatted_string = ', '.join([f'{key}: {value}' for key, value in detection_count.items()])
    if image_record.success_detection:
        return render(request, 'picture_display.html', {
            'image_path': image_record.processed_image.url,
            'car_detection_result': formatted_string
        })
    else:
        # Handle the error case where detection was not successful
        return HttpResponse("Error: Car detection was not successful.")



def list_media_files(request):
    raw_files = os.listdir(os.path.join(settings.MEDIA_ROOT, 'raw'))
    processed_files = os.listdir(os.path.join(settings.MEDIA_ROOT, 'processed'))

    context = {
        'raw_files': raw_files,
        'processed_files': processed_files
    }

    return render(request, 'navbar.html', context)


#functions
def convert_to_file_system_path(web_path):
    return os.path.join(settings.MEDIA_ROOT, web_path)

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
        processed_folder_path = os.path.join(settings.MEDIA_ROOT, 'processed')
        filename = f'Processed_{os.path.splitext(os.path.basename(file_location))[0]}.jpg'
        processed_image_path = os.path.join(processed_folder_path, filename)
        cv2.imwrite(processed_image_path, processed_frame)
    else:
        print(f"Error: Unable to load image at {file_location}")

    return os.path.join('processed', filename).replace('\\', '/'), detection_count


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


