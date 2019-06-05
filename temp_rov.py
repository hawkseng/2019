#--------------ROV 2019 CONTROL PROGRAM - SENSOR TEST--------------#

#import modules - I assume import sleep is redundant
import time
from time import sleep
from pymata_aio.pymata3 import PyMata3
from pymata_aio.constants import Constants

#open socket for control board - this is from Matt
board = PyMata3(ip_address = '192.168.0.177', ip_port=3030, ip_handshake='')

#arrays and constants - removed the other units
UNITS_Centigrade = 1

# Registers - from datasheet and examples
TSYS01_ADDR        = 0x77
TSYS01_PROM_READ   = 0xA0
TSYS01_RESET       = 0x1E
TSYS01_CONVERT     = 0x48
TSYS01_READ        = 0x00

# Configure I2C Pin - From original program - I assume this sets I2C communication
board.i2c_config(0)

# Initialize Sensor - This is pymata specific.  Not sure about syntax.  I hope it sends 0x1E to the sensor to reset?
board.i2c_write_request(TSYS01_ADDR, TSYS01_RESET)
sleep(0.1)

# Read calibration values - Wild guesses here.  What Constants?
board.i2c_read_request(TSYS01_ADDR, TSYS01_PROM_READ, Constants.I2C_READ) 
temp_data = board.i2c_read_data(TSYS01_ADDR, TSYS01_PROM_READ)
return True

#main loop
while True:

       


           

time.sleep(0.1)

        
