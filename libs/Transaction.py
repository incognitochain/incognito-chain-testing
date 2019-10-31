import re, time
import json
import pytest
import requests

class Transaction:
    def __init__(self, rpc):
        self.rpc = rpc

    def sendTransaction(self,  sender_privatekey, receiver_paymentaddress, amount_prv):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "createandsendtransaction",
                "params": [sender_privatekey, {receiver_paymentaddress: amount_prv}, -1, 0], "id": 1}
        response = requests.post(self.rpc, data=json.dumps(data), headers=headers)
        # print(response.text)
        resp_json = json.loads(response.text)

        if resp_json['Error'] == None:
            # print (aa['Result']['TxID'])
            # print (aa['Result']['ShardID'])
            return resp_json['Result']['TxID']
        else:
            print(resp_json['Error']['Message'])
            return resp_json['Error']['Message']

    def getBalance(self, address_privatekey):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "getbalancebyprivatekey", "params": [address_privatekey], "id": 1}
        response = requests.post(self.rpc, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)

        if resp_json['Error'] == None:
            return resp_json['Result']
        else:
            print(resp_json['Error']['Message'])
            return resp_json['Error']['Message']
