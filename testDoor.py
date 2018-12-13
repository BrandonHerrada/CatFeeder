import RPi.GPIO as GPIO
from time import sleep
import sys
import serial
from rdm6300 import RDM6300
from MotorControl import *

# Raspberry Pi Pins
Motor1A = 13
Motor1B = 15
PWM = 16
limit_open = 24
limit_closed = 26

# Initialize Raspberry Pi Pins
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setup(Motor1A, GPIO.OUT)
GPIO.setup(Motor1B, GPIO.OUT)
GPIO.setup(PWM, GPIO.OUT)
GPIO.output(Motor1A, GPIO.LOW)
GPIO.output(Motor1B, GPIO.LOW)
GPIO.output(PWM, GPIO.LOW)
Motor_PWM = GPIO.PWM(PWM, 200)
Motor_PWM.start(0)

GPIO.setup(limit_closed, GPIO.IN)
GPIO.setup(limit_open, GPIO.IN)

# Initialize RFID Scanner
rdm6300_reader = RDM6300('/dev/serial0')
print("Creating serial connection")
serial_connection = serial.Serial(rdm6300_reader.getSerial(), rdm6300_reader.getBaudrate())
print("Serial connection created")

if __name__ == "__main__":
    # Print current Tag read
    print(rdm6300_reader.listen(serial_connection))
    while(True):
        serial_connection.flushInput()
        # Save currently read value from RFID reader as rfid_tag
        rfid_tag = rdm6300_reader.listen(serial_connection)
        # If RFID Tag is nearby
        if rfid_tag != "000000000000":
            print("Door Opening!")
            # Open door
            speedControl(Motor_PWM,1,100,'f',0)
            serial_connection.flushInput()

            # As long as a non-zero RFID tag is read keep door open
            while rdm6300_reader.listen(serial_connection) != "000000000000":
                serial_connection.flushInput()

            # Close door when tag is no longer read
            print("Door Closing!")
            speedControl(Motor_PWM,1,100,'b',0)
