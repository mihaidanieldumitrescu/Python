import os
import json


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
        with open(self.path) as f:
            contents = json.load(f)
            try:
                self.labels = contents['labelDict']
                self.accountNames = contents['accountNames']
                self.rentValue = contents['rent']
                self.salaryIdentifier = contents['salaryAccountName']
                self.creditCardPayment = contents['creditCardPaymentAccount']
                self.owedMoneyPaidBack = contents['fatherBTaccount']
            except Exception as e:
                print(f"(JsonConfig) Error: {e}")
                exit()

    def return_account_name(self, iban_code):
        for account_name, iban_json in self.accountNames.items():
            if iban_code == iban_json:
                return account_name
        return None
