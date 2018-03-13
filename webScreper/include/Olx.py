from bs4 import BeautifulSoup
import urllib2

class Olx(object):
	limitPages = 30
	def __init__(self, searchStr):
		self.products = []
		self.loadProducts( searchStr )


	def _del__(self):
		print self.products

	def loadProducts (self, productName):

		url = "https://www.olx.ro/oferte/q-" + productName + "/"
		sortByDesc = "?search%5Border%5D=filter_float_price%3Adesc"
		url += sortByDesc
		url = "https://www.olx.ro/auto-masini-moto-ambarcatiuni/autoturisme/?search%5Bfilter_float_price%3Afrom%5D=2000&search%5Bfilter_float_price%3Ato%5D=4000&search%5Border%5D=filter_float_price%3Aasc"
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
			    self.products.append({ "desc" : productTitle, "price" : productPrice })

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
					else:
						url = ""
				except ValueError:
					print "Error in link next page\n\n %s \n" % ( linkNextPage )
					print ValueError
				self.limitPages -= 1
			print "Done extracting ..."
			
	def getNextPage(self, lastPage):
		pass
	def printResults(self):
		
		for product in self.products:
			print "%s %s" % ( product['price'].ljust(10), product['desc'] )

			#print str ( linkNextPage )
