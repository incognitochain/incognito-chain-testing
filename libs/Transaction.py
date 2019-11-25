import json

import requests

from libs.AutoLog import WARN, DEBUG


class Transaction():
    def __init__(self, ip, rpc):
        self.url = "http://" + ip + ":" + str(rpc)

    def sendTransaction(self, sender_privatekey, receiver_paymentaddress, amount_prv):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "createandsendtransaction",
                "params": [sender_privatekey, {receiver_paymentaddress: amount_prv}, -1, 0], "id": 1}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        # print(response.text)
        resp_json = json.loads(response.text)

        if resp_json['Error'] is None:
            # print (resp_json['Result']['TxID'])
            # print (resp_json['Result']['ShardID'])
            return resp_json['Result']['TxID'], "SUCCESS"
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace']

    def getBalance(self, address_privatekey):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "getbalancebyprivatekey", "params": [address_privatekey], "id": 1}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)

        if resp_json['Error'] is None:
            return resp_json['Result']
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message']

    def send_customeTokenTransaction(self, sender_privatekey, receiver_paymentaddress, tokenid, amount_customToken):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "createandsendtransaction", "id": 1,
                "params": [sender_privatekey, None,-1,1,
                           {
                               "Privacy": True,
                               "TokenID": tokenid,
                               "TokenName": "",
                               "TokenSymbol": "",
                               "TokenTxType": 1,
                               "TokenAmount": 0,
                               "TokenReceivers": {
                                   receiver_paymentaddress: amount_customToken
                               },
                               "TokenFee": 0
                           }
                           ]}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        # print(response.text)
        resp_json = json.loads(response.text)

        if resp_json['Error'] is None:
            # print (resp_json['Result']['TxID'])
            # print (resp_json['Result']['ShardID'])
            return resp_json['Result']['TxID']
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message']

    def get_customTokenBalance(self, address_privatekey, tokenid):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "getlistprivacycustomtokenbalance", "params": [address_privatekey], "id": 1}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        DEBUG(resp_json)

        if resp_json['Error'] is None:
            for token in resp_json['Result']['ListCustomTokenBalance']:
                if token['TokenID'] == tokenid:
                    return token['Amount']
            return 0

        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message']

    def get_txbyhash(self, txid):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "gettransactionbyhash", "params": [txid], "id": 1}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        DEBUG(resp_json)

        if resp_json['Error'] is None:
            return resp_json['Result']['BlockHash'], resp_json['Result']['ShardID']
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message']
