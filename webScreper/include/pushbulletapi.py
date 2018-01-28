import os.path
import re
import json
from pushbullet import Pushbullet

class PushbulletApi:
    
    def __init__(self):
        self.configFile = json.load(open(os.path.join (os.environ['OneDrive'], "PythonData", "config", "pushbullet.json")))
	self.pb = Pushbullet(self.configFile['apiValue'])
	self.samsung = self.pb.get_device('Samsung SM-G935F')
    def pushSomething(self, sitename, message):
	push = self.pb.push_note( sitename, message, device=self.samsung )

pb = PushbulletApi()
pb.pushSomething( "Travelator","New vacation in Caraibe!")
