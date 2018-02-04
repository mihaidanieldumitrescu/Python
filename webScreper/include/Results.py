import json
import os
import re
from pushbulletapi import PushbulletApi

class resultObject:
    
    def __init__(self, sitename, description, link):
        self.title = title
        self.sitename= sitename
        self.link = link

class Results:
    def __init__(self):
        self.jsonFileOutput = os.path.join ( os.environ['OneDrive'], "PythonData", "config", "results.json" )
        self.data = json.load( open ( self.jsonFileOutput) )
        self.pb = PushbulletApi()
        self.jsonModified = 1 
        
    def __del__(self):
        print "Writing output to json file"
        self.writeJson()

    def insertItem(self, siteName, item):
        if not siteName in self.data:
            self.data.update ({ siteName : []})
            
        for site in self.data:
            if re.match ( site, siteName, re.IGNORECASE):
                if item in self.data[site]:
                    print "Item not added as it was already there"
                    return 0
                else:
                    print "Adding new item to '%s' \-n\n %s" % ( siteName, item )
                    self.data[site].append(item)
                    return 1
        return 0

    def writeJson(self):
        if self.jsonModified:
            with open (self.jsonFileOutput,"w") as f:
                f.write ( json.dumps( self.data, indent=4 ) ) 