
from include.Olx import Olx, OlxCars, OlxProduct
from include.iaBilet import iaBilet
from include.Travelator import Travelator

import sys


if len(sys.argv) > 1:
	if sys.argv[1] == "olx":
		obj = Olx(sys.argv[2], 30)
		obj.load_products()
	elif sys.argv[1] == "olxcars":
		obj = OlxCars()
	elif sys.argv[1] == "olxproduct":
		print
		obj = OlxProduct(link=u"https://www.olx.ro/oferta/volkswagen-passat-2002-IDaWZx7.html")
		obj.load_page()

	elif sys.argv[1] == "iabilet":
		obj = iaBilet()
	elif sys.argv[1] == "travelator":
		obj = Travelator()
		obj.loadTitles()
		obj.filter()
	else:
		print("Unknown parameter!")
else:
	print("Please specify site name!")

