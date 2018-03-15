from bs4 import BeautifulSoup
from Results import Results, ResultObject
from pushbulletapi import PushbulletApi

import urllib2
import json
import re
import os,string

SITE_NAME = "Traveletor"
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
				print "Looking for {}  ...\n". format( keyword )
				for ( country, title, link) in vacations:
					print "Current country: '{}' ".format (country)
					if keyword in country:
						if filterDict['Travelator']['notification'] == 'on':
							description = "Jackpot! Vacation in '%s' found!\n\n  Link: %s" %  ( country, link )
							travObj = TravelatorObject( description, link )
							self.pb.pushSomething( travObj )	
			
	def printResult(self):
	
		for ( country,title, link) in self.loadTitles():
			if country != "":
				if self.debug:
					print "Found '{}'! sending it to db ...\n".format (country)
				isNewEntry = self.res.insertItem( SITE_NAME, [ country, title, link ] )
				if isNewEntry:

					description = "Found new vacation in '%s'!\n\n Link: %s" %  ( country, link )
					item = TravelatorObject( description, link )
					print item
					if (  not self.debug or self.debugFlags['callPushbullet'] ):
						self.pb.pushSomething( item )
						
	def loadTitles (self):

		url = "http://www.travelator.ro"
		if url != "":

			print "Attempting to open the following url: '%s' \n\n" % ( url )
			
			headers = {'User-Agent' : 'Mozilla 5.10'}
			request = urllib2.Request(url, None, headers)

			content = urllib2.urlopen( request ).read()
			soup = BeautifulSoup(content, 'lxml')
	
			print "Finding first page ... \n\n"
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
		