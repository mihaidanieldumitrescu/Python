from bs4 import BeautifulSoup
from codecs import open
import pprint
import urllib2
import json
import os,re

class OlxProduct:
	def __init__(self, link="https://www.olx.ro/oferta/masina-renault-megane-IDbEIBo.html" ):
		self.title = ""
		self.link = link.split("#")[0] if len ( link.split("#") ) else link
		self.price = 0
		self.details = {}
		self.description = []
		self.images = []
		self.pageCounter = 0
		
		print "(OlxProduct contructor) Link is {}\n".format (self.link)

	def __repr__(self):
		detailsPretty = {}
		for key in self.details:
			detailsPretty[key.ljust(16)] = self.details[key]
		
		return (
					( "Title:".ljust (15) + " {}\n" +
					"Link:".ljust (15) + " {}\n" +
					"Description:".ljust (15) +" {}\n"+
					"Page count:".ljust (15)  + " {}\n\n"+

					"Details:".ljust (15)  +"\n{}\n\n"+
					"Images:".ljust (15)  + "\n{}\n"+
					"\n").format ( pprint.pformat( self.title, indent=4), pprint.pformat( self.link, indent=4), pprint.pformat( self.description, indent=4), pprint.pformat(self.pageCounter, indent=4),
								   pprint.pformat( detailsPretty, indent=4), pprint.pformat( self.images, indent=4)  ) )
			
	def loadPage (self):
		
		if re.search ( r'https?://www.olx.ro/oferta' ,self.link ):
			headers = {'User-Agent' : 'Mozilla 5.10'}
			
			# Create the Request.
			request = urllib2.Request( self.link, None, headers)
	
			content = urllib2.urlopen( request ).read()
			soup = BeautifulSoup(content, 'lxml')
			
			# self.title
			if soup.find ( "div", { "class": "offer-titlebox"}):
				self.title = soup.find ( "div", { "class": "offer-titlebox"}).h1.text.strip()
			else:
				self.title = "n/a" 
			# self.price
			if soup.find( "div", { "class" : "price-label" } ):
				self.price = soup.find( "div", { "class" : "price-label" } ).strong.text
			elif soup.find( "div", { "class" : "pricelabel" } ):
				self.price  = soup.find( "div", { "class" : "pricelabel" } ).strong.text
			else:
				self.price = "n/a"
			# self.description
			self.description = soup.find ( "div", { "id": "textContent"}).text.strip()
	
			# self.images
			for div in soup.findAll ( "div", { "class": "photo-glow"}):
				if type ( div.img ) != type ( None ):
					self.images.append ( div.img['src'] )

			# self.details
			for table in soup.findAll ( "table", { "class": "item"}):
				if table.find ( 'a' ):
					self.details[table.th.string] = table.strong.a.text.strip()
				else:
					if type ( table.strong ) != type ( None ):
						self.details[table.th.string] = table.strong.text.strip()
	
			# self.pageCounter
			if soup.find ( "div", { "id": "offerbottombar"}):
				self.pageCounter = soup.find ( "div", { "id": "offerbottombar"}).strong.text
			else:
				self.pageCounter = "n/a"
				
		else:
			print "(OlxProduct) Error: Not an olx link!\n"
			
	def toHtmldiv (self):
		if re.search ( r'https?://www.olx.ro/oferta' ,self.link ):
			div = [ u"<div class='olx-product'>\n" ]
			title = u"<h3><a href='" + self.link + u"' >" + self.price + u" - " + self.title + u"</a></h3>\n\n";
			# paragraph e singurul care foloseste metoda text in loc de string "Adus\xc4\x83 din Germania" -> "Adus\u0103 din Germania"
			description = u"<p>" + self.description + u"</p>\n" 
			details =     u"<p>An de fabricatie: {} - Rulaj: {} - Capacitate: {}".format ( self.details['An de fabricatie'] if self.details.has_key('An de fabricatie') else u"N/A",
																						   self.details['Rulaj'] if self.details.has_key('Rulaj') else u"N/A",
																						   self.details['Capacitate motor'] if self.details.has_key('Capacitate motor') else u"N/A" ) 
			images = ( u"<div class='image-gallery'>\n" +
					   u"\n".join ( [ u"<img src ='"+ x +"' height='300' ></img>" for x in self.images ] ) +
					   u"</div>" )
			
			div.append ( title )
			div.append ( details )
			div.append ( description )
	
			div.append ( images )
			div.append ( u"</div>")
			return u"\n".join ( div )
		else:
			return u"<p>-Page empty-\n\n"
	
