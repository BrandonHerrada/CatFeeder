import RPi.GPIO as GPIO
from time import sleep
import sys


#Set pinmode to GPIO number
GPIO.setmode(GPIO.BOARD)

#motor1_init
Motor1A = 13
Motor1B = 15
PWM = 16
GPIO.setup(Motor1A, GPIO.OUT)
GPIO.setup(Motor1B, GPIO.OUT)
GPIO.setup(PWM, GPIO.OUT)
#Set Motor PWM to pin with Frequency of 500 Hz
Motor_PWM = GPIO.PWM(PWM, 200)

#Set Motor1 to 0
Motor_PWM.start(0)
GPIO.output(Motor1A, GPIO.LOW)
GPIO.output(Motor1B, GPIO.LOW)
GPIO.output(PWM, GPIO.LOW)

#motor2_init
Motor2A = 11
Motor2B = 18
GPIO.setup(Motor2A, GPIO.OUT)
GPIO.setup(Motor2B, GPIO.OUT)

GPIO.output(Motor2A, GPIO.LOW)
GPIO.output(Motor2B, GPIO.LOW)


def speedControl(motor, motor_num, pwm_value, direction, duration):
    if motor_num == 1:
        PinA = Motor1A
        PinB = Motor1B
    else:
        PinA = Motor2A
        PinB = Motor2B
    motor.ChangeDutyCycle(pwm_value)    
    if direction == 'f':
        GPIO.output(PinA, GPIO.HIGH)
        GPIO.output(PinB, GPIO.LOW)
        GPIO.output(PWM, GPIO.HIGH)
    elif direction == 'b':
        GPIO.output(PinA, GPIO.LOW)
        GPIO.output(PinB, GPIO.HIGH)
        GPIO.output(PWM, GPIO.HIGH)
    else:
        GPIO.output(PinA, GPIO.LOW)
        GPIO.output(PinB, GPIO.LOW)
        GPIO.output(PWM, GPIO.LOW)
    sleep(duration)

if __name__ == "__main__":
    while(True):
        print("test")
        try:
            speedControl(Motor_PWM, 1, 100, 'b', 0.5)
            #speedControl(Motor_PWM, 1, 100, 'f', 0.25)
            #speedControl(Motor_PWM, 1, 50, 'b', 0.5)
            #speedControl(Motor2, 2, 15, 'f', 0.5)
            #GPIO.output(Motor1B,GPIO.HIGH)
            #GPIO.output(Motor1E,GPIO.HIGH)
            #GPIO.output(Motor1A,GPIO.HIGH)
            #sleep(1)

        except (KeyboardInterrupt, SystemExit):
            GPIO.cleanup()
            break
