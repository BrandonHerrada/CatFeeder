import time
import serial

class RDM6300:
    SERIAL_PORT = ''
    BAUDRATE = 9600

    RDM_START = 2
    RDM_END = 3
    RDM_DATA_SZ = 20

    def __init__(self, serial_port):
        self.SERIAL_PORT = serial_port
        print ("Initialized Serial Port")

    @staticmethod
    def __verify_checksum(data, checksum):
        try:
            result = int(data[0:2], 16) \
                     ^ int(data[2:4], 16) \
                     ^ int(data[4:6], 16) \
                     ^ int(data[6:8], 16) \
                     ^ int(data[8:10], 16)
            result = format(result, 'x')

        except ValueError:
            return False

        if result.lower() != checksum.lower():
            return False
        return True

    @staticmethod
    def __fix_zeros(data):
        return data.replace(' ', '0')

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

        expected_len = 12
        while expected_len is not 0:

            expected_len -= 1
            byte_read = serial_connection.read()

            if int(ord(byte_read)) == self.RDM_START:
                expected_len = 12
                continue

            if ord(byte_read) != self.RDM_END:
                tag_string += chr(ord(byte_read))
                continue
            break

        data = tag_string[0:len(tag_string) - 2]
        checksum = tag_string[len(tag_string) - 2:len(tag_string)]
        checksum_ok = self.__verify_checksum(data, checksum)

        if not checksum_ok:
            return False
        return self.__fix_zeros(data)

    # Return Baudrate (Communication Transfer Rate)
    def getBaudrate(self):
        return self.BAUDRATE
    # Return Serial port
    def getSerial(self):
        return self.SERIAL_PORT
    # Read RFID and return data
    def listen(self, serial_connection):
        data = self.__read_sequence(serial_connection)
        # check if its an actual RFID string
        if data is False:
            print("No cat detected")
            data = "000000000000"
            return data
        else:
            return data