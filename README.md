[Pretty version](https://cdn.rawgit.com/oooseun/MyGarage/master/mygarage.html)

Demo -> https://www.youtube.com/watch?v=1Qu-76sq3Ak 
MyGarage DIY
==

Intro
----------
You're in bed at 11:30 PM, watching TV. Then you come to the sudden realization that you might have left the garage open ? What do you do ? Struggle out of bed all the way to the garage to find out it was actually closed (or open). Only if there was a way to know if your garage was open without going through the struggle.

This application was made in as an attempt to cheaply & easily automate one's garage. I think i was a little successful with this as all the parts could be bought for about $20. I'd advice splurging a little more and getting higher quality parts though. The main idea here is we have a server hooked up to a relay and some ultrasonic sensors. These sensors read and interact with the Raspberry Pi to provide information that can be accessed via the server.

#### <i class="icon-file"></i> Parts

- [Raspberry Pi Zero](https://www.adafruit.com/product/2885)
- [2 Ultrasonic Sensors](http://amzn.to/2b4kPcx)
- [Wifi Dongle](http://amzn.to/2aB6Dmd)*
- [SD card (4 or 8gb)](http://amzn.to/2aB7wLD)
- [Simple relay](http://amzn.to/2aB8kQt)
- Optional: [miniHDMI Adapter](http://amzn.to/2aNj5CE)**
- Optional: [USB Hub](http://amzn.to/2aHL4U0)**
- Optional: [>1A microUSB Hub](http://amzn.to/2aHL4U0)**
- Optional: [microUSB -> USB adapter](http://amzn.to/2aNj5CE)**
- Optional: [Headers](http://amzn.to/2aNj5CE)**
- Alternate to Ultrasonic sensors : [Wired Door magnets](http://amzn.to/2aB7AL7)

***I Personally used [this](http://amzn.to/2aHLrOg) but it seems to interfere with my actual garage opener so i recommended a different one**

****You can avoid all the optionals (except the power supply) above by getting a [Raspberry Pi 3](http://amzn.to/2aQlUQm) (or one with decent ports)**



#### <i class="icon-file"></i> Parts (Cheap Version)

- [Raspberry Pi Zero](https://www.adafruit.com/product/2885) Or [Microcenter](http://www.microcenter.com/product/457746/Raspberry_Pi_Zero)
- [2 Ultrasonic Sensors](http://www.ebay.com/sch/i.html?_from=R40&_trksid=p2050601.m570.l1313.TR9.TRC2.A0.H0.Xultrasonic+sensor.TRS1&_nkw=ultrasonic+sensor&_sacat=0)
- [Wifi Dongle](http://www.ebay.com/sch/i.html?_odkw=ultrasonic+sensor&_osacat=0&_from=R40&_trksid=p2045573.m570.l1313.TR12.TRC2.A0.H1.Xraspberry+pi+wifi.TRS0&_nkw=raspberry+pi+wifi&_sacat=0)
- [SD card (4 or 8gb)](http://www.ebay.com/sch/i.html?_odkw=raspberry+pi+wifi&_osacat=0&_from=R40&_trksid=p2045573.m570.l1311.R1.TR9.TRC2.A0.H0.X4gbmicro.TRS0&_nkw=4gb+micro+sd+card&_sacat=0)
- [Simple relay](http://www.ebay.com/sch/i.html?_odkw=arduno+relay&_osacat=0&_from=R40&_trksid=p2045573.m570.l1313.TR0.TRC0.H0.TRS0&_nkw=arduino+relay&_sacat=0)


You'll need a monitor to get things going with the pi. 


Backend
----------
Take a minute to familiarize yourself with the layout of your pi. Gather soldering tools, wires, jumper cables, and all other stuff. [This](http://www.raspberrypi-spy.co.uk/wp-content/uploads/2012/06/Raspberry-Pi-GPIO-Layout-Model-B-Plus-rotated-2700x900.png) will be a handy reference tool for pin layout. 

#### <i class="icon-file"></i> General Overview

The general overview is we have 1 ultrasonic sensor to measure the distance to the car, 1 to measure the distance to the top of the garage, and a relay to open the garage. We measure the distance to the top of the garage because it's more accurate when the distance is not too far away. Pointing the sensor straight towards the garage door will introduce extra errors and inaccuracies. The relay shorts the 2 wires that triggers the garage door. These 2 wires are nearly universal and you should have no problem with this. You could either short the 2 wires coming from the wall switch, or (like i did) connect your own wires to the 'ports' as seen below.

![](https://raw.githubusercontent.com/oooseun/MyGarage/master/Assets/FH13FEB_GADOFX_08.JPG)

Quick Recap. 
Position Ultrasonic sensors to face the top edge of the door and the car (assumes a single car garage) and the relay is to be wired into the garage box. Info on relays [here](http://www.instructables.com/id/Controlling-AC-light-using-Arduino-with-relay-modu/)


#### <i class="icon-file"></i> Raspberry Pi Setup
This is not meant to serve as a setup tutorial (i'll go over the basics) but here are much more detailed tutorials on getting started. I advise you even run some menial programs on your own. [Here's](http://www.instructables.com/id/Ultimate-Raspberry-Pi-Configuration-Guide/) a wonderful instructable on this and [here's](https://www.raspberrypi.org/documentation/) the official setup page

QUICK OVERVIEW
- Install Raspbian unto the SD card
    - Go to the [downloads](https://www.raspberrypi.org/downloads/) page and download the Raspbian Jessie image
    - Follow the instructions to write the image unto an SD card for [Windows](https://www.raspberrypi.org/documentation/installation/installing-images/windows.md), [Mac](https://www.raspberrypi.org/documentation/installation/installing-images/mac.md) or [Linux](https://www.raspberrypi.org/documentation/installation/installing-images/linux.md)
    - Play around with [all](https://www.raspberrypi.org/documentation/usage/) that comes with Raspberry ?
- Go through initial setup.
    - Luckily, most peripherals are plug and play. You might have to change a password here or there but there isn't much setup to do other than writing the image. 
- Install Flask
    - This shall be our Server aplication/library
    - Make sure the internet is working
```sh
pi@raspberrypi ~ $ sudo apt-get install python-pip
pi@raspberrypi ~ $ sudo pip install flask
```
- Connect all the components up
    - There should be 3 components to wire up. The 2 ultrasonic sensors (one for the car and one for the garage)
    - Here's the code (self explanatory) I personally used to setup my sensors. You may change it anytime. Remember to reference this  [chart](http://www.raspberrypi-spy.co.uk/wp-content/uploads/2012/06/Raspberry-Pi-GPIO-Layout-Model-B-Plus-rotated-2700x900.png) for pin numbers. 
```python
        trigDoorPin=24    #Trigger pin for ultrasonic targeting the door. Using BCM Mode on RaspPi
        echoDoorPin=23
        trigCarPin=12
        echoCarPin=26
        GPIO.setmode(GPIO.BCM)      #Needed config. Google 'BCM'
        GPIO.setup(4,GPIO.OUT)      #Setting up IO pins
        GPIO.setup(15,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.output(4,GPIO.LOW)
        GPIO.setup(trigDoorPin,GPIO.OUT)    #Set pin as GPIO out
        GPIO.setup(echoDoorPin,GPIO.IN)     #Set pin as GPIO in
        GPIO.setup(trigCarPin,GPIO.OUT)
        GPIO.setup(echoCarPin,GPIO.IN)    
```
   - Don't forget the relay.
        - i did not define the relay. Rather, since the function for this was simple, i did it inline.
```python
def openClose(): #Basically, turn on the relay for half a second (.01 seconds didn't work). 
    GPIO.output(4,GPIO.HIGH)
    sleep(.5)
    GPIO.output(4,GPIO.LOW)
```
- Test and make adjustments
    - The 2 parts of the [backend code](https://raw.githubusercontent.com/oooseun/MyGarage/master/app.py) you'll need to adjust are the thresholds (line 32) AND the passphrase.
    - Each threshold is unique. You'll have to experiment to see where yours lies. 
    - The passphrase is a security feature to ensure anyone who knows you have open ports in your network can't guess their way into it. A blank passphrase is treated as "". I advise you use this feature even if the passphrase is as short as "a".
    - The passphrase is then converted to md5(). so localhost:6011/togglea is not going to work. Rather localhost:6011/toggle0cc175b9c0f1b6a831c399e269772661
    
   **So after a class in networks, i realised a long url can just be defeated by sniffing. will be aiming to include encryption soon* 
- Final code comments
    - The rest of the code is pretty straight forward and heavily commented. You should take a look at it. 


#### <i class="icon-file"></i> Mounting options
![](https://raw.githubusercontent.com/oooseun/MyGarage/master/Assets/DSC02783.jpg)
![](https://raw.githubusercontent.com/oooseun/MyGarage/master/Assets/DSC02784.jpg)


#### <i class="icon-file"></i> Wrapping Up
If all went well, you should be able to go to theraspberrypisIPaddress:6011/toggle + whatever the md5ofthepassphrase_is and your garage should open. 


This is the ideal case scenario. If all didn't go well, troubleshoot by running individual functions e.g. the openClose() function to determing if the relay works as expected. I'll also advice you have all this setup **BEFORE** you hook it up to the garage. 

#### <i class="icon-file"></i> The WWW
So how would you make it possible to be able to open your garage while **not** connected to you homes network? This is Called Port Forwarding. A feature most routers should have. 

![](https://raw.githubusercontent.com/oooseun/MyGarage/master/Assets/port%20Forwarding.png)


[Google](https://www.google.com/) your router's manufacturer + port fowarding. Each one is different. I have Netgear and i need to go to 192.168.0.1, enter the default admin + password (whic is actually admin & password). Find out the pi's local ip. Go to the advanced section on port fowarding. Then enable the ports i want to foward on the ip address of the item i want to foward. 
The pictures below may be of help

![](https://raw.githubusercontent.com/oooseun/MyGarage/master/Assets/ipaddr.jpg)


![](https://raw.githubusercontent.com/oooseun/MyGarage/master/Assets/adv.jpg)


![](https://raw.githubusercontent.com/oooseun/MyGarage/master/Assets/ports.jpg)


SUCCESS !?
-
if so, [find out your external ip address](http://whatismyipaddress.com/). Go to http://yourip:6011/toggle+yourpersonalpassphrasehash and voila! your garage can open from anywhere in the world. Try this with your phone on LTE and see!

Front End
----------
For android users out there, this is where we part unforunately. I have no Java/android dev experience. If any of you can make an equivalent app for android, that'd be **INCREDIBLE!!** I have a workable solution though. With Flask, you can serve static files, meaning you could make your links into a web app like [this guy's](http://www.driscocity.com/idiots-guide-to-a-raspberry-pi-garage-door-opener/) solution

![](http://www.driscocity.com/wp-content/uploads/2014/05/dooropener.jpg)




#MyGarage
This is a native ios app i built to work with this system and similar systems with a little adaptation. If you followed everything above, this should be plug and play. [Here is a video](https://www.youtube.com/watch?v=1Qu-76sq3Ak) of the initial setup. I think it's absolutely gorgeous. You can make your own judgements. 


![](https://raw.githubusercontent.com/oooseun/MyGarage/master/Assets/AppScreenshotCollageSmall.jpg)



[![](https://raw.githubusercontent.com/oooseun/MyGarage/f5ef525425ac1b84a45d0d11520a42462e8430e5/Assets/Download_on_the_App_Store_Badge.jpg)](https://itunes.apple.com/WebObjects/MZStore.woa/wa/viewSoftware?id=1140600357&mt=8)

To download this app, visit the App Store


#### <i class="icon-file"></i> Official Description

    This is an app for DIYers like myself who love to tinker with stuff. This app particularly lets you control your garage with a native iPhone app.
    
    
     It includes many features and benefits like 
    - Touch id for authentication/security
    - Geofencing for closing/open the door on exit/entrance
    - Allow access to close friends and family
    - Setup is easy with the right backend solution
    - Visual representation of garage door activity
    - Very secure
    - Ability to see if system is offline 
    
    Best of all, IT'S FREE!!
    
    
    
    Backend needs as little as a toggle switch and an Open/Closed state to work. Please refer to http://github.com/oooseun/MyGarage for setup instructions. 
    
    The app is completely detached from any servers other than the ones you yourself so your data isn't being beamed off to some remote location.

### Table of contents

[TOC]



