# webcamera-car-detection
### Introduction
This Django application is designed to detect and count cars using a webcam. Leveraging advanced computer vision techniques, the app captures images from the webcam, processes them to detect vehicles, and maintains a count of the cars identified.
### Installation and Setup

#### Prerequisites
- Python (3.x recommended)
- pip (Python package manager)
- Virtual environment (optional, but recommended)

#### Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/jadas08/webcamera-car-detection.git
   cd your-repository-name
2. **Locally add files for the yolo model in the trained-models folder**:
   You will need yolov3.weights, yolov3.cfg and coco.names. You will also need two folders in the media folder - raw and processed - these will be used as media root.
3. **Install requirements**:
   ```bash
   pip install -r requirements.txt

3. **Make migrations and run the server**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
4. **Go to see the app**:
   Open your browser and navigate to http://localhost:8000.
  

### Features
Real-time Car Detection: Utilizes the webcam to capture live footage and detect cars in real-time.

Car Counting: Keeps a tally of the number of cars detected in each image.

Image Processing: Processes and stores images for both raw captures and after car detection.

Web Interface: Django-based web interface for easy interaction with the application.

### How It Works
Taking Pictures: The application captures images from the webcam when initiated by the user.

Car Detection: Each captured image is processed to detect cars. This is done using the detect_cars function which employs the YOLOv3 model for object detection.

Display Results: The application displays the processed image along with the count of cars detected.
### Views
take_picture: Handles the image capture process.

picture_taken: Displays the captured image and the results of the car detection.

list_media_files: Lists all the raw and processed images stored by the application.

### Upcoming Features
Scheduler for Regular Captures: Future development includes adding a scheduler to automate the image capture and car detection process at regular intervals.

Later - Raspberry PI integration.
### Models
ImageRecord: Stores details of each image capture session, including time of capture, raw and processed image paths, and the success status of capture and detection.
