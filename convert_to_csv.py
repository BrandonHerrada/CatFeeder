import csv
import sys

''' Cat Class
Class created to store specific information of each cat
Parameters: 	rfid - tag serial
			  	name - cat name
				time - eating time stamps
				allow - total allowed food amount  
				ate - amount ate in respect with time stamps

Returns: none
'''
class Cat:
	'''
	Constructor - initialize a cat
	param: rfid, name
	return: none
	'''
    def __init__(self, rfid, name):
        self.rfid = rfid
        self.name = name
        self.time = []
        self.allow = 0.0
        self.ate = []

	'''
	add time stamp to this.time
	param: tstamp - array of time stamps
	modifies: this.time
	returns: none
	'''
    def add_time(self, tstamp):
        self.time = [x for x in tstamp]
        
	'''
	add ate food amount to this.ate
	param: left - array of ate food amount 
	modifies: this.ate
	returns: none
	'''
    def add_foot_ate(self, left):
        self.ate = [x for x in left]
        
	'''
	change total allowance
	param: allow - float(total allowance)
	modifies: this.allow
	returns: none
	'''
    def change_allow(self, allow):
        self.allow = allow
		
#main class
if __name__ == '__main__':
    ### Open sensor data, and output file
    inputfile1 = sys.argv[1]
    outputfile = sys.argv[2]
    datafile = open(inputfile1)
    output = open(outputfile, 'w')

    ### Read sensor data
    inputreader = csv.reader(datafile, delimiter=',')
    inputreader.next() # Skip header
    cat = []
	
    # Read line by line, store information
    for row in inputreader:
        if len(row) == 0:
            continue
        catid = str.strip(row[0])
        name = str.strip(row[1])
        time = []
        amount = []
        for i in range(2,len(row)-1):
            if '-' in row[i]: #it is a time stamp
                t = str.strip(row[i])
                t = t.replace("[", '')
                t = t.replace("]", '')
                t = t.split('-')
                time.append(t[2]+'-'+t[3]+'-'+t[4])
            else:			# it is a food amount
                a = str.strip(row[i])
                a = a.replace('[', '')
                a = a.replace(']', '')
                amount.append(float(a))
        allowance = float(row[-1])
        c = Cat(catid, name)
        c.change_allow(allowance)
        c.add_time(time)
        c.add_foot_ate(amount)
        cat.append(c)

    datafile.close()
	
    ### Output to csv
    outputstr = "#rfid, name, time ate, amount ate (g), allowance left (g)\n"
    output.write(outputstr)
    for c in cat:
        rfid = c.rfid
        name = c.name
        allow = c.allow
        for i in range(len(c.time)):
            allow -= c.ate[i]
            outputstr = rfid + "," + name + ","+ c.time[i]+","+str(c.ate[i]) + "," + str(allow)+"\n"
            output.write(outputstr)
    
    output.close()
