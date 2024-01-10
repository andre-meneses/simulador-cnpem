from mcp2210 import Mcp2210, Mcp2210GpioDesignation, Mcp2210GpioDirection

def Mcp():
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


