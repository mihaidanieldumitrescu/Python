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
        self.rulaj = {}

        self.sheet = None
        self.overdraft_flag = False

        self.statement_filename = None
        self.entries = []

    @staticmethod
    def get_cell_column_value(column_number, row):
        return row[column_number].value

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

        column_a = Statement.get_cell_column_value(0, curr_row)
        column_b = Statement.get_cell_column_value(1, curr_row)

        if rx == 0:
            # Data generare extras: -> Monthly statement
            # Perioada: -> At demand statement
            if column_a == "Perioada:":
                self.statementType = 'OnDemand'
                self.headers['Perioada'] = column_b
            elif column_a == "Data generare extras:":
                self.statementType = 'Monthly'
                self.headers['Data generare extras'] = column_b
        elif rx == 1:
            # Numar extras:	xx
            self.headers['Numar extras'] = column_b
        elif rx == 5:
            # Nume client: xx
            self.headers['Nume client'] = column_b
        elif rx == 6:
            # Adresa: xx
            self.headers['Adresa client'] = column_b
        elif rx in (11, 12, 13):
            if 'Cod IBAN:' == column_a:
                iban_code = column_b

                self.headers['Cod IBAN'] = iban_code

                acc_name = self.json_config.return_account_name(iban_code)
                self.accountName = acc_name if acc_name else "Unknown"

        elif rx == 14:
            # 13 Sold initial	Rulaj debitor	Rulaj creditor	Sold final
            # 14 0				0				0				0
            self.rulaj['Sold initial'] = curr_row[0].value
            self.rulaj['Rulaj debitor'] = curr_row[1].value
            self.rulaj['Rulaj creditor'] = curr_row[2].value
            self.rulaj['Sold final'] = curr_row[3].value
        elif rx in (16, 17):
            if "Valoare plafon descoperit de cont" == Statement.get_cell_column_value(0, curr_row):
                self.headers['Valoare plafon descoperit de cont'] = Statement.get_cell_column_value(0, self.sheet.row(rx + 1))
                self.overdraft_flag = True

    def is_account(self, account_number, defined_account):
        assert defined_account in self.json_config.accountNames, f"Account name '{defined_account}' not found in JSON config file"

        if account_number == self.json_config.accountNames[defined_account]:
            return True
        return False

    def is_transfer_between_visa_mastercard(self, source_account_id, destination_account_id):
        test_list = []

        for account_id in source_account_id, destination_account_id:
            for account_name in "Visa", "Mastercard":
                if self.is_account(account_id, account_name):
                    test_list.append(True)

        return test_list == [True, True]

    @staticmethod
    def clean_operation_description(description):
        return " ".join(filter(lambda x: 'OPIB' not in x, description.split('|')))

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
         nume_beneficiar,
         den_banca_ordonator,
         nr_cont_sursa,
         descrierea_tranzactiei) = list(map(lambda x: x.value, curr_row))

        numar_cont_destinatie = self.headers['Cod IBAN']
        assert numar_cont_destinatie, "IBAN code not found!"

        if len(data_tranzactiei.split('/')) == 3:

            s = None
            is_adjustment = False

            if self.is_transfer_between_visa_mastercard(nr_cont_sursa, numar_cont_destinatie):
                is_adjustment = True
            elif self.is_account(nr_cont_sursa, "Ramburs credit"):
                s = "cont_credit_ramburs|"
            elif self.is_account(nr_cont_sursa, "Mastercard"):
                s = "cont_mastercard|"
            elif self.is_account(nr_cont_sursa, "Visa"):
                s = "cont_visa|"
            elif self.is_account(nr_cont_sursa, "Economii"):
                s = "cont_economii|"

            if s:
                descrierea_tranzactiei = s + Statement.clean_operation_description(descrierea_tranzactiei)

            # Descrierea tranzactiei
            # ENEL ENERGIE MUNTENIA BUCUREȘTI |Card nr. XXXX XXXX XXXX XXXX |Data utilizarii cardului 2/03/2017
            # UBER   *TRIP                    |Card nr. XXXX XXXX XXXX XXXX |Valoare in EUR 4.31 |
            #                                   1 EUR = 4.6404 RON |Data utilizarii cardului 9/09/2018

            if "Data utilizarii cardului" in descrierea_tranzactiei:
                op_description = descrierea_tranzactiei.split("|")[0].title()
                data_utilizarii = descrierea_tranzactiei.split("|")[-1].split()[-1]
            else:
                data_utilizarii = data_tranzactiei
                directie = "in" if suma_debit else "din"
                op_description = f"<small> {nume_beneficiar} - {directie}_{descrierea_tranzactiei} </small>".title()

            debit_value = suma_debit
            credit_value = suma_credit

            if is_adjustment:
                label_str = self.label_adjustment(nr_cont_sursa, numar_cont_destinatie)
            elif debit_value:
                label_str = self.label_debit(op_description)
            elif credit_value:
                label_str = self.label_credit(nume_beneficiar)

            entry = EntryNew(date_log=datetime.strptime(data_utilizarii, "%d/%m/%Y"),
                             description=op_description,
                             value=debit_value if debit_value else credit_value,
                             suma_debit=debit_value,
                             suma_credit=credit_value,
                             label=label_str,
                             account=self.accountName,
                             statement_type=self.statementType)

            return entry

    def label_debit(self, description):

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

    def label_credit(self, nume_beneficiar):

        salary_pattern = self.json_config.salaryIdentifier
        found_salary_pattern = re.search(salary_pattern, nume_beneficiar, re.I)
        return "_salary" if found_salary_pattern else "_transferredInto"

    def label_adjustment(self, source_account, destination_account):

        # [{ "Account name": "Account number" }]
        account_items = self.json_config.accountNames.items()
        source, destination = "Unknown", "Unknown"

        for item in account_items:
            if item[1] == source_account:
                source = item[0]
            elif item[1] == destination_account:
                destination = item[0]

        return f"adjustment.{source}To{destination}"

    def get_identifier_dict(self):
        return dict(data_generare_extras=self.headers.get('Data generare extras'),
                    cod_iban=self.headers.get('Cod IBAN'),
                    tranzactii=len(self.entries))

    def load_statement(self, file_path):
        """
        Parse filename statement
        :param file_path:
        :return: list
        """

        self.statement_filename = os.path.basename(file_path)

        book = xlrd.open_workbook(file_path)
        self.sheet = book.sheet_by_index(0)

        self.json_config.load_file()

        for rx in range(self.sheet.nrows):

            if rx < 18:
                self.get_excel_headers(rx)
            elif rx >= 18:
                entry = self.get_statement_row(rx)
                if entry:
                    self.entries.append(entry)

        statement_date = self.headers.get('Perioada') if self.headers.get('Perioada') else self.headers.get('Data generare extras')

        print(f"{os.path.basename(file_path)}")
        print(f"\t -> {self.accountName}, {statement_date}, {self.statementType}, entries={len(self.entries)}\n")



if __name__ == "__main__":
    assert len(sys.argv) > 1, r"Please specify a excel file found in 'Onedrive\PythonData\extrasDeCont' "
    testObj = Statement()
    testObj.load_statement(sys.argv[1])
    print(pprint.pformat(testObj.data))
