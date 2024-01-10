# Programa de simulação de tomografia e escaneamento de feixe
import cv2
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
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        PNP = ret
    cv2.imwrite('fotoA.jpg', frame)
    cap.release()

def clickB():
    PNP = False
    while (PNP == False):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        PNP = ret
    cv2.imwrite('fotoB.jpg', frame)
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
    (thresh, blackAndWhiteImage) = cv2.threshold(img_output, 40, 255, cv2.THRESH_BINARY)
    cv2.imwrite('pixelA.jpg', blackAndWhiteImage)

 
# Define a porta e a velocidade de comunicação com o Galil
# O goniômetro foi instalado na saída 8 (H) da eletrônica de controle
# O comando SHH habilita o motor, o comando MTH diz o tipo de motor
# O comando CN1 diz a polaridade do Limit Switch

ser = serial.Serial('COM4', 115200)
ser.write(b'SHH\r\n')
ser.write(b'MTH = -2\r\n')
ser.write(b'CN1\r\n')


# O motor tem 200 passos/volta e o Galil está configurado com uma interpolação de 64
# Isso resulta em 12800 passos por grau
# Como não descobri como informar o termino do movimento, estou calculando o tempo

def Move(x):
    ang = str(x*12800)
    angu = bytes('PRH=' + ang +'\r\n', 'utf-8')
    ser.write(angu)
    ser.write(b'SPH=60000\r\n')
    ser.write(b'BGH\r\n')
    tempo = abs(x*12800/60000)*1.1
    time.sleep(tempo)

# Configuração dos pinos da MCP2010

mcp = Mcp2210(serial_number="0000423978")
mcp.configure_spi_timing(chip_select_to_data_delay=0, last_data_byte_to_cs=0,
                         delay_between_bytes=0)
mcp.set_gpio_designation(0, Mcp2210GpioDesignation.GPIO)

# set pin 0 to output
mcp.set_gpio_direction(0, Mcp2210GpioDirection.OUTPUT)

#desliga o laser caso ele esteja ligado
mcp.set_gpio_output_value(0, False)


# Essa rotina liga o laser

def laser_on():
    mcp.set_gpio_output_value(0, True)

def laser_off():
    mcp.set_gpio_output_value(0, False)

   
HOST = "192.168.0.11"  # The server's hostname or IP address
PORT = 10001  # The port used by the server

 
def burnT(): 
    laser_on()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        for i in range(30):      
            posit="MWV:1.5\r\n"
            negat="MWV:-1.5\r\n"
            arr1 = bytes(posit, 'utf-8')
            arr2 = bytes(negat, 'utf-8')
            s.sendall(arr1)
            time.sleep(0.05)
            s.sendall(arr2)
            time.sleep(0.05)
    laser_off()

def burn2():
    
    disthor = 100
    offsetX = 1
    offsetY = -3
    increm = 4
    npontos = int(disthor/increm)

    calx = 20/(113.41+114.21)
    caly = 20/(153.02+154.22)

    vinix = -(disthor/2)*calx
    viniy = -(disthor/2)*caly
    
    print("vinix:", vinix)
    print("viniy:", viniy)

    HOSTY = "192.168.1.10"  # The server's hostname or IP address
    PORT = 10001  # The port used by the server
    sy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sy.connect((HOSTY, PORT))


    HOSTX = "192.168.0.11"  # The server's hostname or IP address
    PORT = 10001  # The port used by the server
    sx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sx.connect((HOSTX, PORT))
    
    

    posY = viniy + offsetY
    for i in range(npontos):      
        posYst = "MWV:"+str(posY)+"\r\n"
        arrY = bytes(posYst, 'utf-8')  
        sy.sendall(arrY)
        laser_on()
        posX = vinix + offsetX       
        posXst = "MWV:"+str(posX)+"\r\n"
        arrX = bytes(posXst, 'utf-8')
        sx.sendall(arrX)
        posX = -vinix + offsetX      
        posXst = "MWV:"+str(posX)+"\r\n"
        arrX = bytes(posXst, 'utf-8')
        sx.sendall(arrX)
        laser_off()
        posY = posY + increm * caly
    laser_off()


def burn3():
    disthor = 100
    offsetX = 1
    offsetY = -3
    increm = 4
    npontos = int(disthor/increm)

    calx = 20/(113.41+114.21)
    caly = 20/(153.02+154.22)

    vinix = -(disthor/2)*calx
    viniy = -(disthor/2)*caly
    

    HOSTY = "192.168.1.10"  # The server's hostname or IP address
    PORT = 10001  # The port used by the server
    sy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sy.connect((HOSTY, PORT))


    HOSTX = "192.168.0.11"  # The server's hostname or IP address
    PORT = 10001  # The port used by the server
    sx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sx.connect((HOSTX, PORT))
    
    

    posY = viniy + offsetY
    laser_on()
    for i in range(npontos):
        posYst = "MWV:"+str(posY)+"\r\n"
        arrY = bytes(posYst, 'utf-8')  
        sy.sendall(arrY)     
        posX = vinix + offsetX       
        posXst = "MWV:"+str(posX)+"\r\n"
        arrX = bytes(posXst, 'utf-8')
        sx.sendall(arrX)
        time.sleep(0.001)
        posX = -vinix + offsetX      
        posXst = "MWV:"+str(posX)+"\r\n"
        arrX = bytes(posXst, 'utf-8')
        sx.sendall(arrX)
        time.sleep(0.001)
        posY = posY + increm * caly
    laser_off()
   



  
# Inicio da tomografia com coleta de 4 fotos

a = 1
print('Iniciando Tomografia')
slide =str(a)
print('Taking photo:',a)
clickA()
img_input = cv2.imread('fotoA.jpg')
cv2.imwrite('slide' + slide + '.jpg', img_input)
pixeling(5)
img_input = cv2.imread('pixelA.jpg')
cv2.imwrite('pixel' + slide + '.jpg', img_input)

a = 2
while a < 5:
    print('Moving to position',a)
    Move (90)
    slide =str(a)
    print('Taking photo:',a)
    clickA()
    img_input = cv2.imread('fotoA.jpg')
    cv2.imwrite('slide' + slide + '.jpg', img_input)
    pixeling(5)
    img_input = cv2.imread('pixelA.jpg')
    cv2.imwrite('pixel' + slide + '.jpg', img_input)
    a+=1
else:
    print ('Tomografia encerrada')

 
# Esse angulo foi aleatorio, considerando 90 graus entre a camera A e o Laser
#Move(-54)
 

#Inicio da queima do tumor com o laser
a = 1
print('Iniciando Dose')
slide =str(a)
print('Position:',a)
print('Burning:',a)
for i in range (10):
    burn3()
    time.sleep(0.05)

#clickB()
#img_input = cv2.imread('fotoB.jpg')
#cv2.imwrite('Contor' + slide + '.jpg', img_input)

a = 2
while a < 5:
    print('Moving to position',a)
    Move (90)
    slide =str(a)
    print('Position:',a)
    print('Burning:',a)
    for i in range (10):
        burn3()
        time.sleep(0.05)
#    clickB()
#    img_input = cv2.imread('fotoB.jpg')
#    cv2.imwrite('Contor' + slide + '.jpg', img_input)
    a+=1
else:
    print ('Tratamento encerrado')   
ser.close()


