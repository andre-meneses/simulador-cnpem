# Programa de teste do cabeçote laser

# Import necessary modules
from mcp2210 import Mcp2210, Mcp2210GpioDesignation, Mcp2210GpioDirection
import time

# Configuration of MCP2210 GPIO pins

def Prepare():
    """
    Prepare and configure the MCP2210 USB-to-SPI bridge.
    :return: Mcp2210 object for communication.
    """
    mcp = Mcp2210(serial_number="0000423978")  # Initialize the MCP2210 device with its serial number
    
    # Configure SPI timing parameters
    mcp.configure_spi_timing(chip_select_to_data_delay=0, last_data_byte_to_cs=0, delay_between_bytes=0)
    
    # Set GPIO pin 0 as a general-purpose I/O (GPIO) pin
    mcp.set_gpio_designation(0, Mcp2210GpioDesignation.GPIO)
    
    # Set GPIO pin 0 as an output pin
    mcp.set_gpio_direction(0, Mcp2210GpioDirection.OUTPUT)
    
    # Turn off the laser if it is currently on
    mcp.set_gpio_output_value(0, False)
    
    return mcp

# These functions control the laser, turning it on and off
def laser_on(mcp):
    """
    Turn on the laser by setting the GPIO pin to high (True).
    :param mcp: Mcp2210 object for communication.
    """
    mcp.set_gpio_output_value(0, True)

def laser_off(mcp):
    """
    Turn off the laser by setting the GPIO pin to low (False).
    :param mcp: Mcp2210 object for communication.
    """
    mcp.set_gpio_output_value(0, False)

if __name__ == '__main__':
    mcp = Prepare()  # Initialize the MCP2210
    for i in range(1000):
        laser_on(mcp)   # Turn on the laser
        time.sleep(0.1) # Wait for 0.1 seconds
        laser_off(mcp)  # Turn off the laser
        time.sleep(0.1) # Wait for 0.1 seconds

