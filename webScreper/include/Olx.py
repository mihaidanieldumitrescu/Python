from bs4 import BeautifulSoup
import urllib2

class Olx(object):

	def __init__(self, searchStr):
		self.products = []
		self.loadProducts( searchStr )

	def _del__(self):
		print self.products

	def loadProducts (self, productName):

		url = "https://www.olx.ro/oferta/q-" + productName + "/"
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
			print "finding all paragraphs.. \n\n"
			frames = soup.div.find_all('tr', {"class" : "wrap"})
			if len ( frames ) == 0:
				print "Error: Either link is wrong or something changed in page structure!\n\n"
				print soup
			for link in frames:
			    productTitle = link.strong.string.encode('ascii', 'ignore') 
			    productPrice = ""
			    priceArr = ( link.find_all( 'p', { "class" : "price"}))
			    if priceArr[0]:
			    	productPrice = priceArr[0].strong.string
				print { "desc" : productTitle, "price" : productPrice }
			    self.products.append({ "desc" : productTitle, "price" : productPrice })

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

			#print str ( linkNextPage )
