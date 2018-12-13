import RPi.GPIO as GPIO
from time import sleep
import sys
from hx711 import HX711
from MotorControl import *

# Raspberry Pi Pin numbers
Motor2A = 11
Motor2B = 18
PWM = 16

# Initialize raspberry pi pins
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setup(Motor2A, GPIO.OUT)
GPIO.setup(Motor2B, GPIO.OUT)
GPIO.setup(PWM, GPIO.OUT)
GPIO.output(Motor2A, GPIO.LOW)
GPIO.output(Motor2B, GPIO.LOW)
GPIO.output(PWM, GPIO.LOW)

# Set pulse width period to 1/100 s
Motor_PWM = GPIO.PWM(PWM, 100)
# Set pwm to 0% (Always off) in the duty cycle
Motor_PWM.start(0)

#Inilialize the scale
print("Initializing Scale")
Scale = HX711(29, 31)
Scale.set_reading_format("LSB", "MSB")
Scale.set_reference_unit(390)
Scale.reset()
Scale.tare()
Scale.power_down()
Scale.power_up()
# Initial weight should be 0
initial_weight = Scale.get_weight(5)
print("Startup weight:"+str(initial_weight))

if __name__ == "__main__":
    # Run the feeder until the scale reads 22 additional grams have been added
    # The purpose of this forward and backward motion is to allow for any food to be dislodged
    while(Scale.get_weight(5) < 22):
        print(Scale.get_weight(5))
        # Run the feeder motor for 0.2 seconds backward
        speedControl(Motor_PWM, 2, 100, 'b', 0.2)
        # If this released more than 22 grams break out of loop
        if(Scale.get_weight(5) > 22):
            break
        # Run motor forward  for 0.1 seconds forward
        speedControl(Motor_PWM, 2, 100, 'f', 0.1)
    # Wait 3 seconds
    sleep(3)
    print("Final Food amount added(g): {}".format(Scale.get_weight(5)))