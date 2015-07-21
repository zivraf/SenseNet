# SenseNet is a simple motion sensor. Using Raspberry PI and a motion sensor, we sense events (motion on\off) and send them to Azure.
# SenseNet uses Azure Service Bus (EventHub) as a cloud gateway. We can plug in multiple processing streams.
# This sample uses a simple loop and periodically read the sensor's state detecting state chenge and then send them ot the cloud
# DO NOT USE - a better version of this samples which uses interrupts is kept under the name of motionSensor

import RPi.GPIO as GPIO
import sys, optparse, time, platform, urllib, socket, ConfigParser, datetime

from proton import *
 
PIR = 4

pirState = False                        # we start, assuming no motion detected
pirVal = False                          # we start, assuming no motion detected
 
Config = ConfigParser.ConfigParser()
Config.read("appconfig.ini")
location = Config.get(platform.node(),'Location')


ehNamespace = Config.get("eventhub", "sensnet-ns")
ehEntity = Config.get("eventhub","motiontracker")
ehUsername = Config.get("eventhub","sender")
ehPassword = urllib.quote_plus (Config.get("eventhub","ehPassword"))

AMQP_CONN_STR = "amqps://"+ehUsername+":"+ehPassword+"@"+ehNamespace+".servicebus.windows.net/"+ehEntity

print ("Read config file. Location is "+location)

mng = Messenger()
mng.start()


GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR, GPIO.IN)


while True:
    pirVal = GPIO.input(PIR)            # read input value
    if (pirVal == True):                # check if the input is HIGH
        if (pirState == False):
            # we have _just_ turned on
            pirState = True
            print time.strftime("%H:%M:%S") + " - Motion ON"
            msgOn = Message()
            msgOn.address = AMQP_CONN_STR
            msgOn.properties = {}
            msgOn.properties[u"Hostname"] = unicode (platform.node())
            msgOn.properties[u"Motion"] = unicode ("On")
            msgOn.properties[u"Location"] = unicode (location)
            msgOn.properties[u"Timestamp"] = unicode ( datetime.datetime.now().isoformat())
            msgOn.annotations = {}
            msgOn.annotations[symbol("x-opt-partition-key")]=unicode (platform.node())
            mng.put(msgOn)
            mng.send()
            time.sleep (5)
    else:
        if (pirState == True):
            # we have _just_ turned off
            pirState = False;
            print time.strftime("%H:%M:%S") + " - Motion OFF"
            msgOff = Message()
            msgOff.address = AMQP_CONN_STR
            msgOff.properties = {}
            msgOff.properties[u"Hostname"] = unicode (platform.node())
            msgOff.properties[u"Motion"] = unicode ("Off")
            msgOff.properties[u"Location"] = unicode (location)
            msgOn.properties[u"Timestamp"] = unicode (time.strftime("%ctime "))
            msgOff.annotations = {}
            msgOff.annotations[symbol("x-opt-partition-key")]=unicode (platform.node())
            mng.put(msgOff)
            mng.send()
            time.sleep (2)
   
mng.stop()



    





