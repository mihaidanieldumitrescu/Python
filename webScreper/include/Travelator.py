from bs4 import BeautifulSoup
from include.Results import Results, ResultObject
from pushbullet import Pushbullet

import urllib3
import json
import re
import os,string

SITE_NAME = "Travelator"
class Travelator:

	def __init__(self):
		self.configFile = json.load(open( os.path.join (os.environ['OneDrive'], "PythonData", "config", "EuropeAirports.json")) )
		self.titles = []
		self.pb  = PushbulletApi()
		self.res = Results()
		self.debug = 1
		self.debugFlags = { "loadTitles": 0 ,"callPushbullet" : 1, "addToJson" : 0 }

	def run(self):
		
		self.printResult()
		
	def filter(self):
		filterDict = {}
		vacations = self.loadTitles()
		with open( os.path.join (os.environ['OneDrive'], "PythonData", "config", "globalSearch.json")) as jsonFile:
			filterDict = json.load( jsonFile )
			
		if filterDict['Travelator']:
			for keyword in  filterDict['Travelator']['keywords']:
				print (f"Looking for {keyword}  ...\n")
				for country, title, link in vacations:
					print (f"Current country: '{country}'")
					if keyword in country:
						if filterDict['Travelator']['notification'] == 'on':
							description = "Jackpot! Vacation in '%s' found!\n\n  Link: %s" %  ( country, link )
							travObj = TravelatorObject( description, link )
							self.pb.pushSomething( travObj )	
			
	def printResult(self):
	
		for ( country,title, link) in self.loadTitles():
			if country != "":
				if self.debug:
					print ("Found '{country}'! sending it to db ...\n")
				isNewEntry = self.res.insertItem( SITE_NAME, [ country, title, link ] )
				if isNewEntry:

					description = f"Found new vacation in '{country}'!\n\n Link: {link}"
					item = TravelatorObject( description, link )
					print (item)
					if not self.debug or self.debugFlags['callPushbullet']:
						self.pb.pushSomething( item )
						
	def loadTitles (self):

		url = "http://www.travelator.ro"
		if url != "":

			print (f"Attempting to open the following url: '{url}' \n\n")
			
			headers = {'User-Agent' : 'Mozilla 5.10'}
			request = urllib3.Request(url, None, headers)

			content = urllib3.urlopen( request ).read()
			soup = BeautifulSoup(content, 'lxml')
	
			print ("Finding first page ... \n\n")
			frames = soup.div.find_all('h3', {"class" : "post-title"})

			for link in frames:
				encodedTitle = link.text.encode("utf-8",'ignore')
				yield [ self.findCountryEurope( encodedTitle ), encodedTitle, link.a['href'] ]
	
	def findCountryEurope (self, title):
		tmp = ""
		for country in self.configFile:

			for airportCityName in self.configFile[country]:
				pattern= airportCityName[0].encode("utf-8",'ignore')
				pattern = string.replace( pattern, " Island", "")
				
				if re.search ( pattern, title,  re.IGNORECASE):
					tmp += country + "/" + pattern + "; " 
		return tmp

class TravelatorObject (ResultObject):
	def __init__(self, description, link):
		ResultObject.__init__(self, description, link )
		self.siteName = "Travelator"
		
	def __str__(self):
		return "Sitename: '%s' \nDesc: %s \nLink: %s \n" % (self.siteName, self.description, self.link)
		