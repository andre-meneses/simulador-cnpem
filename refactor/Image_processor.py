import cv2
import numpy as np

class ImageProcessor:
    def __init__(self, image):
        # Assign the image directly
        self.image = image

    def avg_green(self):
        if self.image is None:
            print("Error: Image not provided or loaded properly.")
            return None

        # Calculate the average of the green channel
        average_green_value = np.mean(self.image[:, :, 1])

        return average_green_value

# Example Usage
if __name__ == "__main__":
    # Load an image
    image = cv2.imread("images/test/captured_image_2.jpg")

    if image is not None:
        image_processor = ImageProcessor(image)
        avg_green_value = image_processor.avg_green()
        if avg_green_value is not None:
            print(f"Average green value: {avg_green_value}")
    else:
        print("Error: Image could not be loaded.")

