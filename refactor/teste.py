import cv2 
from Camera import Camera
from Image_processor import ImageProcessor
import numpy as np
import matplotlib.pyplot as plt
import cv2

def find_contour(index):
    camera = Camera(0)
    img = camera.take_picture(return_image=True)[36:471, 110:530]

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(img_gray, (5, 5), 0)

    ret, thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)

    # draw contours on the original image
    image_copy = img.copy()
    cv2.drawContours(image=image_copy, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)

    area = 0

    for contour in contours: 
        area += cv2.contourArea(contour)

    # see the results
    # cv2.imshow('None approximation', image_copy)
    # cv2.waitKey(0)
    cv2.imwrite(f"images/contours_teste/{index}.jpg", image_copy)
    # cv2.destroyAllWindows()

    return area

if __name__ == '__main__':
    find_contour(2)
