from IncognitoChain.Configs.Constants import PBNB_ID


class CustodianRemoteAddr:

    def __init__(self, data):
        self.data: dict = data

    def get_remote_addr(self, token, custodian_acc=None):
        addr_type = 0 if token == PBNB_ID else 1
        if custodian_acc is not None:
            return self.data[custodian_acc][addr_type]
        else:
            return [self.data[custodian][addr_type] for custodian, addr in self.data.items()]

    def get_accounts(self, inc_addr=None):
        if inc_addr is None:
            return self.data.keys()
        else:
            for acc in self.data.keys():
                if acc.payment_key == inc_addr:
                    return acc
