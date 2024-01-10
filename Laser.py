#Programa de teste do cabeÃ§ote laser

from mcp2210 import Mcp2210, Mcp2210GpioDesignation, Mcp2210GpioDirection
import time

# ConfiguraÃ§Ã£o dos pinos da MCP2010

def Prepare():
    mcp = Mcp2210(serial_number="0000423978")
    mcp.configure_spi_timing(chip_select_to_data_delay=0, last_data_byte_to_cs=0,
                             delay_between_bytes=0)
    mcp.set_gpio_designation(0, Mcp2210GpioDesignation.GPIO)

    # set pin 0 to output
    mcp.set_gpio_direction(0, Mcp2210GpioDirection.OUTPUT)

    #desliga o laser caso ele esteja ligado
    mcp.set_gpio_output_value(0, False)

    return mcp


# Essas rotinas ligam e desligam o laser
def laser_on(mcp):
    mcp.set_gpio_output_value(0, True)

def laser_off(mcp):
    mcp.set_gpio_output_value(0, False)

if __name__ == '__main__':
    mcp = Prepare()
    for i in range(1000):
        laser_on(mcp)
        time.sleep(0.1)
        laser_off(mcp)
        time.sleep(0.1)
