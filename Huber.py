#Programa de movimentação do goniometro huber
import serial

def Parse_state(message):
    message = message.decode('utf-8')
    message =  "".join(message.split()) 
    return int(message[0])

def Prepare():
    ser = serial.Serial('/dev/ttyUSB0', 115200)
    ser.write(b'SHH\r\n')
    ser.write(b'MTH = -2\r\n')
    ser.write(b'CN1\r\n')
    return ser


def Move(x,speed=80000, acc=20000, dacc=20000):
    angle = str(x*12800)
    angle = bytes('PRH=' + angle +'\r\n', 'utf-8')

    ser = Prepare()
    _speed = f"SPH={speed}\r\n"
    _acc = f"ACH={acc}\r\n"
    _dacc = f"DCH={dacc}\r\n"

    ser.write(angle)
    ser.write(bytes(_speed,'utf-8'))
    ser.write(bytes(_acc,'utf-8'))
    ser.write(bytes(_dacc,'utf-8'))
    
    ser.write(b'BGH\r\n')
    ser.write(b'MG _BGH\r\n')

    for i in range(9):
        ser.readline()
    
    state = Parse_state(ser.readline()) 

    while state == 1:
        ser.write(b'MG _BGH\r\n')
        ser.readline()
        state = Parse_state(ser.readline()) 
        print(state)

    ser.close()

if __name__ == '__main__':
    Move(30)

