
from include.Olx import Olx,OlxCars
from include.iaBilet import iaBilet
from include.Travelator import Travelator

import sys


if len ( sys.argv ) > 1:
	if sys.argv[1] == "olx":
		obj = Olx( sys.argv[2], 30 )
		obj.loadProducts()
	elif sys.argv[1] == "olxcars":
		obj = OlxCars()
	elif sys.argv[1] == "iabilet":
		obj = iaBilet()
	elif sys.argv[1] == "travelator":
		obj = Travelator()
	else:
		print "Unknown parameter!"
else:
	print "Please specify site name!"

