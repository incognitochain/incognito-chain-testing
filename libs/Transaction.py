import json
import requests
from libs.AutoLog import WARN, DEBUG, INFO

class Transaction():
    def __init__(self, ip, rpc):
        self.url = "http://" + ip + ":" + str(rpc)

    def sendTransaction(self, sender_privatekey, receiver_paymentaddress, amount_prv, fee=-1, privacy=1):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "createandsendtransaction",
                "params": [sender_privatekey, {receiver_paymentaddress: amount_prv}, fee, privacy], "id": 1}
        """
        3rd param: -1 => auto estimate fee; >0 => fee * transaction size (KB)
        4th param: 0 => no privacy ; 1 => privacy
        """

        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        # print(response.text)
        resp_json = json.loads(response.text)

        if resp_json['Error'] is None:
            # print (resp_json['Result']['TxID'])
            # print (resp_json['Result']['ShardID'])
            return resp_json['Result']['TxID'], "SUCCESS"
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256]

    def getBalance(self, privatekey):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "getbalancebyprivatekey", "params": [privatekey], "id": 1}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)

        if resp_json['Error'] is None:
            return resp_json['Result']
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256]

    def get_txbyhash(self, txid):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "gettransactionbyhash", "params": [txid], "id": 1}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        DEBUG(resp_json)

        if resp_json['Error'] is None:
            return resp_json['Result']['BlockHash'], resp_json['Result']['ShardID'], resp_json['Result']['IsPrivacy'],resp_json['Result']['PrivacyCustomTokenIsPrivacy']
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256]

    def estimatefee_PRV(self, sender_privatekey, receiver_paymentaddress, amount_prv, fee=0, privacy=0):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "estimatefee",
                "params": [sender_privatekey, {receiver_paymentaddress: amount_prv}, fee, privacy], "id": 1}
        """
        3rd param: -1 => auto estimate fee; >0 => fee * transaction size (KB)
        4th param: 0 => no privacy ; 1 => privacy
        """

        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        # print(response.text)
        resp_json = json.loads(response.text)

        if resp_json['Error'] is None:
            # print (resp_json['Result']['TxID'])
            # print (resp_json['Result']['ShardID'])
            return resp_json['Result']['EstimateTxSizeInKb'], "SUCCESS"
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256]

    ###############
    # TOKEN SECTION
    ###############
    def init_customToken(self, privatekey, payment_address, symbol, amount, prv_fee=-1):
        headers = {'Content-Type': 'application/json'}
        # TokenTxType = 0 => init
        data = {"id": 1, "jsonrpc": "1.0", "method": "createandsendprivacycustomtokentransaction",
                "params": [
                    privatekey, None, prv_fee, 1,
                    {
                        "Privacy": True,
                        "TokenID": "",
                        "TokenName": symbol + "_" + symbol,
                        "TokenSymbol": symbol,
                        "TokenFee": 0,
                        "TokenTxType": 0,
                        "TokenAmount": amount,
                        "TokenReceivers": {
                            payment_address: amount
                        }
                    }
                ]}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        DEBUG(resp_json)

        if resp_json['Error'] is None:
            return resp_json['Result']['TxID'], resp_json['Result']['TokenID']
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256]

    def send_customTokenTransaction(self, sender_privatekey, receiver_paymentaddress, tokenid, amount_customToken,
                                    prv_fee=0, token_fee=0, prv_amount=0, prv_privacy=0,token_privacy=0):
        headers = {'Content-Type': 'application/json'}
        # TokenTxType = 1 => send token
        data = {"jsonrpc": "1.0", "method": "createandsendprivacycustomtokentransaction", "id": 1,
                "params": [sender_privatekey, {receiver_paymentaddress: prv_amount} , prv_fee, prv_privacy,
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
                               "TokenFee": token_fee
                           },
                           "", token_privacy
                           ]}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        # print(response.text)
        resp_json = json.loads(response.text)
        DEBUG(resp_json)

        if resp_json['Error'] is None:
            return resp_json['Result']['TxID'], resp_json['Result']['ShardID']
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256]

    def get_customTokenBalance(self, privatekey, tokenid):
        headers = {'Content-Type': 'application/json'}
        data = {"id": 1, "jsonrpc": "1.0", "method": "getbalanceprivacycustomtoken",
                "params": [privatekey, tokenid]}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        DEBUG(resp_json)

        if resp_json['Error'] is None:
            return resp_json['Result'], "SUCCESS"
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256]

    def estimatefee_token(self, sender_privatekey, receiver_paymentaddress, tokenid, amount_customToken,
                          prv_fee=0, token_fee=0):
        headers = {'Content-Type': 'application/json'}
        # TokenTxType = 1 => send token
        data = {"jsonrpc": "1.0", "method": "estimatefee", "id": 1,
                "params": [sender_privatekey, None, prv_fee, 1,
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
                               "TokenFee": token_fee
                           },
                           "", 0
                           ]}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        DEBUG(resp_json)

        if resp_json['Error'] is None:
            return resp_json['Result']['EstimateTxSizeInKb'], "SUCCESS"
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256]
