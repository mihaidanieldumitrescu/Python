from bs4 import BeautifulSoup
from datetime import datetime,timedelta
from Results import Results, ResultObject

import sys
import os
import urllib2
import json

import re

class iaBilet:

	def __init__(self):
		self.events = []
		self.matches = []
		self.config = {}
		self.loadConfig()
		self.loadPage()
		#print self.generateDates()
		
	def __del__(self):
		if len ( self.matches ) > 0:
			print "\nmatches found\n\n"
			print "\n".join( self.matches )
			
			print "\n"
		#print "\n".join( self.generateDates() )
	def __str__(self):
		tmp = "Printing list of extracted objects: \n\n"
		for eventName in sorted ( self.events ):
			tmp += "Found '%s' with '%s' \n" % ( eventName.ljust(20), self.events[eventName])		
		return tmp		

	def loadPage(self):
		dates = self.generateDates()
		
		for ( year, month ) in dates:
			parameter = "%s/%s" % ( year, month )
			url = "http://www.iabilet.ro/bilete/" + parameter
			print url

			content = urllib2.urlopen(url).read()
			soup = BeautifulSoup(content,"lxml")
			eventList = soup.find_all("div", { "class": "event-list" })
			for event in eventList:

				frames = event.find_all("script")
			
				for frame in frames:
					separateJson = ( frame.string.split("\n"))[2]
					data = json.loads( separateJson )
					(cityName, eventDate, eventName ) = ( data['location']['address']['addressLocality'].encode('utf-8','ignore'), data['startDate'].encode('utf-8','ignore'), data['name'].encode('utf-8','ignore') )
					print  "%s %s %s" % (cityName.ljust(10), eventDate.ljust(8), eventName)
					self.events.append ( { "cityName" :  cityName, "eventDate" : eventDate, "eventName" : eventName  } )
					for showType in self.config:
						for showName in self.config[showType]:
							if re.search (showName, eventName.lower()):
								self.matches.append( "%s %s %s" % (cityName.ljust(10), eventDate.ljust(8), eventName) )
		#print "Matches found: \n\n" + str( self.matches ) ;
		if len (self.events) == 0:
			print "Error: Cannot extract anything from page!\n"
			
	def loadConfig (self):
		with open ( os.path.join ( os.environ['OneDrive'], "PythonData", "config", "webScraper.json") ) as f:
			self.config = json.load( f )
	
	def isEventFound(self, eventName):
		for event in self.events:	
			if event == eventName:
				return 1
		return 0
	
	def generateDates(self):
		dates = []
		dateDict = {}
		dateToday = datetime.now()
		daysForward= 60

		unsorted = []
		for monthVal in range (0, daysForward):
			#dates.append ( str (datetime.now() + timedelta(days=monthVal)))
			extractedGroup = re.search ( "(\d{4}).(\d{2}).\d{2}" , str ( datetime.now() + timedelta(days=monthVal) ) )
			year = extractedGroup.group(1)
			month = extractedGroup.group(2)
			unsorted.append ( [ int( year ), int ( month ) ] )
			
		for pair in unsorted:
			if not ( pair in dates):
				dates.append ( pair )
				

		return dates

class IaBiletObject (ResultObject):
	def __init__(self, description, link):
		ResultObject.__init__(self, description, link )
		self.siteName = "Travelator"