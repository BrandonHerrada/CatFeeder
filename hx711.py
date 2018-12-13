import RPi.GPIO as GPIO
import time
import numpy  # sudo apt-get python-numpy
import sys

class HX711:
    #==========================================
    # Constructor:
    # dout: digital input pin
    # pd_sck: digital output pin
    #==========================================
    def __init__(self, dout, pd_sck, gain=128):
        self.PD_SCK = pd_sck
        self.DOUT = dout

        # Tell the OS what pins will be used and how
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.PD_SCK, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)

        # Set constants and variables as defined by manufacturer
        self.GAIN = 0
        self.REFERENCE_UNIT = 1  # The value returned by the hx711 that corresponds to your reference unit AFTER dividing by the SCALE.
        
        self.OFFSET = 1
        self.lastVal = long(0)

        self.LSByte = [2, -1, -1]
        self.MSByte = [0, 3, 1]
        
        self.MSBit = [0, 8, 1]
        self.LSBit = [7, -1, -1]

        self.byte_format = 'LSB'
        self.bit_format = 'MSB'

        self.byte_range_values = self.LSByte
        self.bit_range_values = self.MSBit

        self.set_gain(gain)

        time.sleep(1)
        
    #==========================================
    # Method is_ready:
    #   Checks if the specified input pin DOUT is low
    #==========================================
    def is_ready(self):
        return GPIO.input(self.DOUT) == 0

    # Method set_gain:
    #   setter for self.GAIN
    def set_gain(self, gain):
        if gain is 128:
            self.GAIN = 1
        elif gain is 64:
            self.GAIN = 3
        elif gain is 32:
            self.GAIN = 2

        GPIO.output(self.PD_SCK, False)
        self.read()
    
    #==========================================
    # Method createBoolList
    #   creates a list of boolean values
    # params:
    #   size: 
    #       The size of the list to create
    #==========================================
    def createBoolList(self, size=8):
        ret = []
        for i in range(size):
            ret.append(False)
        return ret
        
    #==========================================
    # Method read:
    #   Reads a value from the scale
    #==========================================
    def read(self):
        while not self.is_ready():
            #print("WAITING")
            pass

        dataBits = [self.createBoolList(), self.createBoolList(), self.createBoolList()]
        dataBytes = [0x0] * 4

        for j in range(self.byte_range_values[0], self.byte_range_values[1], self.byte_range_values[2]):
            for i in range(self.bit_range_values[0], self.bit_range_values[1], self.bit_range_values[2]):
                GPIO.output(self.PD_SCK, True)
                dataBits[j][i] = GPIO.input(self.DOUT)
                GPIO.output(self.PD_SCK, False)
            dataBytes[j] = numpy.packbits(numpy.uint8(dataBits[j]))

        #set channel and gain factor for next reading
        for i in range(self.GAIN):
            GPIO.output(self.PD_SCK, True)
            GPIO.output(self.PD_SCK, False)

        #check for all 1
        #if all(item is True for item in dataBits[0]):
        #    return long(self.lastVal)

        dataBytes[2] ^= 0x80
        return dataBytes
    

    #==========================================
    # Method get_np_arr8_string:
    #   returns a string formatted as a numpy 
    #   8-bit number string
    #==========================================
    def get_np_arr8_string(self):
        np_arr8 = self.read_np_arr8()
        np_arr8_string = "[";
        comma = ", "
        for i in range(4):
            if i is 3:
                comma = ""
            np_arr8_string += str(np_arr8[i]) + comma
        np_arr8_string += "]";
        
        return np_arr8_string

    #==========================================
    # Method read_np_arr8:
    #   Reads value to a numpy 
    #   8-bit number string
    #==========================================
    def read_np_arr8(self):
        dataBytes = self.read()
        np_arr8 = numpy.uint8(dataBytes)

        return np_arr8

    #==========================================
    # Method read_np_arr8:
    #   Reads a value to a long integer
    #==========================================
    def read_long(self):
        np_arr8 = self.read_np_arr8()
        np_arr32 = np_arr8.view('uint32')
        self.lastVal = np_arr32

        return long(self.lastVal)

    #==========================================
    # Method read_average:
    #     Reads <times> values and returns the average
    # params:
    #   times: 
    #      how many values to read
    #  
    #==========================================
    def read_average(self, times=3):
        values = long(0)
        for i in range(times):
            values += self.read_long()

        return values / times
        
    #==========================================
    # Method get_value:
    #     Reads <times> values and returns the 
    #     average, corrected by the tare OFFSET
    # params:
    #   times: 
    #      how many values to read
    #  
    #==========================================
    def get_value(self, times=3):
        return self.read_average(times) - self.OFFSET

    #==========================================
    # Method get_weight:
    #     Reads <times> values and returns the 
    #     average, corrected by the tare OFFSET 
    #     and divided by the reference value
    # params:
    #   times: 
    #      how many values to read
    #  
    #==========================================
    def get_weight(self, times=3):
        value = self.get_value(times)
        value = value / self.REFERENCE_UNIT
        return value

    #==========================================
    # Method tare:
    #     Reads <times> values and sets it as 
    #     the offset
    # params:
    #   times: 
    #      how many values to read
    #  
    #==========================================
    def tare(self, times=15):
       
        # Backup REFERENCE_UNIT value
        reference_unit = self.REFERENCE_UNIT
        self.set_reference_unit(1)

        value = self.read_average(times)
        self.set_offset(value)

        self.set_reference_unit(reference_unit)
        return value;

    #==========================================
    # Method set_reading_format:
    #     Specified by the manufacturer.
    #     Do not edit
    #  
    #==========================================
    def set_reading_format(self, byte_format="LSB", bit_format="MSB"):

        self.byte_format = byte_format
        self.bit_format = bit_format

        if byte_format == "LSB":
            self.byte_range_values = self.LSByte
        elif byte_format == "MSB":
            self.byte_range_values = self.MSByte

        if bit_format == "LSB":
            self.bit_range_values = self.LSBit
        elif bit_format == "MSB":
            self.bit_range_values = self.MSBit

    # OFFSET setter
    def set_offset(self, offset):
        self.OFFSET = offset

    # REFERENCE_UNIT setter
    def set_reference_unit(self, reference_unit):
        self.REFERENCE_UNIT = reference_unit

    # HX711 datasheet states that setting the PDA_CLOCK pin on high for >60 microseconds would power off the chip.
    # I used 100 microseconds, just in case.
    # I've found it is good practice to reset the hx711 if it wasn't used for more than a few seconds.
    def power_down(self):
        GPIO.output(self.PD_SCK, False)
        GPIO.output(self.PD_SCK, True)
        time.sleep(0.0001)

    def power_up(self):
        GPIO.output(self.PD_SCK, False)
        time.sleep(0.0001)

    def reset(self):
        self.power_down()
        self.power_up()

    def listen(self):
        # Reset the input pins
        self.reset()
        # Read a value
        w = self.get_weight(5)

    def cleanAndExit(self):
        print("Cleaning...")
        GPIO.cleanup()
        print("Bye!")
        sys.exit()