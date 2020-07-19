import pytest

import pprint as pp
from includes.Entries import Entries
from main.RaiffaisenStatement import Statement
from json_config.JsonConfig import JsonConfig

"""

MASTERCARD 

OPIB/1 |25 martie
DOBANDA DEBITOARE
OPIB/1 |Transfer intre conturi proprii
OPIB/1 |Git init
OPIB/1 |25 aprilie
OPIB/1 |Balans Revolut (good-food) |ramasi luna martie

VISA

OPIB/1 |Economii martie
OPIB/1 |Git init
OPIB/1 |Nikon Monarch 5 8x42 |cel.ro
OPIB/1 |Transfer intre conturi proprii
OPIB/1 |books-express.ro |Shell programming in UNIX
COMISION ADMINISTRARE STANDARD

"""

config = JsonConfig()
config.load_file()

testdata = [
    [r"test_data/20_04_23_Mastercard.xlsx", 15, "Monthly", True, config.accountNames["Mastercard"]],
    [r"test_data/20_04_31_Visa.xlsx", 42, "Monthly", False, config.accountNames["Visa"]]
]


@pytest.mark.parametrize("filename, operations, statement_type, overdraft, iban", testdata, ids=["Mastercard statement", "Visa statement"])
def test_statement(filename, operations, statement_type, overdraft, iban):
    s = Statement()
    entries = s.load_statement(filename)
    assert s.statementType == statement_type
    assert s.overdraft_flag is overdraft
    assert s.headers['Cod IBAN'] == iban
    if not len(entries) == operations:
        raise ValueError("Missing entries")


def test_get_entries():

    ent = Entries(r"test_data")
    ent.extract_data_excel_sheets()

    # Remove empty lines
    entries_list = list(filter(None, ent.get_entries()))

    # print(pp.pprint(list(map(lambda x: str(x), entries_list))))

