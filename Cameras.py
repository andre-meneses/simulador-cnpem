#Programa de teste das cameras
import cv2

 
def take_photo():
    cap = cv2.VideoCapture(1)
    ret, frame = cap.read()
    cv2.imwrite('lixo.jpg', frame)
    cap.release()
    
    
take_photo()