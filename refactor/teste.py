import cv2 as cv
from Camera import Camera
from Image_processor import ImageProcessor
import numpy as np
import matplotlib.pyplot as plt


def show_wait_destroy(winname, img):
    cv.imshow(winname, img)
    cv.moveWindow(winname, 500, 0)
    cv.waitKey(0)
    cv.destroyWindow(winname)

def find_contour(index, camera_number):
    camera = Camera(camera_number)
    img = camera.take_picture(return_image=True)[125:250, 150:480]

    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    blurred = cv.GaussianBlur(img_gray, (5, 5), 0)

    ret, thresh = cv.threshold(blurred, 120, 255, cv.THRESH_BINARY)
        
    contours, hierarchy = cv.findContours(image=thresh, mode=cv.RETR_TREE, method=cv.CHAIN_APPROX_SIMPLE)

    # draw contours on the original image
    image_copy = img.copy()
    cv.drawContours(image=image_copy, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv.LINE_AA)

    area = 0

    for contour in contours: 
        area += cv.contourArea(contour)

    # see the results
    # cv.imshow('None approximation', image_copy)
    # cv.waitKey(0)
    cv.imwrite(f"images/contours_teste/camera_{camera_number}_{index}.jpg", image_copy)
    # cv.destroyAllWindows()

    return area

if __name__ == '__main__':
    find_contour(2, 2)
