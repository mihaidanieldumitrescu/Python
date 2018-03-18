from bs4 import BeautifulSoup
import pprint
import urllib2
import json
import os

class Olx(object):
	def __init__(self, searchStr, limit=3):
		self.products = []
		self.limitPages = limit
		self.pagesIndex = 1
		# [ {}, {}, {}]
		
		#self.loadDebug()

	
	def loadDebug(self):
		with open ("olxCarsResults.json","r") as f:
			self.products = json.load ( f )
			
		for product in self.products:
			print "{} {}".format ( product[0].ljust(20), str( product[1]).rjust(5))
		
		
	def loadProducts ( self ):
		
		#sortByDesc = "?search%5Border%5D=filter_float_price%3Adesc"
		#url = sortByDesc
		url = "https://www.olx.ro/auto-masini-moto-ambarcatiuni/autoturisme/?search%5Bfilter_float_price%3Afrom%5D=600&search%5Bfilter_float_price%3Ato%5D=1400"
		#url = "https://www.olx.ro/oferte/q-asus-transformer/"
		while url != "":

			print "Attempting to open the following url: '%s' \n\n" % ( url )

			# Add your headers
			headers = {'User-Agent' : 'Mozilla 5.10'}

			# Create the Request.
			request = urllib2.Request(url, None, headers)

			content = urllib2.urlopen( request ).read()
			soup = BeautifulSoup(content, 'lxml')
			url = ""
			
			frames = soup.div.find_all('tr', {"class" : "wrap"})
			if len ( frames ) == 0:
				print "Error: Either link is wrong or something changed in page structure!\n\n"
				print soup
			for link in frames:
			    productTitle = link.strong.string 
			    productPrice = ""
			    priceArr = ( link.find_all( 'p', { "class" : "price"}))
			    if len ( priceArr):
			        productPrice = priceArr[0].strong.string
			    else:
			        productPrice = -1
			    self.products.append( [ productTitle, productPrice ] )

			lastPage = soup.find_all ("div", { "class": "pager rel clr"})
			#print lastPage
			linkNextPage = ""

			for link in lastPage:

				if self.limitPages == 0:
					break

				linkNextPage = link.find ( "span", { "class" : "fbold next abs large"})
				 
				try:
					if linkNextPage.a:
						url = linkNextPage.a['href']
						self.pagesIndex += 1
					else:
						url = ""
				except ValueError:
					print "Error in link next page\n\n %s \n" % ( linkNextPage )
					print ValueError
				self.limitPages -= 1
			print "Done extracting ...\n\n Found a number of {} pages and a total of {} items ".format(self.pagesIndex,len(self.products))
			
	def getNextPage(self, lastPage):
		pass
	

	def printResults(self):
		
		for product in self.products:
			print "%s %s" % ( product['price'].ljust(10), product['desc'] )

			#print str ( linkNextPage )

			
class OlxCars( Olx ):
	
	def __init__(self):
		searchlink = "https://www.olx.ro/auto-masini-moto-ambarcatiuni/autoturisme/?search%5Bfilter_float_price%3Afrom%5D=600&search%5Bfilter_float_price%3Ato%5D=1400"
		Olx.__init__( self, searchlink, 3 )
		self.pp = pprint.PrettyPrinter( indent=4)
		self.statistics = {}
		self.loadProducts()
		self.filterWordsCarsModels = json.load( open( os.path.join (os.environ['OneDrive'], "PythonData", "config", "olx_cars.json")))
		self.sortByModel()
		self.writeResults()
		
	def sortByModel(self):
		# filterWords = {"opel": ['vectra', 'astra'], 'peugeot': '206' }
		sortedList = []
		otherCars = []
		for carBuilder in self.filterWordsCarsModels[0]:
			for carModel in self.filterWordsCarsModels[0][carBuilder]:
				print "Looking for {} ...".format ( carModel )
				self.statistics[carModel] = { "occurences" : 0, "prices" : [] }
				for productDesc in self.products:
					if carModel in productDesc[0].lower():
						sortedList.append ( [ self.filterDesc( productDesc[0]), productDesc[1]])
						self.statistics[carModel]['prices'].append ( productDesc[1] )
						self.statistics[carModel]['occurences'] += 1
					else:
						otherCars.append ( [ self.filterDesc( productDesc[0]), productDesc[1]])
		sortedList.append (otherCars)
		self.pp.pprint( sortedList )
		self.pp.pprint (self.statistics)
	
	def writeResults(self):
		with open ("olxCarsResults.json", "w") as f:
			f.write ( json.dumps(self.products,sort_keys=True, indent=4 ) )
		with open ("olxCarStatistics.json", "w") as f:
			f.write ( json.dumps(self.statistics,sort_keys=True, indent=4 ) )
			
	def filterDesc(self, description):
		filterWords = [ 'vind', 'vand', 'cumpar', 'schimb', 'masina' , 'cu' , 'oferta', 'pret', 'sau' ]
		finalString = ""
		for word in description.lower().split(' '):
			if not word.lower() in filterWords:
				finalString += word + " "
		return finalString