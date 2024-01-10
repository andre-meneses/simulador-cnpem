#Programa de teste do laser
import time
from mcp2210 import Mcp2210, Mcp2210GpioDesignation, Mcp2210GpioDirection

# connect to the device by serial number
mcp = Mcp2210(serial_number="0000423978")

 

# this only needs to happen once
# if you don't call this, the device will use the existing settings

mcp.configure_spi_timing(chip_select_to_data_delay=0,
                         last_data_byte_to_cs=0,
                         delay_between_bytes=0)

 # set all pins as GPIO
for i in range(9):
    mcp.set_gpio_designation(i, Mcp2210GpioDesignation.GPIO)

 # set pin 0 to output
mcp.set_gpio_direction(0, Mcp2210GpioDirection.OUTPUT)

 # flash an LED
mcp.set_gpio_output_value(0, False)
for i in range(100):
    mcp.set_gpio_output_value(0, True)
    time.sleep(0.1)
    mcp.set_gpio_output_value(0, False)
    time.sleep(0.1)


