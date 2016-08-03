import RPi.GPIO as GPIO
from time import sleep
from flask import Flask, render_template,request,jsonify
from multiprocessing import Process
app=Flask(__name__)
import time
import threading
import hashlib
m = hashlib.md5()
#from hcsr04sensor import sensor

passphrase = "oladipo"
m.update(passphrase)
passPhraseHash=str(m.hexdigest())
m.digest()


ticks=time.time()
previousActivityList =[None]*20
previousActivityNameList = ['']*20
trigDoorPin=24
echoDoorPin=23
trigCarPin=12
echoCarPin=26
doorThreshold = 180 #inverse logic
carThreshold=115
stateForDoor = "initialize"
stateForCar = "initialize"
GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.OUT)
GPIO.setup(15,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.output(4,GPIO.LOW)
GPIO.setup(trigDoorPin,GPIO.OUT)                  #Set pin as GPIO out
GPIO.setup(echoDoorPin,GPIO.IN)                   #Set pin as GPIO in
GPIO.setup(trigCarPin,GPIO.OUT)
GPIO.setup(echoCarPin,GPIO.IN)

garageData = {'SystemStatus':101,'isCar':True,'isClosed':False,'timeSinceLast':'17:32','timelineDataTimes':previousActivityList,
'timelineDataActivity':previousActivityNameList,'uptime':ticks,'lastActivityTime':0.0,'lastActivity':'Undefined'
}
statusCodes={'ok':101,'UltrasonicMalfunction':202,'GarageDoorMalfunction':404,'unknown':660}
#Basic Function
def openClose():
    GPIO.output(4,GPIO.HIGH)
    sleep(.5)
    GPIO.output(4,GPIO.LOW)

#Door Functions
def getDoorDistance():
    inCM=0
    dataList  = [None]*7
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
    return inCM

#Using a mild stateForDoor achine for error checking. Won't say closed/open unless it's been closed previously.
def isDoorClosed():
    #return GPIO.input(doorSensorPin)  #If using Reed Sensor
    distance = getDoorDistance()
    #garageData['timeSinceLast'] = distance  #For Debugging
    currState = distance > doorThreshold
    global stateForDoor
    if (currState and not garageData['isClosed']) or ((currState==0) and  garageData['isClosed']) :   #We think it just closed or just opened. stateForDoor should be volatile now
        if stateForDoor == "v1":
            stateForDoor = "v2"
            return garageData['isClosed']
        elif stateForDoor == "v2":
            stateForDoor = "okay"
            return currState
        else:
            stateForDoor = "v1"
            return garageData['isClosed']
    return currState

def updateDoorStatus():
    #while True:
    isDoorClosedBool = isDoorClosed()
    if isDoorClosedBool and not garageData['isClosed']: #Meaning the garage door was just closed
        garageData['lastActivityTime']=garageData['timeSinceLast'] = time.time()
        garageData['lastActivity'] = 'Closed'
        garageData['timelineDataTimes'].insert(0,time.time())
        garageData['timelineDataTimes'].pop()
        garageData['timelineDataActivity'].insert(0,'Closed')
        garageData['timelineDataActivity'].pop()
    elif  (isDoorClosedBool==0) and  garageData['isClosed']:
        garageData['lastActivityTime']=garageData['timeSinceLast'] = time.time()
        garageData['lastActivity'] = 'Opened'
        garageData['timelineDataTimes'].insert(0,time.time())
        garageData['timelineDataTimes'].pop()
        garageData['timelineDataActivity'].insert(0,'Opened')
        garageData['timelineDataActivity'].pop()


    garageData['isClosed'] =  isDoorClosedBool
    print('isDoorClosedBool :',isDoorClosedBool)
    #print('garageData[''isClosed''] :',garageData['isClosed'])
    #threading.Timer(1,updateDoorStatus).start() #every second.
    #sleep(3)

def checkForGarageDoorErrors():
    for i in enumerate(garageData['timelineDataTimes'][1:]):
        if abs(garageData['timelineDataTimes',i] - garageData['timelineDataTimes',i+1]) < 24:
            garageData['timelineDataActivity'].pop(i+1)
            garageData['timelineDataActivity'].pop(i)
            garageData['timelineDataTimes'].pop(i+1)
            garageData['timelineDataTimes'].pop(i)
            break

'''
    if garageData["timelineDataActivity"][0] == garageData["timelineDataActivity"][1]:
        return err
'''


#Check for Car (Ultrasonic)
def getCarDistance():
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
    #
def updateCarStatus():
    ''' NOT Sure I NEED THIS
    if isCar() and not garageData['isCar']: #Meaning the Car just arrived
        garageData['isCar'] = True
    elif not isCar() and garageData['isCar']: #Meaning the car just left
        garageData['isCar'] = False
    '''
    #while True:
    garageData['isCar'] = isCar()
    #threading.Timer(5,updateCarStatus).start() #every second.
    #sleep(5)

#Ultrasonic Workings
def readUltra(trig,echo):
      GPIO.output(trig, False)                 #Set trig as LOW
      #Would sleep for 2 secs to settle sensor but we avoid that by not reading more than 5 times a sec (10 times actually)
      sleep(.01)
      GPIO.output(trig, True)
      sleep(0.00001)
      GPIO.output(trig, False)
      while GPIO.input(echo)==0:               #Check whether the echo is LOW
        pulse_start = time.time()              #Saves the last known time of LOW pulse

      while GPIO.input(echo)==1:               #Check whether the echo is HIGH
        pulse_end = time.time()

      pulse_duration = pulse_end - pulse_start #Get pulse duration to a variable
      distance = pulse_duration * 17150        #Multiply pulse duration by 17150 to get distance
      distance = round(distance, 2)            #Round to two decimal points
      if distance > 2 and distance < 400:      #Check whether the distance is within range
          pass #print "Distance:",distance - 0.5,"cm"  #Print distance with 0.5 cm calibration
      else:
        print("Out Of Range")                   #display out of range
      return distance
def median(lst):
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2

    if (lstLen % 2):
        return sortedLst[index]
    else:
        return (sortedLst[index] + sortedLst[index + 1])/2.0

@app.route("/")
def main():
    return "Hello there"
passPhraseHashToggle = '/toggle' + passPhraseHash
@app.route(passPhraseHashToggle)
def toggle():
    openClose()
    sleep(12)
    return "All Good"

@app.route("/data"+passPhraseHash)
def data():
    return jsonify(**garageData)

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
    app.run(host='0.0.0.0',port=6011,debug=True,use_reloader=False)

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

set_interval(updateDoorStatus,3)
set_interval(updateCarStatus,5)
#set_interval(checkForGarageDoorErrors,30)
#set_interval(test,3)

#updateDoorStatus()
#updateCarStatus()
if __name__ =="__main__":
    runApp()
    '''
    p1=Process(target=updateDoorStatus)
    p1.start()
    p2=Process(target = updateCarStatus)
    p2.start()
    p3=Process(target = runApp)
    p3.start()
    '''
