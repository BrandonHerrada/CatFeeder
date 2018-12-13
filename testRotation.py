import RPi.GPIO as GPIO
from time import sleep
import sys
from hx711 import HX711
from MotorControl import *

# Raspberry Pi Pins
Motor2A = 11
Motor2B = 18
PWM = 16

# Initialize Pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(Motor2A, GPIO.OUT)
GPIO.setup(Motor2B, GPIO.OUT)
GPIO.setup(PWM, GPIO.OUT)
GPIO.output(Motor2A, GPIO.LOW)
GPIO.output(Motor2B, GPIO.LOW)
GPIO.output(PWM, GPIO.LOW)
Motor_PWM = GPIO.PWM(PWM, 200)
Motor_PWM.start(0)

if __name__ == "__main__":
    # Run motor for ~60 degrees of movement
    speedControl(Motor_PWM, 2, 30, 'f', 0.41)
