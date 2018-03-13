
from include.Olx import Olx
from include.iaBilet import iaBilet
from include.Travelator import Travelator

import sys


if len ( sys.argv ) > 1:
	if sys.argv[1] == "olx":
		obj = Olx( sys.argv[2] )
	elif sys.argv[1] == "iabilet":
		obj = iaBilet()
	elif sys.argv[1] == "travelator":
		obj = Travelator()
	else:
		print "Unknown parameter!"
else:
	print "Please specify site name!"

