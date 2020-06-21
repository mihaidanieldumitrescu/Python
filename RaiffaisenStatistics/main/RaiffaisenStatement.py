import xlrd
import os
import sys
import re
import pprint

from datetime import datetime
from main.EntryNew import EntryNew
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

        self.sheet = None
        self.overdraft_flag = False

    def get_excel_headers(self, rx):
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
        curr_row = self.sheet.row(rx)

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
            if self.overdraft_flag:
                self.rulaj['Valoare plafon descoperit de cont'] = curr_row[0].value

    def get_statement_row(self, rx):

        # This is where operations are listed
        # 		0 Data inregistrare
        # 		1 Data tranzactiei
        # 		2 Suma debit
        # 		3 Suma credit
        # 		4 Nr. OP
        # 		5 Cod fiscal beneficiar
        # 		6 Ordonator final
        # 		7 Beneficiar final
        # 		8 Nume/Denumire  ordonator/beneficiar"
        # 		9 "Denumire Banca ordonator/ beneficiar"
        # 		10 "Nr. cont in/din care se  efectueaza tranzactiile"
        # 		11 Descrierea tranzactiei

        curr_row = self.sheet.row(rx)

        (data_inregistrare,
         data_tranzactiei,
         suma_debit,
         suma_credit,
         nr_op,
         cod_fiscal_beneficiar,
         ordonator_final,
         beneficiar_final,
         nume_sau_denumire_ordonator_beneficiar,
         den_banca_ordonator,
         nr_cont,
         descrierea_tranzactiei) = list(map(lambda x: x.value, curr_row))

        if len(data_tranzactiei.split('/')) == 3:
            search = re.search("DUMITRESCU", nume_sau_denumire_ordonator_beneficiar)
            if re.search(r'5244$', nr_cont) and search:
                descrierea_tranzactiei = "_transfer_credit_ramburs|" + descrierea_tranzactiei
            elif re.search(r'5113$', nr_cont) and search:
                descrierea_tranzactiei = "_transfer_mastercard|" + descrierea_tranzactiei
            elif re.search(r'6184$', nr_cont) and search:
                descrierea_tranzactiei = "_transfer_visa|" + descrierea_tranzactiei
            elif re.search(r'9074$', nr_cont) and search:
                descrierea_tranzactiei = "_transfer_economii|" + descrierea_tranzactiei

            # Descrierea tranzactiei
            # ENEL ENERGIE MUNTENIA BUCUREȘTI |Card nr. XXXX XXXX XXXX XXXX |Data utilizarii cardului 2/03/2017
            # UBER   *TRIP                    |Card nr. XXXX XXXX XXXX XXXX |Valoare in EUR 4.31 |
            #                                   1 EUR = 4.6404 RON |Data utilizarii cardului 9/09/2018

            if "Data utilizarii cardului" in descrierea_tranzactiei:
                tmp = descrierea_tranzactiei.split("|")[-1]
                data_utilizarii = tmp.split()[-1]
            else:
                data_utilizarii = data_tranzactiei

            (day, month, year) = data_utilizarii.split("/")
            op_description = descrierea_tranzactiei.split("|")[0]
            if re.match("OPIB", descrierea_tranzactiei):
                op_description = descrierea_tranzactiei.split("|")[1]
            debit_value = suma_debit
            credit_value = suma_credit
            date_format = "%d/%m/%Y"
            label_str = self.label_me(op_description)

            if debit_value:
                return EntryNew(day=day,
                                month=month,
                                year=year,
                                date_log=datetime.strptime(data_utilizarii, date_format),
                                period="liquidation",
                                description=op_description,
                                value=-debit_value,
                                suma_debit=debit_value,
                                label=label_str,
                                account=self.accountName,
                                statement_type=self.statementType)
            elif credit_value:

                period = "liquidation" if 1 <= int(day) <= 15 else "advance"
                salary_pattern = self.json_config.salaryIdentifier
                if re.search(salary_pattern,
                             nume_sau_denumire_ordonator_beneficiar,
                             re.IGNORECASE):
                    label = "_salary"
                else:
                    label = "_transferredInto"

                return EntryNew(day=day,
                                month=month,
                                year=year,
                                date_log=datetime.strptime(data_utilizarii, date_format),
                                period=period,
                                description=op_description,
                                value=credit_value,
                                suma_credit=credit_value,
                                label=label,
                                account=self.accountName,
                                statement_type=self.statementType)
            else:
                raise ValueError(
                    f"Corrupt entry: No debit or credit values! \n\t* {pprint.pformat(curr_row)}\n\n")

    def label_me(self, description):

        """ Selects the correct label from json config file

        :param description: Operation description that contains service name
        :return: label name
        """

        master_labels = self.json_config.labels

        # {    "leisure" :  {
        #           "film": [ "cinema", "avatar media project" ] }
        # ...

        for masterLabel in master_labels:
            for childLabel in master_labels[masterLabel]:
                if re.search(r"|".join(master_labels[masterLabel][childLabel]), description, re.I):
                    return f"{masterLabel}.{childLabel}"
        return "spent.other"

    def load_statement(self, filename):
        full_path_to_file = os.path.join(os.environ['OneDrive'], "PythonData", "extrasDeCont", filename)
        assert os.path.isfile(full_path_to_file), f"File not found: '{full_path_to_file}'"
        print(f"{os.path.basename(filename)}")
        book = xlrd.open_workbook(full_path_to_file)
        self.sheet = book.sheet_by_index(0)

        statement_entries = []

        self.json_config.load_file()

        for rx in range(self.sheet.nrows):

            if rx < 18:
                self.get_excel_headers(rx)
            elif rx >= 18:
                statement_entries.append(self.get_statement_row(rx))

        statement_date = self.headers.get('Perioada') if self.headers.get('Perioada') else self.headers.get('Data generare extras')
        print(f"\t -> {self.accountName}, {statement_date}, {self.statementType}, entries={len(self.operations)}\n")

        return statement_entries


if __name__ == "__main__":
    assert len(sys.argv) > 1, r"Please specify a excel file found in 'Onedrive\PythonData\extrasDeCont' "
    testObj = Statement()
    testObj.load_statement(sys.argv[1])
    print(pprint.pformat(testObj.data))