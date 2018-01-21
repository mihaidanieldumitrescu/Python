import xlrd

class Statement(object):

	def __init__(self):
		self.statements = [
							{
								"headers" : {
												"Data generare extras": "",
												"Numar extras" : "",
												"Nume client" :"",
												"Adresa" : "",
												"Numar client" : "",
												"Cod BIC Raiffeisen Bank" : "",
												"Unitate Bancara" : "",
												
												"Cod IBAN" : "",
												"Tip cont" : "",
												"Valuta" : ""
											},
								"status" : {
												"Sold initial" : 0,
												"Rulaj debitor"	: 0,
												"Rulaj creditor" : 0,
												"Sold final" : 0
											},
								"content" : {
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
							}
						]

	def readStatement(self):
		pass
	
	def popStatement(self):
		pass

