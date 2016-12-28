'''
Written By Ope Oladipo
This is some code i wrote to serve a a framework of monitoring and controlling your garage using ultrasonic sensors, a relay and a microcontroller.
This is specific to the raspberry pi


'''
import RPi.GPIO as GPIO                     #To be used to access GPIO pins
from time import sleep
from flask import Flask, render_template,request,jsonify  #To make our server
app=Flask(__name__)
import time
import threading
import hashlib                                              #to generate md5 hash
m = hashlib.md5()
#from hcsr04sensor import sensor

passphrase = "passphrase"                                   #default hashphrase
if passphrase != "":                                        #IF passphrase is blank, hashphrase = ""
    m.update(passphrase)
    passPhraseHash=str(m.hexdigest())
    m.digest()
else :
    passPhraseHash=""

ticks=time.time()                                           #Current time
previousActivityList =[None]*20                             #Array of garage activity times
previousActivityNameList = ['']*20                          #Array of garage activity actions (i.e. opened or closed)
trigDoorPin=24                                              #Trigger pin for ultrasonic targeting the door. Using BCM Mode on RaspPi
echoDoorPin=23
trigCarPin=12
echoCarPin=26
doorThreshold = 180 #inverse logic                          #By inverse logic i mean garage is open if below threshold due to pointing the sensor at the top of the garage
carThreshold=115                                            #If distance is above this threshold car is there
stateForDoor = "initialize"                                 #Needed a ranom string to start (or no string)
stateForCar = "initialize"
GPIO.setmode(GPIO.BCM)                                      #Needed config. Google 'BCM'
GPIO.setup(4,GPIO.OUT)                                      #Setting up IO pins
GPIO.setup(15,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.output(4,GPIO.LOW)
GPIO.setup(trigDoorPin,GPIO.OUT)                            #Set pin as GPIO out
GPIO.setup(echoDoorPin,GPIO.IN)                             #Set pin as GPIO in
GPIO.setup(trigCarPin,GPIO.OUT)
GPIO.setup(echoCarPin,GPIO.IN)

garageData = {'SystemStatus':101,'isCar':True,'isClosed':False,'timeSinceLast':'17:32','timelineDataTimes':previousActivityList,
'timelineDataActivity':previousActivityNameList,'uptime':ticks,'lastActivityTime':0.0,'lastActivity':'Undefined'
} #initializing data pool.
statusCodes={'ok':101,'UltrasonicMalfunction':202,'GarageDoorMalfunction':404,'unknown':660}  #initializing status codes
#Basic openClose Function
def openClose():                                            #Basically, turn on the relay for half a second (.01 seconds wasn't working sooo). This'll trigger the garage door.
    GPIO.output(4,GPIO.HIGH)
    sleep(.5)
    GPIO.output(4,GPIO.LOW)

#Door Functions
def getDoorDistance():                                      #This returns the distance of the door from the Door sensor. This returns the median of 8 tries (and can still be inaccurate)
    inCM=0
    dataList  = [None]*8
    try:
        for x in range(0,7):
            tempDistance = readUltra(trigDoorPin,echoDoorPin)
            if tempDistance != 0:
                dataList[x] = tempDistance
            else:
                sleep(.01)
                dataList[x] = readUltra(trigDoorPin,echoDoorPin)
            sleep(.4)
        inCM=median(dataList)
    except :
        pass
    print ('Door distance is' , inCM )
    return inCM                                             #returns result in cm

#Using a mild stateForDoor machine for error checking. Won't say closed/open unless it's been closed previously twice. Redundancy is essential to US sensors.
def isDoorClosed():
    #return GPIO.input(doorSensorPin)                       #If using Reed Sensor <--- That's all you need.
    distance = getDoorDistance()
    currState = distance > doorThreshold                    #Current state is true if door distance > thrreshold
    global stateForDoor                                     #Required to use variable in function
    if (currState and not garageData['isClosed']) or ((currState==0) and  garageData['isClosed']) :   #We think it just closed or just opened. stateForDoor should be volatile now
        if stateForDoor == "v1":                            #v1 stands for volatile state 1
            stateForDoor = "v2"                             #v2=volatile2. We set the door state to volatile2 meaning we're a little more sure of its state.
            return garageData['isClosed']
        elif stateForDoor == "v2":                          #v2 -> okay means we can return the current state as it has remain unchanged for 2 cycles meaning it's most likely right.
            stateForDoor = "okay"
            return currState
        else:
            stateForDoor = "v1"
            return garageData['isClosed']
    return currState

def updateDoorStatus():
    isDoorClosedBool = isDoorClosed()
    if isDoorClosedBool and not garageData['isClosed']:   #Meaning the garage door was just closed
        garageData['lastActivityTime']=garageData['timeSinceLast'] = time.time()        #fill out data.
        garageData['lastActivity'] = 'Closed'
        garageData['timelineDataTimes'].insert(0,time.time())
        garageData['timelineDataTimes'].pop()
        garageData['timelineDataActivity'].insert(0,'Closed')
        garageData['timelineDataActivity'].pop()
    elif  (isDoorClosedBool==0) and  garageData['isClosed']:#Meaning the garage door was just opened
        garageData['lastActivityTime']=garageData['timeSinceLast'] = time.time()
        garageData['lastActivity'] = 'Opened'
        garageData['timelineDataTimes'].insert(0,time.time())
        garageData['timelineDataTimes'].pop()
        garageData['timelineDataActivity'].insert(0,'Opened')
        garageData['timelineDataActivity'].pop()

    garageData['isClosed'] =  isDoorClosedBool
    print('isDoorClosedBool :',isDoorClosedBool)

def checkForGarageDoorErrors(): #This is kind of unfinished. Feel free to email me/pull request code that fits the bill. i got too busy with the app.
    '''
    for i in enumerate(garageData['timelineDataTimes'][1:]):
        if abs(garageData['timelineDataTimes',i] - garageData['timelineDataTimes',i+1]) < 24:
            garageData['timelineDataActivity'].pop(i+1)
            garageData['timelineDataActivity'].pop(i)
            garageData['timelineDataTimes'].pop(i+1)
            garageData['timelineDataTimes'].pop(i)
            break
    '''

def getCarDistance():                                       #Check for Car (Ultrasonic) Pretty much the same as getDoorDistance() but with median of 3 instead.
    inCM=0
    dataList  = [None]*3
    try:
        sleep(.2)
        for x in range(0,2):
            tempDistance = readUltra(trigCarPin,echoCarPin)
            if tempDistance != 0:
                dataList[x] = tempDistance
            else:
                sleep(.05)
                dataList[x] = readUltra(trigCarPin,echoCarPin)
            sleep(.4)
            #print ('Car distance is' , tempDistance )
        inCM=median(dataList)
    except :
        pass
    print ('Car distance is' , inCM )
    return inCM

def isCar():
    distance = getCarDistance()
    currState = distance < carThreshold
    global stateForCar
    if (currState and not garageData['isCar']) or ((currState==0) and  garageData['isCar']) :   #Car state just changed. stateForCar should be volatile now
        if stateForCar == "v1":
            stateForCar = "v2"
            return garageData['isCar']
        elif stateForCar == "v2":
            stateForCar = "okay"
            return currState
        else:
            stateForCar = "v1"
            return garageData['isCar']
    return currState
    #
def updateCarStatus():
    garageData['isCar'] = isCar()


#Ultrasonic Workings
def readUltra(trig,echo):
      GPIO.output(trig, False)                              #Set trig as LOW
      #Would sleep for 2 secs to settle sensor but we avoid that by not reading more than 5 times a sec (10 times actually)
      sleep(.01)
      GPIO.output(trig, True)
      sleep(0.00001)
      GPIO.output(trig, False)
      while GPIO.input(echo)==0:                            #Check whether the echo is LOW
        pulse_start = time.time()                           #Saves the last known time of LOW pulse

      while GPIO.input(echo)==1:                            #Check whether the echo is HIGH
        pulse_end = time.time()

      pulse_duration = pulse_end - pulse_start              #Get pulse duration to a variable
      distance = pulse_duration * 17150                     #Multiply pulse duration by 17150 to get distance
      distance = round(distance, 2)                         #Round to two decimal points
      if distance > 2 and distance < 400:                   #Check whether the distance is within range
          pass                                              #print "Distance:",distance - 0.5,"cm"  #Print distance with 0.5 cm calibration
      else:
        print("Out Of Range")                               #display out of range
      return distance

def median(lst):                                            #return median
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2
    if (lstLen % 2):
        return sortedLst[index]
    else:
        return (sortedLst[index] + sortedLst[index + 1])/2.0
                                                            #Flask at work!
@app.route("/")
def main():                                                 #if http:localhost:port return "Hello there"
    return "Hello there"
@app.route('/toggle' + passPhraseHash)                      #if http:localhost:port/toggle+ '456789ifdju767tfgvyuheij2h8gftv' <- hash open/close garage.
def toggle():
    openClose()
    sleep(12)
    return "All Good"

@app.route("/data"+passPhraseHash)
def data():
    return jsonify(**garageData)                            #return garage data in JSON form.

@app.route("/status"+passPhraseHash)
def status():
    return garageData['SystemStatus']

@app.route("/toggle")
def toggle2():
    return "Please include hash at the end of the link"

@app.route("/data")
def data2():
    return "Please include hash at the end of the link"

@app.route("/status")
def status2():
    return "Please include hash at the end of the link"

def runApp():
    app.run(host='0.0.0.0',port=6011,debug=True,use_reloader=False)     #Host server on port 6011

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

set_interval(updateDoorStatus,3)                                         #enables multithreading (otherwise conflicts with server (runApp()))
set_interval(updateCarStatus,5)
#set_interval(checkForGarageDoorErrors,30)
#set_interval(test,3)

#updateDoorStatus()
#updateCarStatus()
if __name__ =="__main__":
    runApp()