class Olx(object):
	def __init__(self, searchStr, limit=1):
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
		fail = 0
		pages = 0
		url = "https://www.olx.ro/auto-masini-moto-ambarcatiuni/autoturisme/?search%5Bfilter_float_price%3Afrom%5D=2000&search%5Bfilter_float_price%3Ato%5D=7000"
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
			
			frames = soup.find_all('tr', {"class" : "wrap"})
			if len ( frames ) == 0:
				fail = 1
				with open ("dump_{}.html".format(pages), "w") as f:
					f.write (str(soup))
				pages += 1
			
			for link in frames:
				productLink = link.a['href'].split("#")[0] if len ( link.a['href'].split("#") ) else link.a['href']
				productTitle = link.strong.string 
				productPrice = ""
				priceArr = ( link.find_all( 'p', { "class" : "price"}))
				
				if re.search (r'www.autovit.ro', productLink):
					print "Skipping autovit link {} \n".format (productLink) 
					next
					
				if len ( priceArr):
					productPrice = int ( priceArr[0].strong.string.encode('utf-8').replace(' \xe2\x82\xae','').replace(' \xe2\x82\xac','').replace(' ' ,'') )

				else:
					productPrice = -1
				self.products.append( [ productTitle, productPrice, productLink ] )

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
		if fail:
			print "Error: Either link is wrong or something changed in page structure!\n\n"
			
	def getNextPage(self, lastPage):
		pass
	

	def printResults(self):
		
		for product in self.products:
			print "%s %s" % ( product['price'].ljust(10), product['desc'] )

			#print str ( linkNextPage )

			
class OlxCars( Olx ):
	
	def __init__(self):
		searchlink = "https://www.olx.ro/auto-masini-moto-ambarcatiuni/autoturisme/?search%5Bfilter_float_price%3Afrom%5D=600&search%5Bfilter_float_price%3Ato%5D=1400"
		Olx.__init__( self, searchlink, 1 )
		self.pp = pprint.PrettyPrinter( indent=4)
		self.statistics = { "otherCars" : { "prices": [], "occurences": 0} }
		self.productDetailsArr = [] 
		self.loadProducts()
		self.filterWordsCarsModels = json.load( open( os.path.join (os.environ['OneDrive'], "PythonData", "config", "olx_cars.json")))
		self.sortByModel()
		self.readProductDetails()
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
						self.statistics[carModel]['prices'].append ( productDesc[1]  )
						self.statistics[carModel]['prices'] = sorted ( self.statistics[carModel]['prices'] )
						self.statistics[carModel]['occurences'] += 1
					else:
						otherCars.append ( [ self.filterDesc( productDesc[0]), productDesc[1]])
						self.statistics['otherCars'].update ( {self.filterDesc( productDesc[0]) : productDesc[1] }  )
						self.statistics['otherCars']['occurences'] += 1
				tmpSum = 0
				for price in self.statistics[carModel]['prices']:
					tmpSum += int(  price  )
				if len ( self.statistics[carModel]['prices'] ) :
					self.statistics[carModel]['average'] = tmpSum / len ( self.statistics[carModel]['prices'] )
		sortedList.append (otherCars)
		#self.pp.pprint( sortedList )
		#self.pp.pprint (self.statistics)
		
	def readProductDetails (self):
		for productArr in self.products:
			if productArr[2]:
				obj = OlxProduct( productArr[2] )
				obj.loadPage()
				self.productDetailsArr.append ( obj )
			
	def writeResults(self):
		with open ("olxCarsResults.json", "w") as f:
			f.write ( json.dumps(self.products, sort_keys=True, indent=4 ) )
		with open ("olxCarStatistics.json", "w") as f:
			f.write ( json.dumps(self.statistics, sort_keys=True, indent=4 ) )
		with open ("reportCars.html", "w", encoding='utf-8') as f:
			f.write ( "<html>") 
			f.write ( "<head>\n\t<meta charset='UTF-8'> \n\t <title>Olx-Cars Report</title>\n</head>\n<body>\n\n") 
			f.write ( "\n\n".join ( [ x.toHtmldiv() for x in self.productDetailsArr ] ) )
			f.write ( "</body></html>") 
		
		print "OBS: Where are the Other car category?\n\n"
			
	def filterDesc(self, description):
		filterWords = [ 'vind', 'vand', 'cumpar', 'schimb', 'masina' , 'cu' , 'oferta', 'pret', 'sau' ]
		finalString = ""
		for word in description.lower().split(' '):
			if not word.lower() in filterWords:
				finalString += word + " "
		return finalString
	
