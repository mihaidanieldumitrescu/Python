from html import HTML
from Entries import Entries
from EntryNew import EntryNew

class WriteHtmlOutput:

	def __init__(self, entry):
	        self.htmlOutput = HTML()
		self.printMe = entry
		self.writeOutput()
		pprint (self.printMe)

	def writeOutput(self):
		output = open ( "budgetStatistics.html", "w")
       		current = EntryNew()
		table = self.htmlOutput.table()
		for entry in self.printMe:
		    row = table.tr
		    if current.period != entry.period:
		        current.period = entry.period
		        row.td( entry.period )
		    else:
		        row.td()
		        
		    if current.month != entry.month:
		        current.month = entry.month
		        row.td( entry.month )
		    else:
		        row.td()
		        
		    if current.year != entry.year:
		        current.year = entry.year
		        row.td( entry.year )
		    else:
		        row.td()
		    row.td( entry.description )
		    row.td( entry.value )
		    row.td( entry.label )

		output.write ( str (self.htmlOutput ) )
		output.close

