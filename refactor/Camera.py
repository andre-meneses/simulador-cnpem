import cv2

class Camera:
    """A class to interact with a camera device using OpenCV.

    Args:
        camera_number (int): The index of the camera device.

    Attributes:
        camera_number (int): The index of the camera device.

    Methods:
        take_picture: Captures a picture from the camera.
    """
    def __init__(self, camera_number):
        self.camera_number = camera_number

    def take_picture(self, output_name=None, return_image=False):
        """Captures a picture from the camera.

        Args:
            output_name (str, optional): The file path to save the captured image. Defaults to None.
            return_image (bool, optional): Whether to return the captured image as an array. Defaults to False.

        Returns:
            bool or numpy.ndarray or None: If return_image is False, returns True if the capture was successful, 
                                           False otherwise. If return_image is True, returns the captured image as
                                           a numpy array if successful, None otherwise.
        """
        cap = cv2.VideoCapture(self.camera_number)
        if not cap.isOpened():
            print(f"Error: Camera with index {self.camera_number} could not be opened.")
            return None if return_image else False

        try:
            ret, frame = cap.read()
            if not ret:
                print("Error: No frame captured from the camera.")
                return None if return_image else False

            if output_name:
                cv2.imwrite(output_name, frame)
                # print(f"Image saved as {output_name}")

            if return_image:
                return frame

            return True

        except Exception as e:
            print(f"An error occurred: {e}")
            return None if return_image else False

        finally:
            cap.release()

def find_available_cameras(limit=10):
    available_cameras = []
    for i in range(limit):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
    return available_cameras


if __name__ == '__main__':
    cameras = find_available_cameras()
    print("Available Cameras:", cameras)

    # Creating camera instances and taking pictures
    for camera_number in cameras:
        cam = Camera(camera_number)
        cam.take_picture(f'images/test/captured_image_{camera_number}.jpg')

