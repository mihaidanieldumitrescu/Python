import xlrd
import os
import sys
import re
import pprint

from json_config.JsonConfig import JsonConfig


class Statement(object):

	def __init__(self):
		self.json_config = JsonConfig()
		self.statementType = None
		self.accountName = None
		self.headers = {}
		self.rulaj = {}
		self.data = {
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
		}

		self.example = {
													"Data inregistrare": "",
													"Data tranzactiei": "",
													"Suma debit": "",
													"Suma credit": "",
													"Nr. OP": "",
													"Cod fiscal beneficiar": "",
													"Ordonator final": "",
													"Beneficiar final": "",
													"Nume/Denumire ordonator/beneficiar": "",
													"Denumire Banca ordonator/ beneficiar": "",
													"Nr. cont in/din care se efectueaza tranzactiile": "",
													"Nr. cont in/din care se efectueaza tranzactiile": "",
													"Descrierea tranzactiei": ""

						}

	def load_statement(self, filename):
		full_path_to_file = os.path.join(os.environ['OneDrive'], "PythonData", "extrasDeCont", filename)
		print(f"{os.path.basename(filename)}")
		book = xlrd.open_workbook(full_path_to_file)
		sh = book.sheet_by_index(0)
		overdraft_flag = 0

		self.json_config.load_file()

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
				self.headers['Numar extras'] = curr_row[1].value
			elif rx == 5:
				self.headers['Nume client'] = curr_row[1].value
			elif rx == 6:
				self.headers['Adresa client'] = curr_row[1].value
			elif rx == 11:
				self.headers['Cod IBAN'] = curr_row[1].value
				acc_name = self.json_config.return_account_name(curr_row[1].value)
				if acc_name:
					self.accountName = acc_name
				else:
					self.accountName = "Unknown"
			elif rx == 14:
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

				if len(curr_row[1].value.split('/') ) == 3:
					cardCF = ""

					if re.search(r'5244$', curr_row[10].value) and re.search("dumitrescu", curr_row[8].value, re.IGNORECASE):
						cardCF = "transfer_ramburs_cumparaturi|"
					elif re.search(r'5113$', curr_row[10].value) and re.search("dumitrescu", curr_row[8].value, re.IGNORECASE):
						cardCF = "_transfer_mastercard|"
					elif re.search(r'6184$', curr_row[10].value) and re.search("dumitrescu", curr_row[8].value, re.IGNORECASE):
						cardCF = "_transfer_visa|"
					elif re.search(r'9074$', curr_row[10].value) and re.search("dumitrescu", curr_row[8].value, re.IGNORECASE):
						cardCF = "_transfer_economii|"

					# ENEL ENERGIE MUNTENIA BUCURESTI |Card nr. XXXX XXXX XXXX XXXX |Data utilizarii cardului 2/03/2017
					# UBER   *TRIP                    |Card nr. XXXX XXXX XXXX XXXX |Valoare in EUR 4.31 |
					#                                   1 EUR = 4.6404 RON |Data utilizarii cardului 9/09/2018

					if "Data utilizarii cardului" in curr_row[11].value:
						tmp = curr_row[11].value.split("|")[-1]
						# Data utilizarii cardului 8/09/2018

						data_utilizarii = tmp.split()[-1]
					else:
						data_utilizarii = curr_row[1].value

					self.data['operations'].append({

									"Data inregistrare": curr_row[0].value,
									"Data tranzactiei": curr_row[1].value,
									"Data utilizarii cardului": data_utilizarii,
									"Suma debit": curr_row[2].value,
									"Suma credit": curr_row[3].value,
									"Nume/Denumire ordonator/beneficiar": curr_row[8].value,
									"Descrierea tranzactiei": cardCF + curr_row[11].value

								})
		statement_date = self.headers.get('Perioada') if self.headers.get('Perioada') else self.headers.get('Data generare extras')
		print(f"\t ->{self.accountName}, {statement_date}, {self.statementType}\n")

	def sold_precendent(self):
		sold = float(self.data['rulaj']['Sold initial'])
		if 'Valoare plafon descoperit de cont' in self.data['rulaj']:
			sold += float(self.data['rulaj']['Valoare plafon descoperit de cont'])

		for operatie in self.data['operations']:
			if re.search(self.json_config.salaryIdentifier, operatie['Nume/Denumire ordonator/beneficiar'], re.IGNORECASE):
				break
			if operatie['Suma debit'] != '':
				sold -= float(operatie['Suma debit'])
			if operatie['Suma credit'] != '':
				sold += float(operatie['Suma credit'])
		return sold


if __name__ == "__main__":
	testObj = Statement()
	if len(sys.argv) > 1:
		testObj.load_statement(sys.argv[1])

		print(pprint.pformat(testObj.data))
	else:
		print(r"Please specify a excel file found in 'Onedrive\PythonData\extrasDeCont' ")
