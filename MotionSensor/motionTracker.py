# SenseNet is a simple motion sensor. Using Raspberry PI and a motion sensor, we sense events (motion on\off) and send them to Azure.
# SenseNet uses Azure Service Bus (EventHub) as a cloud gateway. We can plug in multiple processing streams.
# This sample uses AMQP 1.0 with the apache-proton library and was tested using proton 0.9.2
# This sample uses registeers for for interrupts sent from the sensor and only then sends messages to the cluod

import RPi.GPIO as GPIO
import sys, optparse, time, platform, urllib, socket, ConfigParser, datetime, threading

from proton import *
 
PIR = 4

pirState = False                        # we start, assuming no motion detected
pirVal = False                          # we start, assuming no motion detected
 
Config = ConfigParser.ConfigParser()
Config.read("appconfig.ini")
location = Config.get(platform.node(),'Location')


ehNamespace = Config.get("eventhub", "ehNamespace")
ehEntity = Config.get("eventhub","ehEntity")
ehUsername = Config.get("eventhub","ehUsername")
ehPassword = urllib.quote_plus (Config.get("eventhub","ehPassword"))

AMQP_CONN_STR = "amqps://"+ehUsername+":"+ehPassword+"@"+ehNamespace+".servicebus.windows.net/"+ehEntity

print ("Read config file. Location is "+location)

mng = Messenger()
mng.start()


GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR, GPIO.IN)

def send_message (value):
    # Initialized message properties. We decided to use message properties rather than body in order to enable the reciever side to pick whatever attributes regardless of the message format.
    msgOn = Message()
    msgOn.address = AMQP_CONN_STR
    msgOn.properties = {}
    msgOn.properties[u"Hostname"] = unicode (platform.node())
    msgOn.properties[u"Motion"] = unicode (value)
    msgOn.properties[u"Location"] = unicode (location)
    msgOn.properties[u"Time"] = unicode (datetime.datetime.now())
    # Message annotations are used for protocol properties
    msgOn.annotations = {}
    # Setting partition key enables us to process messages sent from a devices in order as we use the hostname as the key.
    msgOn.annotations[symbol("x-opt-partition-key")]=unicode (platform.node())
    mng.put(msgOn)
    mng.send()

# Callback function to be called with the sensor's state
def motion_detect (PIR):
    pirVal = GPIO.input(PIR)            # read input value
    global pirState
    if (pirVal == True):  
        print time.strftime("%H:%M:%S") + " - Motion ON"
        if (pirVal != pirState):
            pirState = pirVal         
            send_message ("True")
        else:
            print time.strftime("%H:%M:%S") + " - duplicate event. dropped"
    else:
        print time.strftime("%H:%M:%S") + " - Motion OFF"
        if (pirVal != pirState):
            pirState = pirVal         
            send_message ("False")
        else:
            print time.strftime("%H:%M:%S") + " - duplicate event. dropped"
try:
    GPIO.add_event_detect(PIR, GPIO.BOTH, callback=motion_detect, bouncetime=2000)    
    while 1:
        time.sleep(100)

except KeyboardInterrupt:
    print ("Quit")
    GPIO.cleanup()
    mng.stop()

       





