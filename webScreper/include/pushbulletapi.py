import os.path
import re
import json
from pushbullet import Pushbullet

class PushbulletApi:
    
    def __init__(self):
        self.configFile = json.load(open(os.path.join ( os.environ['OneDrive'], "PythonData", "config", "pushbullet.json")) )
        self.pb = Pushbullet( self.configFile['apiValue'] )
        self.myDevice = self.pb.get_device( self.configFile['deviceName'] )
        
    def pushSomething(self, item):
    	push = self.pb.push_note( item.siteName, item.description, device=self.myDevice )

    def testApi(self):
        pb = PushbulletApi()
        pb.pushSomething( "Travelator", "New vacation in Caraibe!")
