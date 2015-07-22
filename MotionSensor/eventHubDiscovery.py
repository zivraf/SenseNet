import sys, optparse, time, platform, urllib, socket, ConfigParser
from proton import *


Config = ConfigParser.ConfigParser()
Config.read("appconfig.ini")
location = Config.get(platform.node(),'Location')


ehNamespace = Config.get("eventhub", "ehNamespace")
ehEntity = Config.get("eventhub","ehEntity")
ehUsername = Config.get("eventhub","ehUsername")
ehPassword = urllib.quote_plus (Config.get("eventhub","ehPassword"))

AMQP_CONN_STR = "amqps://"+ehUsername+":"+ehPassword+"@"+ehNamespace+".servicebus.windows.net/"+ehEntity

s = socket.socket()
s.connect(("microsoft.com", 80))
publicIp = s.getsockname()


mng = Messenger()
mng.start()

msg = Message()
msg.address = AMQP_CONN_STR
msg.properties = {}
msg.properties[u"Timestamp"] = unicode (time.strftime("%H:%M:%S"))
msg.properties[u"Hostname"] = unicode (platform.node())
msg.properties[u"Status"] = unicode ("Device Initialized")
msg.properties[u"IP"] = unicode (publicIp)

msg.annotations = {}
msg.annotations[symbol("x-opt-partition-key")]=unicode (platform.node())

msg.body = "Device Initialized"
mng.put(msg)
mng.send()


mng.stop()

