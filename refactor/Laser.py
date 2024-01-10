import time
from Mcp import Mcp

class LaserController:
    def __init__(self, mcp):
        self.mcp = mcp  # MCP2210 instance is passed during initialization

    def switch_laser(self, switch='on'):
        """
        Turn on or off the laser by setting the GPIO pin.
        :param switch: 'on' to turn on, 'off' to turn off.
        """
        if switch == 'on':
            self.mcp.set_gpio_output_value(0, True)
        else:
            self.mcp.set_gpio_output_value(0, False)

    def blink_laser(self, times):
        """
        Blink the laser on and off for a specified duration.
        :param times: Duration to keep the laser on.
        """
        self.switch_laser('on')
        time.sleep(times)
        self.switch_laser('off')


if __name__ == '__main__':
    mcp = Mcp()  # Create an instance of Mcp
    laser_controller = LaserController(mcp)  # Pass the Mcp instance to LaserController

    for i in range(1000):
        laser_controller.switch_laser('on')   # Turn on the laser
        time.sleep(0.1)                       # Wait for 0.1 seconds
        laser_controller.switch_laser('off')  # Turn off the laser
        time.sleep(0.1)                       # Wait for 0.1 seconds

