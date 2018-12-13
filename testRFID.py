#!/bin/python
import time
import serial
# RDM6300 module
#  Serial output:
#  _______________________________________________
#  |0x02| DATA(10 ascii chars) | CHECKSUM | 0x03 |
#  ===============================================
# params: 96008n1

class RDM6300:
    # Interface constants
    SERIAL_PORT = ''
    BAUDRATE = 9600
    # Start byte and end byte constants
    RDM_START = 2
    RDM_END = 3
    # DATA string size
    RDM_DATA_SZ = 10

    # Constructor: 
    #~~~~~~~~~~~~~
    #    Sets the serial port name
    def __init__(self, serial_port):
        self.SERIAL_PORT = serial_port
        print ("Initialized Serial Port")

    # Static method __verify_checksum: 
    #======================================================
    #    Checks if the data string received is a valid ID
    #    by XOR each pair of dat and compairing the result
    #    against the read checksum. 
    #
    # Params:
    #    data:
    #        A list of size 10 containing each byte of
    #        the ID as a 2-digit hexadecimal text string 
    #        e.g ["DE","CA","FF","C0","FF","EE",...]
    #    checksum: 
    #        The checksum as read from the tag as a 
    #        2-digit hexadecimal text string e.g. "D3"
    # Returns:
    #    True if checksum is ok
    #    False if checksum is not ok
    #======================================================
    @staticmethod
    def __verify_checksum(data, checksum):
        try:
            # Calculate checksum
            result = int(data[0:2], 16) \
                     ^ int(data[2:4], 16) \
                     ^ int(data[4:6], 16) \
                     ^ int(data[6:8], 16) \
                     ^ int(data[8:10], 16)
            result = format(result, 'x')

        except ValueError:
            return False

        # Compare calculated to read value
        if result.lower() != checksum.lower():
            return False
        return True

    # Static method __fix_zeros: 
    #======================================================
    #    Replaces spaces with zeros 
    #
    # Params:
    #    data: 
    #        A list of size 10 containing each byte of
    #        the ID as a 2-digit hexadecimal text string 
    #        e.g ["DE","CA","FF","C0","FF","EE",...]
    # Returns:
    #    The data string with zeros instead of spaces
    #======================================================
    @staticmethod
    def __fix_zeros(data):
        return data.replace(' ', '0')

    # Method __read_sequence: 
    #======================================================
    #    Reads a sequence of bytes from the serial 
    #    connection
    #
    # Params:
    #    serial_connection: 
    #        A serial.Serial object which has been 
    #        initialised to use the serial port that the 
    #        scanner module is connected to.
    # Returns:
    #    A string containing the ID read, or False if the 
    #    bytes read are bad
    #======================================================
    def __read_sequence(self, serial_connection):
        serial_connection.timeout=3
        tag_string = ''
        byte_read = serial_connection.read()

        # Check timeout
        if byte_read==None or byte_read=="":
            return False

        # Check first byte
        if int(ord(byte_read)) != self.RDM_START:
            return False

        # Read 12 bytes after the RDM_START byte has been read
        expected_len = 12
        while expected_len is not 0:

            expected_len -= 1
            byte_read = serial_connection.read()
            
            # reset the loop counter if the byte is RDM_START
            if int(ord(byte_read)) == self.RDM_START:
                expected_len = 12
                continue

            # Add the currently read byte to the tag_string
            if ord(byte_read) != self.RDM_END:
                tag_string += chr(ord(byte_read))
                continue
            break

        # Split tag_string into data and checksum
        data = tag_string[0:len(tag_string) - 2]
        checksum = tag_string[len(tag_string) - 2:len(tag_string)]
        # Check checksum
        checksum_ok = self.__verify_checksum(data, checksum)

        if not checksum_ok:
            return False
            
        return self.__fix_zeros(data)

    # Method __read_sequence: 
    #======================================================
    #    Prints the tags as they are read
    #
    #======================================================
    def do_work(self):
        serial_connection = ''
        try:
            print ("Creating serial connection")
            serial_connection = serial.Serial(self.SERIAL_PORT, baudrate=self.BAUDRATE)
            print ("Serial connection created")
            while True:
                data = self.__read_sequence(serial_connection)
                # check if its an actual RFID string
                if data is False:
                    print ("No cat detected")
                    data="000000000000"
                else:
                    print (data)
                # wait for 2 seconds
                time.sleep(2)
                # reset all input buffer data
                serial_connection.flushInput()

        except KeyboardInterrupt:
            print ("\nKilled. Serial port was safely closed.")
            serial_connection.close()
# Main method:
#===============================================
#     initialises RDM6300 object
#     runs RDM6300.do_work()
#===============================================
if __name__ == "__main__":
    rdm6300_reader = RDM6300('/dev/serial0')
    rdm6300_reader.do_work()
