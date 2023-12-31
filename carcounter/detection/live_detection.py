import cv2
import numpy as np
from pathlib import Path


MODELS_DIR = Path('trained-models')


# Function to get the output of the layers
def get_output_layers(net):
    layer_names = net.getLayerNames()
    return [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]


# Include 'classes' as an additional parameter
def draw_bounding_box(img, class_id, confidence, x, y, x_plus_w, y_plus_h, classes):
    label = str(classes[class_id])
    if label == "car":
        color = (0, 255, 0)
    elif label == 'person':
        color = (255, 0, 0)
    elif label == 'dog':
        color = (0, 0, 255)
    if label in ['car', 'person', 'dog']:
        cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)
        cv2.putText(img, label, (x-10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


def detect_cars(frame, net, classes):
    Width = frame.shape[1]
    Height = frame.shape[0]
    scale = 0.00392

    # Create a 4D blob from a frame.
    blob = cv2.dnn.blobFromImage(frame, scale, (416, 416), (0, 0, 0), True, crop=False)

    # Set the input to the network
    net.setInput(blob)

    # Run the forward pass to get output of the output layers
    outs = net.forward(get_output_layers(net))

    # Initialization
    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4

    # For each detetion from each output layer get the confidence, class id, bounding box params
    # and ignore weak detections (confidence < 0.5)
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])

    # Apply non-max suppression to remove overlapping bounding boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    # Go through the detections remaining after nms and draw bounding box
    indices = np.array(indices).flatten()

    # Go through the detections remaining after nms and draw bounding box
    for i in indices:
        box = boxes[i]
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]
        draw_bounding_box(frame, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h), classes)
    
    detection_count = dict()
    for object_type in ['car', 'person', 'dog']:
        detection_count[object_type] = sum(1 for i in indices if class_ids[i] == classes.index(object_type))
    
    
    return frame, detection_count
