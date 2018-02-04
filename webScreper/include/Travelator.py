from bs4 import BeautifulSoup
from Results import Results
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
		self.pb = PushbulletApi()
		self.res = Results()
		self.run()
		
	def run(self):
		
		self.loadTitles ()
		self.printResult()
		

	def printResult(self):
		print "Is this funtion called?\n"
		
		for (title, country, link) in  self.titles:
			if country != "":
				print "Found new item! Adding it to db ...\n"
				isNewEntry = self.res.insertItem( SITE_NAME, [title, country, link] )
				if isNewEntry:
					vacation = "Found new vacation in '%s'\n Link: %s" %  (country, link)
					self.pb.pushSomething( SITE_NAME, vacation )
					
					

	def loadTitles (self):

		url = "http://www.travelator.ro"
 
		while url != "":

			print "Attempting to open the following url: '%s' \n\n" % ( url )
			
			# Add your headers
			headers = {'User-Agent' : 'Mozilla 5.10'}

			# Create the Request. 
			request = urllib2.Request(url, None, headers)

			content = urllib2.urlopen( request ).read()
			soup = BeautifulSoup(content, 'lxml')
			url = ""
			print "Finding first page ... \n\n"
			frames = soup.div.find_all('h3', {"class" : "post-title"})
 
			for link in frames:
				self.titles.append ( [ link.text, self.findCountryEurope( link.text ), link.a['href'] ] )
 
			def dontcare():
				lastPage = soup.find_all ("div", { "class": "pager rel clr"})
				#print lastPage
				linkNextPage = ""
	
				for link in lastPage:
					linkNextPage = link.find ( "span", { "class" : "fbold next abs large"})
					print linkNextPage
					try:
						if linkNextPage.a:
							url = linkNextPage.a['href']
						else:
							url = ""
					except ValueError:
						print "Error in link next page\n\n %s \n" % ( linkNextPage ) 
						print ValueError
			
			print "Done extracting ..."
	
	def findCountryEurope (self, title):
		tmp = ""
		for country in self.configFile:

			for airportCityName in self.configFile[country]:
				pattern= airportCityName[0].encode("utf-8",'ignore')
				pattern = string.replace( pattern, " Island", "")
				
				if re.search ( pattern, title,  re.IGNORECASE):
					tmp += country + "/" + pattern + "; " 
		return tmp

			#print str ( linkNextPage )
class TravelatorItem:
	def __init__(self):
		self.type = "Travelator"
		self.contents = []
		