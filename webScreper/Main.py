
from include.Olx import Olx
from include.iaBilet import iaBilet

import sys


if len ( sys.argv ) > 1:
	if sys.argv[1] == "olx":
		obj = Olx()
	elif sys.argv[1] == "iabilet":
		obj = iaBilet()
	else:
		print "Unknown parameter!"
else:
	print "Please specify site name!"

