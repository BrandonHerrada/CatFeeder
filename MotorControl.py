import RPi.GPIO as GPIO
import time
import sys

# Raspberry pi pins
Motor1A = 13
Motor1B = 15
PWM = 16
Motor2A = 11
Motor2B = 18

# Inputs: (Object) PWM motor controller, (Integer) Motor Number (1 or 2), (Integer) PWM value (0-100%),
# (String) direction that we want to go, (Float) time we want it to run
# Outputs: None
# Description: This will allow the motor to run based on what the user inputs into it, it works for both motors and will
# allow for many combinations of actions. It allows for different speeds and the amount of time to run the motor.
def speedControl(motor, motor_num, pwm_value, direction, duration):

    # Set PinA & PinB to respective pin numbers set by motor number
    if motor_num == 1:
        PinA = Motor1A
        PinB = Motor1B
    else:
        PinA = Motor2A
        PinB = Motor2B

    # If forward assign pins to allow for forward movement and use limit switch with pin 24
    if direction == 'f':
        print("Driving motor {} Forward".format(motor_num))
        limit_switch = 24
        GPIO.output(PinA, GPIO.HIGH)
        GPIO.output(PinB, GPIO.LOW)
        GPIO.output(PWM, GPIO.HIGH)
        runtime = 2
    # If backward assign pins to allow backward movement and use limit switch with pin 26
    elif direction == 'b':
        print("Driving motor {} Backward".format(motor_num))
        limit_switch = 26
        GPIO.output(PinA, GPIO.LOW)
        GPIO.output(PinB, GPIO.HIGH)
        GPIO.output(PWM, GPIO.HIGH)
        runtime = 2
    else:
        limit_switch = 0
        GPIO.output(PinA, GPIO.LOW)
        GPIO.output(PinB, GPIO.LOW)
        GPIO.output(PWM, GPIO.LOW)
    if motor_num == 1:
        limit = False
        motor.ChangeDutyCycle(pwm_value)
        # Run until limit switch is hit or time exceeds estimated time to close door
        # Attempt until door closes
        while not limit:
            start = time.time()
            motor.ChangeDutyCycle(pwm_value)
            print("Waiting for door limit to engage")
            while(time.time()-start < runtime):
                if GPIO.input(limit_switch) == 1:
                    print("Limit Engaged")
                    limit = True
                    break
            # if door does not close try again after 2 seconds
            print("Limit not broken, retrying in 2 seconds")
            if not limit:
                motor.ChangeDutyCycle(0)
                time.sleep(2)
    else:
        print("Running Motor 2")
        motor.ChangeDutyCycle(pwm_value)
        #Read scale test by running for .5 second, reading scale then repeating until maximum is reached
        time.sleep(duration)
    print("Turning off motor")
    motor.ChangeDutyCycle(0)
    GPIO.output(PinA, GPIO.LOW)
    GPIO.output(PinB, GPIO.LOW)
    GPIO.output(PWM, GPIO.LOW)