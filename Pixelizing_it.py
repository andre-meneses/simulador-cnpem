# Programa para teste apenas do prodedimento de pixelização
import cv2

 
# As rotinas click coletam a imagem das cameras USB
# O termo ret indica se a coleta foi bem sucedida
# O looping garante que o programa só acvance se houver imagem

def clickA():
    PNP = False
    while (PNP == False):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        PNP = ret
    cv2.imwrite('fotoA.jpg', frame)
    cap.release()

def cropA():
    image = cv2.imread("fotoA.jpg") 
    cropped_image = image[90:390,200:500] 
    cv2.imwrite('croppedA.jpg', cropped_image) 


def pixeling(pixel_size):
    img_input = cv2.imread('croppedA.jpg',cv2.IMREAD_GRAYSCALE)
    height, width = img_input.shape[:2]
    new_width, new_height = (width // pixel_size, height // pixel_size)
    img_temp = cv2.resize(img_input, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    img_output = cv2.resize(img_temp, (width, height), interpolation=cv2.INTER_NEAREST)
    (thresh, blackAndWhiteImage) = cv2.threshold(img_output, 60, 255, cv2.THRESH_BINARY)
    cv2.imwrite('pixelA.jpg', blackAndWhiteImage)


clickA()
cropA()
pixeling(5)