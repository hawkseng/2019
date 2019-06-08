#--------------ROV 2019 CONTROL PROGRAM - SENSOR TEST--------------#

#import modules - I assume import sleep is redundant
import time
from time import sleep # YES IT IS REDUNDANT
from pymata_aio.pymata3 import PyMata3
from pymata_aio.constants import Constants

def calculate_temperature(k, adc): #Setting up a function to return the calculated temperature based on the ADC value and the constants
    adc16 = adc/256
    #This equation is copied straight from the datasheet page 8
    temperature = (-2)   * k[4] * 10**(-21) * adc16**4 + \ 
                  (4)    * k[3] * 10**(-16) * adc16**3 + \
                  (-2)   * k[2] * 10**(-11) * adc16**2 + \
                  (1)    * k[1] * 10**(-6)  * adc16 \
                  (-1.5) * k[0] * 10**(-2)
    return temperature

#open socket for control board - this is from Matt
board = PyMata3(ip_address = '192.168.0.177', ip_port=3030, ip_handshake='')

#arrays and constants - removed the other units
UNITS_Centigrade = 1 #Not sure what you're doing here...It seems like you just made a new variable and set it equal to 1
#UNITS_Centigrade is not part of any of the imported files in this program; it is part of the tsys01-python example code though, but you're not using it

# Registers - from datasheet and examples
TSYS01_ADDR        = 0x77 #You should confirm this on the hardware side. If the CSB pin is pulled high, it will be 0x76
TSYS01_PROM_READ   = 0xA0
TSYS01_RESET       = 0x1E
TSYS01_CONVERT     = 0x48
TSYS01_READ        = 0x00

k = [] # setting up the constants array that will be used for calculating the temperature later (PROM Constants)
TSYS01_PROM_REGS = [0xA0, 0xA2, 0xA4, 0xA6, 0xA8, 0xAA, 0xAC, 0xAE] #These are all the PROM Registers you'll have to read
# I am just putting them in an array rather than doing something fancy because it's easier to just do a regular C type for loop with this

# Configure I2C Pin - From original program - I assume this sets I2C communication
board.i2c_config(0) #The argument passed in is the read delay time...0 is fine I believe

print('Initializing')

# Initialize Sensor - This is pymata specific.  Not sure about syntax.  I hope it sends 0x1E to the sensor to reset?
board.i2c_write_request(TSYS01_ADDR, TSYS01_RESET) #This should work according to the documentation

#One thing that I don't understand is when Matt calls upon i2c_write_request, he first sends a string of 8 zeros,
# which I am not sure if he is just flushing the communication lines or if that's actually something else.
#He mentions that the esc's accept a 16bit value, and the i2c_write_request command sends bytes at a time passed in as an array

sleep(0.1) #allow the chip to reset

# Read calibration values - Wild guesses here.  What Constants?
#board.i2c_read_request(TSYS01_ADDR, TSYS01_PROM_READ, Constants.I2C_READ) 
#temp_data = board.i2c_read_data(TSYS01_ADDR, TSYS01_PROM_READ)

for i in range(6): #This should read PROM Registers 0xA0 to 0xAA, the last two are used for checksum and something else which I doubt you care about
    board.i2c_read_request(TSY01_ADDR, TSYS01_PROM_REGS[i], 2, Constants.I2C_READ) #Address of the sensor, address of the PROM Register, number of bytes, read_type (not sure about that one)
    k[i] = board.i2c_read_data(TSYS01_ADDR) #This one only takes one argument...if this doesn't work, try TSYS01_PROM_REGS[i] as the argument
    k[i] = (k[i]<<8 | k[i]>>8) #I saw both the pi program and the C++ program swap the MSB and LSB because of the endianness of the protocol...if you get absolutely crazy temperature values, I would suggest you comment this statement out to see if that fixes it first
#I believe this should set up the constants array
print('These are the PROM Constants')
print(k) #just checking if 6 values are printed
    
#return True #Don't Need this

print('Entering the Main Loop')
#main loop
while True: #In your main code, you want to put the following inside the main loop that also polls the joystick. This may hurt the speed at which your code runs. If that is the case, put the following inside the main loop but also inside a conditional if statement so that when a button is pressed, thats the only time it actually calculates the temperature, otherwise, it skips the whole temperature calculation or even reading so your ROV movements and joystick polling isn't affected as mych
    board.i2c_write_request(TSYS01_ADDR, TSYS01_CONVERT) #Start ADC conversion...look at the flow chart on page 8 of the data sheet
    board.sleep(0.01) #sleep for 10ms, as the max conversion time is 9.04ms as shown on page 2 of the data sheet
    board.i2c_write_request(TSYS01_ADDR, TSYS01_READ) #send the read ADC command...again, check out the data sheet end of page 7 timing diagram or page 8
    adc = board.i2c_read_request(TSY01_ADDR, 0, 3, Constants.I2C_READ) #read 3 bytes from the temp sensor with no registers specified
    adc = (adc[0]<<16 | adc[1]<<8 | adc[2]) #this is again flipping the endianness of the bits I think or something...not sure, another thing that could be incorrectly implemented, ask me about this if it doesnt work but I see other people doing this too
    temperature = calculate_temperature(k, adc)
    print('Temperature: ',temperature, '\u00b0C') #should print your temperature in degrees celcius

