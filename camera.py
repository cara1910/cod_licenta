from picamera2 import Picamera2
import time


class Camera:

    def __init__(self):

        self.camera = Picamera2()

        self.camera.configure(
            self.camera.create_video_configuration(
                main={ 
                    "format": "RGB888"
                }
            )
        )

        self.camera.start()

        time.sleep(2)

    def get_frame(self):

        return self.camera.capture_array()

    def stop(self):

        self.camera.stop()
