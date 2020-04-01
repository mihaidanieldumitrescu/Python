import xlrd
import os
import sys
import re
import pprint
from json_config.JsonConfig import JsonConfig


class Statement(object):
	"""
		Contains data found in one excel statement file

		"headers": {
						"Data generare extras": None,
						"Numar extras": None,
						"Nume client": None,
						"Adresa client": None,
						"Numar client": None,
						"Cod BIC Raiffeisen Bank": None,
						"Unitate Bancara": None,

						"Cod IBAN": None,
						"Tip cont": None,
						"Valuta": None
					},
		"rulaj": {
						"Sold initial": 0,
						"Rulaj debitor": 0,
						"Rulaj creditor": 0,
						"Sold final": 0
					},
		"operations": []
	"""
	def __init__(self):
		self.json_config = JsonConfig()
		self.statementType = None
		self.accountName = None
		self.headers = {}
		self.operations = []
		self.rulaj = {}

	def load_statement(self, filename):
		full_path_to_file = os.path.join(os.environ['OneDrive'], "PythonData", "extrasDeCont", filename)
		assert os.path.isfile(full_path_to_file), f"File not found: '{full_path_to_file}'"
		print(f"{os.path.basename(filename)}")
		book = xlrd.open_workbook(full_path_to_file)
		sh = book.sheet_by_index(0)
		overdraft_flag = 0

		self.json_config.load_file()

		""" OVERDRAFT STATEMENT SAMPLE
		0  Data generare extras:	xx/xx/xx
		1  Numar extras:	xx
		2	
		3	
		4	
		5  Nume client:	XX
		6  Adresa:	
		7  Numar client:	xxxxxxxxxx
		8  Cod BIC Raiffeisen Bank:	XXXXXXXX
		9  Unitate Bancara:	RAIFFEISEN BANK S.A.
		10	
		11 Cod IBAN:	ROxxRZBR00000x00xxxxxxxx
		12	
		13 Sold initial	Rulaj debitor	Rulaj creditor	Sold final
		14 0			0				0				0
		15	
		16 Valoare plafon descoperit de cont	Rata dobanda debitoare	Data expirarii descoperitului de cont	
		17 0                                    0                       0  
		18 
		19 Data inregistrare	Data tranzactiei	Suma debit	Suma credit	Nr. OP	Cod fiscal beneficiar	Ordonator final	Beneficiar final	"Nume/Denumire  ordonator/beneficiar"	"Denumire Banca ordonator/ beneficiar"	"Nr. cont in/din care se  efectueaza tranzactiile"	Descrierea tranzactiei
	    20 
	    21 FIRST ENTRY ...
		"""
		for rx in range(sh.nrows):
			curr_row = sh.row(rx)
			if rx == 0:
				# Data generare extras: -> Monthly statement
				# Perioada: -> At demand statement
				if curr_row[0].value == "Perioada:":
					self.statementType = 'OnDemand'
					self.headers['Perioada'] = curr_row[1].value
				elif curr_row[0].value == "Data generare extras:":
					self.statementType = 'Monthly'
					self.headers['Data generare extras'] = curr_row[1].value
			elif rx == 1:
				# Numar extras:	xx
				self.headers['Numar extras'] = curr_row[1].value
			elif rx == 5:
				# Nume client: xx
				self.headers['Nume client'] = curr_row[1].value
			elif rx == 6:
				# Adresa: xx
				self.headers['Adresa client'] = curr_row[1].value
			elif rx == 11:
				# Cod IBAN:	ROxxRZBR00000x00xxxxxxxx
				self.headers['Cod IBAN'] = curr_row[1].value
				acc_name = self.json_config.return_account_name(curr_row[1].value)
				if acc_name:
					self.accountName = acc_name
				else:
					self.accountName = "Unknown"
			elif rx == 14:
				# 13 Sold initial	Rulaj debitor	Rulaj creditor	Sold final
				# 14 0				0				0				0
				self.rulaj['Sold initial'] = curr_row[0].value
				self.rulaj['Rulaj debitor'] = curr_row[1].value
				self.rulaj['Rulaj creditor'] = curr_row[2].value
				self.rulaj['Sold final'] = curr_row[3].value
			elif rx == 16:
				if re.search("Valoare plafon descoperit de cont", curr_row[0].value):
					overdraft_flag = 1

			elif rx == 17:
				if overdraft_flag:
					self.rulaj['Valoare plafon descoperit de cont'] = curr_row[0].value
			elif rx >= 18:

				# This is where operations are listed
				# 		19 Data inregistrare	Data tranzactiei	Suma debit	Suma credit	Nr. OP	Cod fiscal beneficiar	Ordonator final	Beneficiar final	"Nume/Denumire  ordonator/beneficiar"	"Denumire Banca ordonator/ beneficiar"	"Nr. cont in/din care se  efectueaza tranzactiile"	Descrierea tranzactiei

				if len(curr_row[1].value.split('/')) == 3:
					card_cf = ""
					compiled = re.compile("DUMITRESCU")
					search = compiled.search(curr_row[8].value)
					if re.search(r'5244$', curr_row[10].value) and search:
						card_cf = "_transfer_credit_ramburs|"
					elif re.search(r'5113$', curr_row[10].value) and search:
						card_cf = "_transfer_mastercard|"
						curr_row[2].value = 0
						curr_row[3].value = 0
					elif re.search(r'6184$', curr_row[10].value) and search:
						card_cf = "_transfer_visa|"
						curr_row[2].value = 0
						curr_row[3].value = 0
					elif re.search(r'9074$', curr_row[10].value) and search:
						card_cf = "_transfer_economii|"

					# ENEL ENERGIE MUNTENIA BUCUREȘTI |Card nr. XXXX XXXX XXXX XXXX |Data utilizarii cardului 2/03/2017
					# UBER   *TRIP                    |Card nr. XXXX XXXX XXXX XXXX |Valoare in EUR 4.31 |
					#                                   1 EUR = 4.6404 RON |Data utilizarii cardului 9/09/2018

					if "Data utilizarii cardului" in curr_row[11].value:
						tmp = curr_row[11].value.split("|")[-1]
						# Data utilizarii cardului 8/09/2018

						data_utilizarii = tmp.split()[-1]
					else:
						data_utilizarii = curr_row[1].value

					self.operations.append({

									"Data inregistrare": curr_row[0].value,
									"Data tranzactiei": curr_row[1].value,
									"Data utilizarii cardului": data_utilizarii,
									"Suma debit": curr_row[2].value,
									"Suma credit": curr_row[3].value,
									"Nume/Denumire ordonator/beneficiar": curr_row[8].value,
									"Descrierea tranzactiei": card_cf + curr_row[11].value

								})
		statement_date = self.headers.get('Perioada') if self.headers.get('Perioada') else self.headers.get('Data generare extras')
		print(f"\t ->{self.accountName}, {statement_date}, {self.statementType}\n")

	def sold_precendent(self):
		sold = float(self.rulaj['Sold initial'])
		if 'Valoare plafon descoperit de cont' in self.rulaj:
			sold += float(self.rulaj['Valoare plafon descoperit de cont'])

		for operation in self.operations:
			if re.search(self.json_config.salaryIdentifier, operation['Nume/Denumire ordonator/beneficiar'], re.I):
				break
			if operation['Suma debit'] != '':
				sold -= float(operation['Suma debit'])
			if operation['Suma credit'] != '':
				sold += float(operation['Suma credit'])
		return sold


if __name__ == "__main__":
	assert len(sys.argv) > 1, r"Please specify a excel file found in 'Onedrive\PythonData\extrasDeCont' "
	testObj = Statement()
	testObj.load_statement(sys.argv[1])
	print(pprint.pformat(testObj.data))
