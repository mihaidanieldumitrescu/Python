import xlrd
import os
import sys
import re
import pprint


class Statement(object):

	def __init__(self):
		self.pp = pprint.PrettyPrinter( indent=4)
		self.data ={
								"headers" : {
												"Data generare extras": None,
												"Numar extras" : None,
												"Nume client" : None,
												"Adresa client" : None,
												"Numar client" : None,
												"Cod BIC Raiffeisen Bank" : None,
												"Unitate Bancara" : None,
												
												"Cod IBAN" : None,
												"Tip cont" : None,
												"Valuta" : None
											},
								"rulaj" : {
												"Sold initial" : 0,
												"Rulaj debitor"	: 0,
												"Rulaj creditor" : 0,
												"Sold final" : 0
											},
								"operations" : []
		}

		self.example = { 													
													"Data inregistrare"  : "" ,
													"Data tranzactiei" : "" ,
													"Suma debit" : "" ,
													"Suma credit" : "" ,
													"Nr. OP" : "" ,
													"Cod fiscal beneficiar" : "" ,
													"Ordonator final" : "" ,
													"Beneficiar final" : "" ,
													"Nume/Denumire ordonator/beneficiar" : "" ,
													"Denumire Banca ordonator/ beneficiar" : "" ,
													"Nr. cont in/din care se efectueaza tranzactiile" : "" ,
													"Descrierea tranzactiei" : "" 
												
						}
			
	def readStatement(self):
		pass
	
	def loadStatement(self, filename ):
		files = filename
		fullPathToFile = os.path.join ( os.environ['OneDrive'], "PythonData" ,"extrasDeCont", filename )
		print "trying to open " + fullPathToFile
		book = xlrd.open_workbook( fullPathToFile )
		sh = book.sheet_by_index(0)

		for rx in range(sh.nrows):
			index = 0
			currRow = sh.row(rx)
			if rx == 0:
				self.data['headers']['Data generare extras'] = currRow[1].value
			elif rx == 1:
				self.data['headers']['Numar extras'] = currRow[1].value
			elif rx == 5:
				self.data['headers']['Nume client'] = currRow[1].value
			elif rx == 6:
				self.data['headers']['Adresa client'] = currRow[1].value			
			elif rx == 14:

				self.data['rulaj']['Sold initial'] =   currRow[0].value 
				self.data['rulaj']['Rulaj debitor'] =  currRow[1].value 					
				self.data['rulaj']['Rulaj creditor'] =   currRow[2].value  
				self.data['rulaj']['Sold final'] =  currRow[3].value 
			elif rx > 17:
				
				if len ( currRow[1].value.split('/') ) == 3:
					self.data['operations'].append ( {
					
									"Data inregistrare"  : currRow[0].value ,
									"Data tranzactiei" : currRow[1].value ,
									"Suma debit" : currRow[2].value  ,
									"Suma credit" : currRow[3].value ,
									"Nume/Denumire ordonator/beneficiar" : currRow[8].value,
									"Descrierea tranzactiei" : currRow[11].value
								} )

		#self.pp.pprint (self.data)

if __name__ == "__main__":
	testObj = Statement()
	if len ( sys.argv ) > 1:
		testObj.loadStatement(  sys.argv[1] )
	else:
		print "Please specify a excel file found in 'Onedrive\PythonData\extrasDeCont' "