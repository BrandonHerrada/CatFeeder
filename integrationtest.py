import RPi.GPIO as GPIO
import time
import sys
from rdm6300 import RDM6300
import time
import serial
from catProfile import *
import convert_to_csv
from MotorControl import *
from hx711 import HX711

# Inputs: Text file reader object
# Outputs: Returns a dictionary composed of cat Profiles
# Function Description: This allows us to read in from a .csv file containing sensor data pertaining to cats and create a dictionary
#           of cat profiles that allows us to reference to detect a cat and figure out if it is able to eat or not
def MakeProfiles(read_input):
    catProfiles = {}
    read_input.next()
    for row in read_input:
        if len(row) == 0:
            continue
        row = row.split(',')
        catid = str.strip(row[0])
        name = str.strip(row[1])
        times = []
        amount = []
        for i in range(2,len(row)-1):
            if '-' in row[i]:
                t = str.strip(row[i])
                t = t.replace("[", '')
                t = t.replace("]", '')
                times.append(t)
            else:
                a = str.strip(row[i])
                a = a.replace('[', '')
                a = a.replace(']', '')
                amount.append(int(a))
        allowance = int(row[-1])
        catProfiles[catid] = CatProfile(catid, name, allowance, allowance, times, amount)
    return catProfiles

#Pin numbers
Motor1A = 13
Motor1B = 15
PWM = 16
Motor2A = 11
Motor2B = 18
limit_open = 24
limit_closed = 26
pushbutton = 37

#Initialize Raspberry Pi Pins
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)

#Inilialize RFID Reader
rdm6300_reader = RDM6300('/dev/serial0')
print("Creating serial connection")
serial_connection = serial.Serial(rdm6300_reader.getSerial(), rdm6300_reader.getBaudrate())
print("Serial connection created")

#Iniitialize Motors to Raspberry Pi Pins
# Set motor PWM control to Pin 16 with Frequency of 200 Hz
GPIO.setup(Motor1A, GPIO.OUT)
GPIO.setup(Motor1B, GPIO.OUT)
GPIO.setup(PWM, GPIO.OUT)
GPIO.setup(Motor2A, GPIO.OUT)
GPIO.setup(Motor2B, GPIO.OUT)
GPIO.output(Motor1A, GPIO.LOW)
GPIO.output(Motor1B, GPIO.LOW)
GPIO.output(PWM, GPIO.LOW)
GPIO.output(Motor2A, GPIO.LOW)
GPIO.output(Motor2B, GPIO.LOW)
Motor_PWM = GPIO.PWM(PWM, 200)
GPIO.setup(limit_open, GPIO.IN)
GPIO.setup(limit_closed, GPIO.IN)
Motor_PWM.start(0)

