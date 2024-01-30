import cv2 as cv
import outils
import numpy as np
from outils import show_wait_destroy

class ImageProcessor:
    """
    A class for processing images and extracting features.
    """

    def __init__(self, image=None):
        """
        Initialize the ImageProcessor with an image.

        Args:
            image (numpy.ndarray, optional): The input image. Defaults to None.
        """
        self.image = image

    def compute_brightness(self, contour, enlarge_percent=100):
        """
        Compute the brightness of a region specified by a contour.

        Args:
            contour (numpy.ndarray): Contour specifying the region of interest.
            enlarge_percent (int, optional): Percentage to enlarge the bounding rectangle. Defaults to 100.

        Returns:
            float: The total brightness of the region.
        """
        if self.image is None:
            print("Error: Image not provided or loaded properly.")
            return None

        total_brightness = 0

        image = self.image

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
        total_brightness = cropped_image[:,:,1].mean()

        cv.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return total_brightness
    
    def centroids(self, save_path="marked_image.jpg"):
        """
        Find centroids of objects in the image and mark them.

        Args:
            save_path (str, optional): Path to save the marked image. Defaults to "marked_image.jpg".

        Returns:
            list: List of centroids coordinates.
        """
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

        # Save the modified image with centroids and contours marked
        cv.imwrite(save_path, self.image)

        return centroids

    def find_contour(self, index, camera_number, crop_params=(125, 250, 150, 480)):
        """
        Find contours in an image captured by a camera.

        Args:
            index (int): Index of the image.
            camera_number (int): Number of the camera.
            crop_params (tuple, optional): Parameters for cropping the image. Defaults to (125, 250, 150, 480).

        Returns:
            float: Total area of the contours found.
        """
        camera = Camera(camera_number)
        img = camera.take_picture(return_image=True)[crop_params[0]:crop_params[1], crop_params[2]:crop_params[3]]

        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        blurred = cv.GaussianBlur(img_gray, (5, 5), 0)

        ret, thresh = cv.threshold(blurred, 120, 255, cv.THRESH_BINARY)

        contours, hierarchy = cv.findContours(image=thresh, mode=cv.RETR_TREE, method=cv.CHAIN_APPROX_SIMPLE)

        image_copy = img.copy()
        cv.drawContours(image=image_copy, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv.LINE_AA)

        area = 0

        for contour in contours:
            area += cv.contourArea(contour)

        cv.imwrite(f"images/contours_teste/camera_{camera_number}_{index}.jpg", image_copy)

        return area

    def find_tumour(self,image_path=None, crop_params=(65, 275, 130, 500), debug=False):
        """
        Find tumor in the image.

        Args:
            image_path (str, optional): Path to the image file. Defaults to None.
            crop_params (tuple, optional): Parameters for cropping the image. Defaults to (65, 275, 130, 500).
            debug (bool, optional): Whether to show debug image. Defaults to False.

        Returns:
            tuple: Cropped image with tumor and the contour of the tumor.
        """
        crop_top, crop_bottom, crop_left, crop_right = crop_params

        if image_path is None:
            camera = cv.VideoCapture(0)
            ret, image = camera.read()
            camera.release()
            if not ret:
                raise ValueError("Failed to capture image from camera")
        else:
            self.image = cv.imread(image_path)
            if self.image is None:
                raise FileNotFoundError(f"Image file not found at {image_path}")

        cropped_image = self.image[crop_top:crop_bottom, crop_left:crop_right]

        grayscale = cv.cvtColor(cropped_image, cv.COLOR_BGR2GRAY)

        blurred = cv.GaussianBlur(grayscale, (5, 5), 0)

        _, thresh = cv.threshold(blurred, 120, 255, cv.THRESH_BINARY)

        contours, _ = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        mask = np.zeros_like(thresh)
        cv.drawContours(mask, contours, -1, (255), thickness=cv.FILLED)
        mask = 255 - mask
        inverted_contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cv.drawContours(cropped_image, inverted_contours, -1, (255), thickness=cv.FILLED)

        max_area_contour = max(inverted_contours, key=cv.contourArea)

        if debug:
            show_wait_destroy("Debug Image", cropped_image)

        return cropped_image, max_area_contour

# Example Usage
if __name__ == "__main__":
    # image = cv.imread("images/test/captured_image_2.jpg")
    image = cv.imread("images/centroids/marked_centroids.jpg")
    ip = ImageProcessor(image)

    centroids = image_processor.centroids("images/centroids/marked_centroids.jpg")

    if centroids:
        print("centroids:", outils.sort_centroids(centroids))
    else:
        print("Error: Image could not be loaded.")

