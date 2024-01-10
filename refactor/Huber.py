# Programa de movimentação do goniometro huber

# Import the 'serial' module for serial communication with the device
import serial

# Function to parse the device state message and extract the first character as an integer
def Parse_state(message):
    message = message.decode('utf-8')        # Decode the message from bytes to a string
    message = "".join(message.split())       # Remove spaces and other whitespace characters
    return int(message[0])                   # Extract the first character and convert it to an integer

# Function to prepare the serial communication with the goniometer device
def Prepare():
    ser = serial.Serial('/dev/ttyUSB0', 115200)  # Initialize a serial connection to '/dev/ttyUSB0' with a baud rate of 115200
    ser.write(b'SHH\r\n')                        # Send command to the device to stop its current motion
    ser.write(b'MTH = -2\r\n')                   # Set the motor to mode -2
    ser.write(b'CN1\r\n')                        # Connect to controller 1 (assuming this is the controller ID)
    return ser

# Function to move the goniometer to a specified angle in degrees with optional speed, acceleration, and deceleration parameters
def Move(x, speed=80000, acc=20000, dacc=20000):
    """
    Move the goniometer by x degrees with a specified speed, acceleration, and deceleration.
    :param x: The angle to move in degrees.
    :param speed: The speed of the motion in steps per second (default is 80000 steps/s).
    :param acc: The acceleration in steps per second squared (default is 20000 steps/s^2).
    :param dacc: The deceleration in steps per second squared (default is 20000 steps/s^2).
    """

    # Calculate the angle in steps based on the device's configuration
    angle = str(x * 12800)
    angle = bytes('PRH=' + angle + '\r\n', 'utf-8')

    # Prepare the serial connection
    ser = Prepare()
    _speed = f"SPH={speed}\r\n"
    _acc = f"ACH={acc}\r\n"
    _dacc = f"DCH={dacc}\r\n"

    # Send commands to the device
    ser.write(angle)
    ser.write(bytes(_speed, 'utf-8'))
    ser.write(bytes(_acc, 'utf-8'))
    ser.write(bytes(_dacc, 'utf-8'))

    ser.write(b'BGH\r\n')        # Begin motion
    ser.write(b'MG _BGH\r\n')    # Monitor the motion

    for i in range(9):
        ser.readline()            # Read and discard 9 lines of response

    state = Parse_state(ser.readline())  # Get the initial state of the device

    # Wait for the motion to complete (state to change from 1 to another value)
    while state == 1:
        ser.write(b'MG _BGH\r\n')         # Monitor the motion
        ser.readline()                    # Read and discard the response
        state = Parse_state(ser.readline())  # Get the updated state
        print(state)                       # Print the current state

    ser.close()  # Close the serial connection

# Main program
if __name__ == '__main__':
    Move(30)  # Move the goniometer by 30 degrees