#Inilaize Learn Mode Pushbutton
GPIO.setup(pushbutton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#Inilialize Scale to Pins 29, 31
print("Initializing Scale")
Scale = HX711(29, 31)
Scale.set_reading_format("LSB", "MSB")
#Set Scale Reference Value
Scale.set_reference_unit(390)
Scale.reset()
Scale.tare()
Scale.power_down()
Scale.power_up()
#Take initial weight of bowl with food in it
initial_weight = Scale.get_weight(5)
print("Startup weight:"+str(initial_weight))

if __name__ == "__main__":
    #sensor_data.txt is the .csv file we read profiles from
    read_input = open('sensor_data.txt')
    #Somehow convert csv database to profiles
    catProfiles = MakeProfiles(read_input)
    #Cat profile imported into the dictionary for use in testing and detecting rfid from distributed tags
    times = ['2018-360-10-37-20','2018-360-10-37-21']
    amount = [50,10]
    catProfiles['1D00278983'] = CatProfile('1D00278983','Felix','50','40',times,amount)

    #This is used for an extended user feature of adding upload and save times
    #uploaded, saved = False, False

    #This is the main loop that will run as long as the user does not do a Keyboard Interrupt (CTRL + T)
    while(True):
        try:
            #Listen for an RFID in range of the scanner
            rfid_tag = rdm6300_reader.listen(serial_connection)
            print("RFID Tag: {}".format(rfid_tag))

            #Check if there is a cat (0000 means no cat)
            if rfid_tag != "000000000000":
                #Check to see if the cat
                if(catProfiles.get(rfid_tag) != None and not catProfiles[rfid_tag].ableToEat()):
                    print("Cat not allowed to eat, door will not open")
                elif catProfiles.get(rfid_tag) != None and catProfiles[rfid_tag].ableToEat():
                    cat = catProfiles[rfid_tag]
                    #open Food Door
                    print("RFID Tag Found in database")
                    print("Open door")
                    speedControl(Motor_PWM, 1, 100, 'f', 0)
                    Scale.power_down()
                    Scale.power_up()
                    #Read the initial weight on the scale
                    initial = Scale.get_weight(5)
                    #Set variable startingFoodLeft to cat's current food left value
                    startingFoodLeft = cat.getFoodLeft()
                    print("Starting food left: {}".format(startingFoodLeft))
                    print("Scale reads (initial weight):"+str(initial)+".\n Flushing serial input to read tag")
                    serial_connection.flushInput()
                    rfid_tag2 = rdm6300_reader.listen(serial_connection)
                    print("RFID scanner reads: {}".format(rfid_tag2))

                    #Ensure that the cat is still able to eat by updating the amount of food it has left for the day and
                    #that it is within range of the scanner
                    while(cat.ableToEat() and cat.getRFID() == rfid_tag2):
                        print("Cat is within range and has food left for the day")
                        #Read load cell data and wait until cat has eaten daily allowance or id is no longer read
                        new_weight = Scale.get_weight(5)
                        print("New weight: {}".format(new_weight))
                        print("Setting food left to {}".format(startingFoodLeft-(initial-new_weight)))
                        cat.setFoodLeft(startingFoodLeft - (initial-new_weight))
                        print("foodLeft="+str(cat.getFoodLeft()))
                        #Read once every 1 seconds
                        time.sleep(1)
                        serial_connection.flushInput()
                        rfid_tag2=rdm6300_reader.listen(serial_connection)
                        #If scanner cannot read cat id, it will try again and if it doesnt read it will close the door
                        if(rfid_tag2!=cat.getRFID()):
                            print("Scanned 0000, trying again in case this was an uncertainty thing")
                            time.sleep(1)
                            serial_connection.flushInput()
                            rfid_tag2 = rdm6300_reader.listen(serial_connection)
                        print("RFID scanner reads: {}".format(rfid_tag2))
                        Scale.power_down()
                        Scale.power_up()
                    #Append eating time and food left value
                    print("Cat is done eating, saving time")
                    cat.setFoodLeft(startingFoodLeft-(initial-Scale.get_weight(5)))
                    print("Cat has {} grams of food left for the day".format(cat.getFoodLeft()))
                    cat.appendTime(startingFoodLeft)
                    #Close door
                    print("Closing door")
                    speedControl(Motor_PWM, 1, 100, 'b', 0)
                    #Extended User Feature: if cat runs out of food upload updated file to drive and alert the owner
                #Learn mode is enabled if the push button is pressed and the rfid tag is not already in the dictionary
                elif catProfiles.get(rfid_tag) == None and GPIO.input(pushbutton):
                    catProfiles[rfid_tag] = CatProfile(rfid_tag)
            #wait 2 seconds
            time.sleep(2)
            serial_connection.flushInput()
            #Update the .csv database file after every loop
            outputstr = "#RFID, Name, Times Eaten, Amount Eaten (g), Daily Food Allowance Left (g)\n"
            out = open('sensor_data.txt', 'w')
            out.write(outputstr)
            for i in catProfiles:
                cat = catProfiles[i]
                out.write(cat.PrintToTxt())
                out.write('\n')
            out.close()

            #This will in theory upload to the google drive and update the .csv file throughout times of the day
            '''
            t = time.localtime()
            current_time = time.strftime('%H-%M', t)
            #Upload at 5pm, this allows for it to be uploaded if the cat continues to eat more than a minute at the start of the hour
            if current_time[0:2] == '17' and uploaded == False:
                #Upload to drive
                uploaded = True
            #Save to database every hour
            if current_time[3] == '1' or saved == False:
                #Save to Database
                saved = True
                for i in catProfiles:
                    print(i)
            if current_time[3] == '59' and saved == True:
                saved = False
            #Verify structure of numbers
            if current_time[0:2] == '00' and uploaded == True:
                uploaded = False
            '''
            #Refill Cat food by testing the weight
            while (Scale.get_weight(5) < -60):
                print(Scale.get_weight(5))
                speedControl(Motor_PWM, 2, 100, 'b', 0.2)
                if (Scale.get_weight(5) > -60):
                    break
                speedControl(Motor_PWM, 2, 100, 'f', 0.1)
            #Extended User Feature: update local cat profiles if any changes have been made every hour or so
        except (KeyboardInterrupt, SystemExit):
            print("Keyboard interrupt or system exit called")
            serial_connection.close()
            Scale.cleanAndExit()
