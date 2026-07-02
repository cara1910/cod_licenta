import os
import cv2
import time
from datetime import datetime
from manager_stocare import cleanup_storage_if_needed
from camera import Camera
from detection import PersonDetector
from database import init_db, save_detection
from email_notifier import send_email_to_all_users

from config import (
    IMAGE_FOLDER,
    SAVE_COOLDOWN_SECONDS,
    DETECT_EVERY_N_FRAMES
)

WINDOW_NAME = "Sistem supraveghere"

def draw_boxes(frame, boxes):
    for x1, y1, x2, y2, confidence in boxes:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        label = f"PERSON {confidence * 100:.1f}%"

        cv2.putText(
            frame,
            label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

def get_today_folder():
    today = datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(IMAGE_FOLDER, today)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def save_event(frame, person_count):
    folder_path = get_today_folder()

    now = datetime.now()
    filename = f"detection_{now.strftime('%H-%M-%S')}.jpg"
    image_path = os.path.join(folder_path, filename)

    cv2.imwrite(image_path, frame)

    save_detection(
        image_path=image_path,
        detected_at=now.strftime("%Y-%m-%d %H:%M:%S"),
        person_count=person_count
    )

    print(f"[SAVE] {image_path} | persoane: {person_count}")


def should_save_image(current_count, previous_count, last_save_time):
    if current_count == 0:
        return False

    if previous_count == 0:
        return True

    if current_count > previous_count:
        return True

    if last_save_time is None:
        return True

    elapsed = time.time() - last_save_time

    return elapsed >= SAVE_COOLDOWN_SECONDS


def handle_email_alerts(current_count, previous_count):
    if previous_count == 0 and current_count > 0:
        send_email_to_all_users(
            "Alertă birou",
            "A fost detectată o persoană în birou."
        )

    elif current_count > previous_count:
        difference = current_count - previous_count

        if difference == 1:
            message = "A mai intrat o persoană în birou."
        else:
            message = f"Au mai intrat {difference} persoane în birou."

        send_email_to_all_users(
            "Alertă birou",
            message
        )

    elif previous_count > 0 and current_count == 0:
        send_email_to_all_users(
            "Birou liber",
            "Nu mai este nicio persoană în birou."
        )


def main():
    init_db()

    camera = Camera()
    detector = PersonDetector()

    frame_counter = 0
    previous_person_count = 0
    current_person_count = 0
    last_save_time = None
    last_boxes = []

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 640, 480)

    print("Sistem de supraveghere pornit.")
    print("Apasă Q pentru oprire.")

    try:
        while True:
            frame = camera.get_frame()
            frame_counter += 1

            if frame_counter % DETECT_EVERY_N_FRAMES == 0:
                current_person_count, last_boxes = detector.detect(frame)

                handle_email_alerts(
                    current_person_count,
                    previous_person_count
                )

                if current_person_count == 0:
                    if previous_person_count != 0:
                        print("[RESET] Biroul este liber.")

                    previous_person_count = 0
                    last_save_time = None

                else:
                    if should_save_image(
                        current_person_count,
                        previous_person_count,
                        last_save_time
                    ):
                        frame_to_save = frame.copy()
                        draw_boxes(frame_to_save, last_boxes)

                        save_event(frame_to_save, current_person_count)

                        cleanup_storage_if_needed()

                        last_save_time = time.time()

                    previous_person_count = current_person_count

            draw_boxes(frame, last_boxes)

            cv2.putText(
                frame,
                f"Persoane: {current_person_count}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    finally:
        camera.stop()
        cv2.destroyAllWindows()
        print("Sistem oprit.")


if __name__ == "__main__":
    main()
