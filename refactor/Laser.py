import time
from Mcp import Mcp

# These functions control the laser, turning it on and off
def switch_laser(mcp, switch='on'):
    """
    Turn on the laser by setting the GPIO pin to high (True).
    :param mcp: Mcp2210 object for communication.
    """
    if switch=='on':
        mcp.set_gpio_output_value(0, True)
    else:
        mcp.set_gpio_output_value(0, False)

if __name__ == '__main__':
    mcp = Mcp()  # Initialize the MCP2210
    for i in range(1000):
        switch_laser(mcp, switch='on')   # Turn on the laser
        time.sleep(0.1) # Wait for 0.1 seconds
        switch_laser(mcp, switch='off')   # Turn on the laser
        time.sleep(0.1) # Wait for 0.1 seconds

