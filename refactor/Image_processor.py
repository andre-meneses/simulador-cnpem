import cv2 as cv
import outils
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

    def find_color(self, pixel, color=1):
        if self.image is None:
            print("Error: Image not provided or loaded properly.")
            return None

        pixel = (pixel[1], pixel[0])

        return self.image[*pixel, color]

    def compute_whole_brightness(self):
        gray_cropped = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        return gray_cropped.mean()

    def compute_brightness(self, contour, enlarge_percent=20):

        if self.image is None:
            print("Error: Image not provided or loaded properly.")
            return None

        total_brightness = 0

        x, y, w, h = cv.boundingRect(contour)

        # Enlarge the rectangle by the specified percentage
        enlarge_size = max(w, h) * enlarge_percent / 100
        x = int(x - enlarge_size / 2)
        y = int(y - enlarge_size / 2)
        w = int(w + enlarge_size)
        h = int(h + enlarge_size)

        # Ensure the rectangle is within image boundaries
        x, y = max(0, x), max(0, y)
        w, h = min(w, self.image.shape[1] - x), min(h, self.image.shape[0] - y)

        # Crop and calculate brightness
        cropped_image = self.image[y:y+h, x:x+w]
        gray_cropped = cv.cvtColor(cropped_image, cv.COLOR_BGR2GRAY)
        total_brightness = gray_cropped.mean()

        return total_brightness
    
    def centroids(self, save_path="marked_image.jpg"):
        if self.image is None:
            print("Error: Image not provided or loaded properly.")
            return None

        gray = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        blur = cv.GaussianBlur(gray, (5,5), cv.BORDER_DEFAULT)
        ret, thresh = cv.threshold(blur, 130, 255, cv.THRESH_BINARY)

        contours, hierarchies = cv.findContours(thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        blank = np.zeros(thresh.shape[:2], dtype='uint8')
        cv.drawContours(blank, contours, -1, (0, 0, 255), 1)

        centroids = []
        for contour in contours:
            M = cv.moments(contour)
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                centroids.append([cx, cy, contour])
                cv.drawContours(self.image, [contour], -1, (0, 255, 0), 2)
                cv.circle(self.image, (cx, cy), 4, (0, 0, 255), -1)
                # print(f"x: {cx} y: {cy}")

        # Save the modified image with centroids and contours marked
        cv.imwrite(save_path, self.image)

        return centroids

# Example Usage
if __name__ == "__main__":
    image = cv.imread("images/test/captured_image_2.jpg")

    if image is not None:
        image_processor = ImageProcessor(image)

        # avg_green_value = image_processor.avg_green()
        # if avg_green_value is not None:
            # print(f"Average green value: {avg_green_value}")

        centroids = image_processor.centroids("images/centroids/marked_centroids.jpg")
        if centroids:
            print("centroids:", outils.sort_centroids(centroids))
    else:
        print("Error: Image could not be loaded.")

