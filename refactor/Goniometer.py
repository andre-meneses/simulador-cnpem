import serial

class GoniometerController:
    def __init__(self, port='/dev/ttyUSB0', baud_rate=115200):
        self.port = port
        self.baud_rate = baud_rate
        self.steps_per_degree = 12800  # Assuming 12800 steps per degree

    def __enter__(self):
        self.ser = serial.Serial(self.port, self.baud_rate)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.ser.close()

    def _parse_state(self, message):
        message = message.decode('utf-8').strip()
        return int(message[0])

    def _prepare(self):
        self.ser.write(b'SHH\r\n')       
        self.ser.write(b'MTH = -2\r\n')  
        self.ser.write(b'CN1\r\n')       

    def move(self, angle, speed=40000, acc=20000, dec=20000, verbose=False):
        self._prepare()
        angle_steps = str(int(angle * self.steps_per_degree))
        commands = [
            f'PRH={angle_steps}\r\n',
            f'SPH={speed}\r\n',
            f'ACH={acc}\r\n',
            f'DCH={dec}\r\n',
            f'BGH\r\n',
            f'MG _BGH\r\n'
        ]

        for cmd in commands:
            self.ser.write(bytes(cmd, 'utf-8'))

        for _ in range(9):
            self.ser.readline()

        state = self._parse_state(self.ser.readline())
        while state == 1:
            self.ser.write(b'MG _BGH\r\n')
            self.ser.readline()
            state = self._parse_state(self.ser.readline())
            if verbose:
                print(state)

if __name__ == '__main__':
    with GoniometerController() as controller:
        controller.move(-30)  # Move the goniometer by 30 degrees
