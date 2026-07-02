import cv2
from config import CONFIDENCE_THRESHOLD

class PersonDetector:

    def __init__(self):

        self.net = cv2.dnn.readNetFromCaffe(
            "models/MobileNetSSD_deploy.prototxt",
            "models/MobileNetSSD_deploy.caffemodel"
        )

        self.classes = [
            "background", "aeroplane", "bicycle", "bird", "boat",
            "bottle", "bus", "car", "cat", "chair", "cow",
            "diningtable", "dog", "horse", "motorbike", "person",
            "pottedplant", "sheep", "sofa", "train", "tvmonitor"
        ]

    def detect(self, frame):

        h, w = frame.shape[:2]

        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            0.007843,
            (300, 300),
            127.5
        )

        self.net.setInput(blob)

        detections = self.net.forward()

        persons_found = 0

        boxes = []

        for i in range(detections.shape[2]):

            confidence = detections[0, 0, i, 2]

            if confidence > CONFIDENCE_THRESHOLD:

                class_id = int(detections[0, 0, i, 1])

                if self.classes[class_id] == "person":

                    persons_found += 1

                    box = detections[0, 0, i, 3:7] * [w, h, w, h]

                    x1, y1, x2, y2 = box.astype("int")

                    boxes.append(
                        (x1, y1, x2, y2, confidence)
                    )

        return persons_found, boxes




