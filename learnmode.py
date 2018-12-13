from catProfile import *
import RPi.GPIO as GPIO
from rdm6300 import RDM6300
import time
import serial

if __name__ == "__main__":

    # Initialize Raspberry Pi Pins
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(35, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Initialize RFID Reader
    rdm6300_reader = RDM6300('/dev/serial0')
    print("Creating serial connection")
    serial_connection = serial.Serial(rdm6300_reader.getSerial(), rdm6300_reader.getBaudrate())
    print("Serial connection created")

    # Create dictionary
    catProfiles = {}
    while (True):
        try:
            # Read curent tag
            rfid_tag = rdm6300_reader.listen(serial_connection)
            print("RFID: {}".format(rfid_tag))
            # Check if there is a cat is within range(0000 means no cat)
            print(GPIO.input(35))
            if rfid_tag != "000000000000":
                # If the pushbutton is pressed and the cat is within range create a profile for the cat
                if catProfiles.get(rfid_tag) == None and GPIO.input(35):
                    print("Cat Profile being created")
                    catProfiles[rfid_tag] = CatProfile(rfid_tag)
                    cat = catProfiles[rfid_tag]
                    print("Cat profile")
                    cat.PrintProfile()
            time.sleep(2)
            serial_connection.flushInput()
        except (KeyboardInterrupt, SystemExit):
            print("Keyboard interrupt or system exit called")
            serial_connection.close()