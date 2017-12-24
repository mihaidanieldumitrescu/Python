from bs4 import BeautifulSoup
import urllib2
import json

class iaBilet( object ):

	def __init__(self):
		self.events = []
		self.loadPage()

	def __str__(self):
		tmp = "Printing list of extracted objects: \n\n"
		for eventName in sorted ( self.events ):
			tmp += "Found '%s' with '%s' \n" % ( streamerName.ljust(20), self.events[eventName])		
		return tmp		

	def loadPage(self):
		url = "http://www.iabilet.ro/bilete/2017/12"
		content = urllib2.urlopen(url).read()
		soup = BeautifulSoup(content,"lxml")
		eventList = soup.find_all("div", { "class": "event-list" })
		for event in eventList:

			frames = event.find_all("script")
		
			for frame in frames:
				separateJson = ( frame.string.split("\n"))[2]
				data = json.loads( separateJson )
				print  "%s - %s - %s" %(data['location']['address']['addressLocality'].encode('ascii','ignore'), data['startDate'].encode('ascii','ignore'), data['name'].encode('ascii','ignore'))
				#self.events.append ( data ['name'])
		if len (self.events) == 0:
			print "Error: Cannot extract anything from page!\n"
	
	def isStreamerOnline(self,eventName):
		for event in self.events:	
			if event == eventName:
				return 1
		return 0
