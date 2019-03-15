import json
import os
import re
from pushbullet import Pushbullet

class ResultObject:
    def __init__(self, description, link):
        self.description = description
        self.link = link
        
    def __str__(self):
        return  "%s %s" % ( self.description, self.link )

class Results:
    def __init__(self):
        self.data = self.readData()
        self.pb = PushbulletApi()
        self.writeJsonFlag = 0
        self.debug = 1
        
    def __del__(self):
        self.writeJson()
        
    def readData(self):
        data = None
        jsonPath = os.path.join ( os.environ['OneDrive'], "PythonData", "config", "results.json" )
        with  ( open ( jsonPath ) ) as jsonFile:
            data = json.load( jsonFile )
        return data
        
    def insertItem(self, siteName, item):
        if not siteName in self.data:
            self.data.update ({ siteName : []})
            
        for site in self.data:
            if re.match ( site, siteName, re.IGNORECASE):
                if item in self.data[site]:
                    if self.debug:
                        print ("Item not added as it was already there")
                    return 0
                else:
                    #todo: call pushbullet function
                    #self.pb.pushSomething ( siteName, message, link )

                    if self.debug:
                        print ("Adding new item to '{siteName}' \n\n {item}")

                    self.data[site].append(item)
                    #self.pb.pushSomething ( item )
                    self.writeJsonFlag = 1
                    return 1
        return 0

    def writeJson(self):

        jsonPath = os.path.join ( os.environ['OneDrive'], "PythonData", "config", "results.json" )
        if self.writeJsonFlag:
            print ("Writing output to json file ...\n")
            with open ( jsonPath,"w") as f:
                f.write ( json.dumps( self.data, indent=4 ) ) 