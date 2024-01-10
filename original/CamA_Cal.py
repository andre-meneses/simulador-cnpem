#Programa para calibração do sistema
import cv2 as cv
import numpy as np
import serial
import socket
import time
from mcp2210 import Mcp2210, Mcp2210GpioDesignation, Mcp2210GpioDirection



# As rotinas click coletam a imagem das cameras USB
# O termo ret indica se a coleta foi bem sucedida
# O looping garante que o programa só acvance se houver imagem

def clickA():
    PNP = False
    while (PNP == False):
        cap = cv.VideoCapture(0)
        ret, frame = cap.read()
        PNP = ret
    cv.imwrite('painel.jpg', frame)
    cap.release()

def clickB():
    PNP = False
    while (PNP == False):
        cap = cv.VideoCapture(1)
        ret, frame = cap.read()
        PNP = ret
    cv.imwrite('painelB.jpg', frame)
    cap.release()
    
    
def take_photo_C():
    cap = cv.VideoCapture(1)
    ret, frame = cap.read()
    cv.imwrite('painelC.jpg', frame)
    cap.release()
    

# Define a porta e a velocidade de comunicação com o Galil
# O goniômetro foi instalado na saída 8 (H) da eletrônica de controle
# O comando SHH habilita o motor, o comando MTH diz o tipo de motor
# O comando CN1 diz a polaridade do Limit Switch
# O motor tem 200 passos/volta e o Galil está configurado com uma interpolação de 64
# Isso resulta em 12800 passos por grau
# Como não descobri como informar o termino do movimento, estou calculando o tempo

def Move(x):
    ser = serial.Serial('COM4', 115200)
    ser.write(b'SHH\r\n')
    ser.write(b'MTH = -2\r\n')
    ser.write(b'CN1\r\n')
        
    ang = str(x*12800)
    angu = bytes('PRH=' + ang +'\r\n', 'utf-8')
    ser.write(angu)
    ser.write(b'SPH=60000\r\n')
    ser.write(b'BGH\r\n')
    tempo = abs(x*12800/60000)*1.1
    time.sleep(tempo)
    
    ser.close()

# Configuração dos pinos da MCP2010 para comando do laser

mcp = Mcp2210(serial_number="0000423978")
mcp.configure_spi_timing(chip_select_to_data_delay=0, last_data_byte_to_cs=0,
                         delay_between_bytes=0)
mcp.set_gpio_designation(0, Mcp2210GpioDesignation.GPIO)

# set pin 0 to output
mcp.set_gpio_direction(0, Mcp2210GpioDirection.OUTPUT)

#desliga o laser caso ele esteja ligado
mcp.set_gpio_output_value(0, False)


# Essas rotinas ligam ou desligam o laser
def laser_on():
    mcp.set_gpio_output_value(0, True)
def laser_off():
    mcp.set_gpio_output_value(0, False)
    
          
    
        

px = [0,0,0,0,0,0,0,0,0]
py = [0,0,0,0,0,0,0,0,0]

pbx = [0,0,0,0,0,0,0,0,0]
pby = [0,0,0,0,0,0,0,0,0]

vlx = [0,0,0,0,0,0,0,0,0]
vly = [0,0,0,0,0,0,0,0,0]

#identificando os pontos
def centroidsA():
    image = cv.imread("painel.jpg")
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
 
    blur = cv.GaussianBlur(gray, (5,5), cv.BORDER_DEFAULT)
    ret, thresh = cv.threshold(blur, 120, 255, cv.THRESH_BINARY)
    cv.imwrite("painel_out.jpg",thresh)

    #achando os contornos
    contours, hierarchies = cv.findContours(thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    blank = np.zeros(thresh.shape[:2], dtype='uint8')
    cv.drawContours(blank, contours, -1, (0, 0, 255), 1)
    cv.imwrite("painel_contours.jpg", blank)

    #achando os centroides
        
    p = 0
    for i in contours:
        M = cv.moments(i)
        if M['m00'] != 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            px[p] = cx
            py[p] = cy
#            print('px:', px[p],'py', py[p])
            p = p + 1
            cv.drawContours(image, [i], -1, (0, 255, 0), 2)
            cv.circle(image, (cx, cy), 4, (0, 0, 255), -1)
            print(f"x: {cx} y: {cy}")    
    cv.imwrite("painel_centroids.jpg", image)
    
 
    
def centroidsB():
    image = cv.imread("painelB.jpg")
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
 
    blur = cv.GaussianBlur(gray, (5,5), cv.BORDER_DEFAULT)
    ret, thresh = cv.threshold(blur, 120, 255, cv.THRESH_BINARY)
    cv.imwrite("painelB_out.jpg",thresh)

    #achando os contornos
    contours, hierarchies = cv.findContours(thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    blank = np.zeros(thresh.shape[:2], dtype='uint8')
    cv.drawContours(blank, contours, -1, (0, 0, 255), 1)
    cv.imwrite("painelB_contours.jpg", blank)

    #achando os centroides
        
    p = 0
    for i in contours:
        M = cv.moments(i)
        if M['m00'] != 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            pbx[p] = cx
            pby[p] = cy
#            print('px:', px[p],'py', py[p])
            p = p + 1
            cv.drawContours(image, [i], -1, (0, 255, 0), 2)
            cv.circle(image, (cx, cy), 4, (0, 0, 255), -1)
            print(f"x: {cx} y: {cy}")    
    cv.imwrite("painelB_centroids.jpg", image)
    
    
#********************************************************
#print('Coletando posição dos pontos na câmera A')
#clickA()
#centroidsA()
#print('Posicionando para a câmera B')
#Move(90)
print('Coletando posição dos pontos na câmera B')
clickB()
centroidsB()

#for i in range (10):
#    clickB()
#    img = cv.imread('painelB.jpg')
#    print(img[pbx[1]][pby[1]])
#    cor = img[pbx[1]][pby[1]]
#    print(cor[1])
#print('Posicionando para a varredura laser')
#Move(-180)


posYini = -9.0
posXini = 10.0
delta = 0.08


HOSTY = "192.168.1.10"  # The server's hostname or IP address
PORT = 10001  # The port used by the server
sy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sy.connect((HOSTY, PORT))


HOSTX = "192.168.0.11"  # The server's hostname or IP address
PORT = 10001  # The port used by the server
sx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sx.connect((HOSTX, PORT))


verde_max = 0
laser_on()

posY = posYini
for i in range (125):
    posYst = "MWV:"+str(posY)+"\r\n"
    arrY = bytes(posYst, 'utf-8')
    sy.sendall(arrY)
    posX = posXini
    for j in range (175):
        posXst = "MWV:"+str(posX)+"\r\n"
        arrX = bytes(posXst, 'utf-8')  
        sx.sendall(arrX)
        #*******************************************
        clickB()
        img = cv.imread('painelB.jpg')
        cor = img[pbx[0]][pby[0]]
        verde = cor[1]
        if verde > verde_max:
            verde_max = verde
            vlx[0] = posX
            vly[0] = posY
            
        #*******************************************
        posX = posX - delta
        time.sleep(0.02)
    posY = posY + delta
    
print('vlx,vly:',vlx[0],vly[0])        
laser_off()

    
    

    

   