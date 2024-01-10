#Programa de teste da fonte CAEN

import socket
import time
 
HOST = "192.168.1.10"  # The server's hostname or IP address
PORT = 10001  # The port used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("s:",s)
for i in range(10):      
        #print('Entre comando:')
        posit="MWV:5.0\r\n"
        negat="MWV:-5.0\r\n"
        arr1 = bytes(posit, 'utf-8')
        arr2 = bytes(negat, 'utf-8')
        s.sendall(arr1)
        print("Direção Positiva")
        time.sleep(0.2)
        s.sendall(arr2)
        print("Direção Negativa")
        time.sleep(0.2)
        print(i)

nulo="MWV:0.0\r\n"
arr3 = bytes(nulo, 'utf-8')
s.sendall(arr3)
    

nulo="MWV:0.0\r\n"
arr3 = bytes(nulo, 'utf-8')
s.sendall(arr3)