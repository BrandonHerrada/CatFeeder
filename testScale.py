import RPi.GPIO as GPIO
import time
import sys
from hx711 import HX711

hx = HX711(29, 31)

def cleanAndExit():
    print ("Cleaning...")
    GPIO.cleanup()
    print ("Bye!")
    sys.exit()

def scaleInit():
  # Reading format defined by manufacturer
  hx.set_reading_format("LSB", "MSB")

  # Set how many units returned by the chip are equivalent to 1 gram
  hx.set_reference_unit(390)

def testScale():
  hx.reset()
  hx.tare()
  while True:
      try:
        print ("HX711 Scale tester. Calibrated for 5kg weight sensor. Displayed values are in grams")
        keyboard = raw_input("Enter a to print 20 values\nEnter c to print infinite values\n Press Ctrl+C to exit.\n>")
        avg_index=0
        current_sum=0
        measured_avg=0
        actual=0
        if keyboard == "a":
          #reads 20 values and calculates the average
          for counter in range (20):
            # Read a value
            w = hx.get_weight(5)
            print ("    Got value " + str(counter) + "/20: " + str(w))
            current_sum += w
            # Reset the input pins
            hx.power_down()
            hx.power_up()
            time.sleep(0.1)
          measured_avg=(current_sum/20)

          print ("Average is: "+str(measured_avg))
          hx.power_down()
          hx.power_up()
          time.sleep(0.1)
        if keyboard == "c":
          #reads values until interuppted by ctrl+c
          while True:
            #Read a value
            w = hx.get_weight(5)
            print ("    Got value :"+str(w))
            current_sum += w
            #Reset the input pins
            hx.power_down()
            hx.power_up()
            time.sleep(0.1)
      except (KeyboardInterrupt, SystemExit):
          cleanAndExit()

if __name__ == "__main__":
  GPIO.cleanup()
  #Initialise HX711 object (see HX711.py)
  hx=HX711(29,31)
  scaleInit()
  hx.listen()
  testScale()