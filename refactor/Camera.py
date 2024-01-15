import cv2

class Camera:
    def __init__(self, camera_number):
        self.camera_number = camera_number

    def take_picture(self, output_name):
        cap = cv2.VideoCapture(self.camera_number)
        if not cap.isOpened():
            print(f"Error: Camera with index {self.camera_number} could not be opened.")
            return False

        try:
            ret, frame = cap.read()
            if not ret:
                print("Error: No frame captured from the camera.")
                return False

            cv2.imwrite(output_name, frame)
            print(f"Image saved as {output_name}")
            return True

        except Exception as e:
            print(f"An error occurred: {e}")
            return False

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

