import time

# This cat profile is used to store and manage the cat data. It includes the times that the cat ate, the amount of food
# eaten during every session, the name of the cat, its daily food allowance, the amount of food left and its RFID tag
class CatProfile:
    def __init__(self, rfid, name='', food_allowance=40, food_left=40, times=[], eaten =[]):
        self.RFID = rfid
        self.Name = name
        self.Daily_allowance = int(food_allowance)
        self.Food_left = int(food_left)
        self.EatingTimes = times
        self.ServingEaten = eaten

        # This allows the program to understand the current day and is used to check if the cat is able to eat
        t = time.localtime()
        timestamp = time.strftime('%Y %j', t)
        timestamp = timestamp.split(' ')
        timestamp = [int(i) for i in timestamp]
        
        self.Day = timestamp
        
        self.Able_to_eat = self.ableToEat()

    ############################################################################
    # The following functions are created to allow access outside of the class #
    ############################################################################

    # This can be used to change the cat's RFID tag, whether the owner wants to go from microchip to rfid tag or vice
    # versa
    def setRFID (self, setNewID):
        self.RFID = setNewID
    # Return the RFID Tag when prompted
    def getRFID (self):
        return self.RFID
    # Change the daily allowance of the cat, dependent on whether the owner believes their cat should have more food
    def setDailyAllowance (self, newAmount):
        self.Daily_allowance = newAmount
    # Return the daily allowance
    def getDailyAllowance (self):
        return self.Daily_allowance
    # Return how much food the cat has left
    def getFoodLeft (self):
        return self.Food_left
    # Used in conjunction with the scale and is called to update how much food the cat has left
    def setFoodLeft (self, delta):
        #Reduce amount of food left for the day based on how much the
        #The cat has eaten in the last feeding Session, based on the
        #the load cells delta
        self.Food_left = delta
        return self.Food_left
    # This updates the day to a new day when called
    def setDay (self, timestamp):
        self.Day = timestamp
        self.Able_to_eat = True
    # Returns the year and day of the year (out of 365)
    def getDay (self):
        return self.Day
    # Checks the saved day and compares it with the current day to see if the cat can eat again
    def updateDay(self):
        t = time.localtime()
        timestamp = time.strftime('%Y %j', t)
        timestamp = timestamp.split(' ')
        timestamp = [int(i) for i in timestamp]
        day = self.getDay()
        if timestamp[0] > day[0] or timestamp[1] > day[1]:
            self.setDay(timestamp)
            self.Food_left = self.Daily_allowance
            return True
        return False
    # Extended user feature to add more food, at the owner's request, for the cat if the food runs out
    #def owner_override(self, amount):
    #    self.Food_left += amount
    #    self.ableToEat()

    # This checks to ensure that the day is current and that the cat has food left and if so it will allow the cat
    # to eat
    def ableToEat(self):
        if self.updateDay() or self.Food_left > 0:
            self.Able_to_eat = True
        else:
            self.Able_to_eat = False
        return self.Able_to_eat

    # Adds the current time to the times list as well as the amount of food eaten to the servings list
    def appendTime(self, initial_food_left):
        t = time.localtime()
        #Year, Day of the year, (24 format) Hour, Minute, Second
        timestamp = time.strftime('%Y-%j-%H-%M-%S', t)
        self.EatingTimes.append(timestamp)
        self.ServingEaten.append(initial_food_left-self.getFoodLeft())

    # Allows for printing of the class
    def PrintProfile(self):
        output = '{},{},{},{},{}'.format(self.getRFID(), self.Name, self.EatingTimes, self.ServingEaten,
                                         self.getFoodLeft())
        print(output)

    # Ouputs a string of the profile, for use with writing to a .csv file
    def PrintToTxt(self):
        output = '{},{},{},{},{}'.format(self.getRFID(), self.Name, self.EatingTimes, self.ServingEaten,
                                         self.getFoodLeft())
        return output
