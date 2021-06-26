import os
import json
from .defined_labels import LABELS
from .sensitive_information import SENSITIVE_INFO


class JsonConfig:

    def __init__(self, path_to_config_file=os.path.join(os.environ['OneDrive'], "PythonData", "config", "definedLabels.json")):
        self.path = path_to_config_file
        self.labels = None
        self.accountNames = None
        self.rentValue = None
        self.salaryIdentifier = None
        self.creditCardPayment = None
        self.owedMoneyPaidBack = None

    def load_file(self):
        """ Load file defined in self.path """

        self.labels = LABELS['labelDict']
        self.accountNames = SENSITIVE_INFO['accountNames']
        self.rentValue = SENSITIVE_INFO['rent']
        self.salaryIdentifier = SENSITIVE_INFO['salaryAccountName']
        self.creditCardPayment = SENSITIVE_INFO['creditCardPaymentAccount']
        self.owedMoneyPaidBack = SENSITIVE_INFO['fatherBTaccount']

    def __str__(self):
        return f"\
                self.path = {self.path} \n\n\
                self.labels = {self.labels.keys()} \n\
                self.accountNames = {str(self.accountNames)} \n\
                self.rentValue = {str(self.rentValue)} \n\
                self.salaryIdentifier = {str(self.salaryIdentifier)} \n\
                self.creditCardPayment = {str(self.creditCardPayment)} \n\
                self.owedMoneyPaidBack = {str(self.owedMoneyPaidBack)}\n\n"

    def return_account_name(self, iban_code):
        for account_name, iban_json in self.accountNames.items():
            if iban_code == iban_json:
                return account_name
        return None


if __name__ == "__main__":
    j = JsonConfig()
    j.load_file()
    print(j)
