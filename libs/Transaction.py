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
        print(response.text)
        resp_json = json.loads(response.text)

        if resp_json['Error'] is None:
            # print (resp_json['Result']['TxID'])
            # print (resp_json['Result']['ShardID'])
            return resp_json['Result']['TxID'], "SUCCESS"
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256]

    def sendTransactionMultiOuputPRV(self, sender_privatekey, list_receiver_paymentaddress, amount_prv, fee=-1,
                                     privacy=1):
        payment = dict()
        for i in range(0, len(list_receiver_paymentaddress)):
            payment[list_receiver_paymentaddress[i]] = amount_prv

        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "createandsendtransaction",
                "params": [sender_privatekey, payment, fee, privacy], "id": 1}

        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        print(response.text)
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
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256], resp_json['Error']['Code']

    def get_txbyhash(self, txid):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "gettransactionbyhash", "params": [txid], "id": 1}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        DEBUG(resp_json)

        if resp_json['Error'] is None:
            return resp_json['Result']['BlockHash'], resp_json['Result']['ShardID'], resp_json['Result']['IsPrivacy'], \
                   resp_json['Result']['PrivacyCustomTokenIsPrivacy']
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

    def check_is_privacy_prv(self, txid):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "gettransactionbyhash", "params": [txid], "id": 1}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        DEBUG(resp_json)

        if resp_json['Error'] is None:
            if resp_json['Result']['IsPrivacy'] is True and \
                    resp_json['Result']['ProofDetail']['InputCoins'][0]['CoinDetails']['Value'] == 0:
                return True, "privacy"
            else:
                return False, "noprivacy"
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
        print(resp_json)
        DEBUG(resp_json)

        if resp_json['Error'] is None:
            return resp_json['Result']['TxID'], resp_json['Result']['TokenID']
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256]

    def send_customTokenTransaction(self, sender_privatekey, receiver_paymentaddress, tokenid, amount_customToken,
                                    prv_fee=0, token_fee=0, prv_amount=0, prv_privacy=0, token_privacy=0):
        headers = {'Content-Type': 'application/json'}
        # TokenTxType = 1 => send token
        data = {"jsonrpc": "1.0", "method": "createandsendprivacycustomtokentransaction", "id": 1,
                "params": [sender_privatekey, {receiver_paymentaddress: prv_amount}, prv_fee, prv_privacy,
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

    def send_customTokenTransaction_multioutput(self, sender_privatekey, list_receiver_paymentaddress, tokenid,
                                                token_amount,
                                                prv_fee=0, token_fee=0, prv_amount=0, prv_privacy=0, token_privacy=0):
        payment_prv = dict()
        payment_token = dict()
        for i in range(0, len(list_receiver_paymentaddress)):
            payment_prv[list_receiver_paymentaddress[i]] = prv_amount
            payment_token[list_receiver_paymentaddress[i]] = token_amount
        headers = {'Content-Type': 'application/json'}
        # TokenTxType = 1 => send token
        data = {"jsonrpc": "1.0", "method": "createandsendprivacycustomtokentransaction", "id": 1,
                "params": [sender_privatekey, payment_prv, prv_fee, prv_privacy,
                           {
                               "Privacy": True,
                               "TokenID": tokenid,
                               "TokenName": "",
                               "TokenSymbol": "",
                               "TokenTxType": 1,
                               "TokenAmount": 0,
                               "TokenReceivers": payment_token,
                               "TokenFee": token_fee
                           },
                           "", token_privacy
                           ]}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        print(response.text)
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

    def check_is_privacy_token(self, txid):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "gettransactionbyhash", "params": [txid], "id": 1}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        DEBUG(resp_json)

        if resp_json['Error'] is None:
            if resp_json['Result']['PrivacyCustomTokenIsPrivacy'] is True and \
                    resp_json['Result']['PrivacyCustomTokenProofDetail']['InputCoins'][0]['CoinDetails']['Value'] == 0:
                return True, "privacy"
            else:
                return False, "noprivacy"
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256]

    ###############
    # WITHDRAW REWARD
    ###############

    def withdrawReward(self, privateKey, paymentAddress, tokenId):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "withdrawreward",
                "params": [privateKey, 0, 0, 0,
                           {
                               "PaymentAddress": paymentAddress,
                               "TokenID": tokenId
                           }

                           ],
                "id": 1}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        DEBUG(resp_json)
        print(resp_json)
        if resp_json['Error'] is None:
            return resp_json['Result']['TxID'], "SUCCESS"
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256]

    def get_reward_prv(self, payment_address):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "getrewardamount", "params": [payment_address], "id": 1}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)

        if resp_json['Error'] is None:
            return "PRV", resp_json['Result']["PRV"]
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256], resp_json['Error']['Code']

    def get_reward_token(self, payment_address):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "getrewardamount", "params": [payment_address], "id": 1}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)

        if resp_json['Error'] is None and len(resp_json["Result"]) == 1:
            return "NoToken", "NoReward"
        elif resp_json['Error'] is None and len(resp_json["Result"]) > 1:
            result_token = dict()
            for k, v in resp_json["Result"].items():
                if k != "PRV" and v > 0:
                    key = k
                    value = v
                    result_token[k] = v
                    break
            if not result_token:
                return "NoToken", "NoReward"
            else:
                return list(result_token.keys())[0], list(result_token.values())[0]
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256], resp_json['Error']['Code']

    def get_reward_specific_token(self, payment_address, token_id):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "getrewardamount", "params": [payment_address], "id": 1}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        # print(resp_json)
        if resp_json['Error'] is None:
            return token_id, resp_json['Result'][token_id]
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256], resp_json['Error']['Code']

    def check_reward_specific_token(self, payment_address, token_id):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "getrewardamount", "params": [payment_address], "id": 1}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        # print(resp_json)
        if resp_json['Error'] is None:
            for k, v in resp_json["Result"].items():
                if k == str(token_id):
                    return "Token exist", "success"
            return "token not exist", "success"
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256], resp_json['Error']['Code']

    def get_full_reward(self, payment_address):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "getrewardamount", "params": [payment_address], "id": 1}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)

        if resp_json['Error'] is None and len(resp_json["Result"]) == 1:
            return "NoToken", "NoReward"
        elif resp_json['Error'] is None and len(resp_json["Result"]) > 1:
            result_token = dict()
            for k, v in resp_json["Result"].items():
                if k != "PRV" and v > 0:
                    key = k
                    value = v
                    result_token[k] = v

            if not result_token:
                return "NoToken", "NoReward"
            else:
                return list(result_token.keys()), list(result_token.values())
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256], resp_json['Error']['Code']

    ###############
    # WITHDRAW REWARD
    ###############

    def defragment_prv(self, private_key, min_value, auto_fee=-1, is_privacy=1):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "defragmentaccount",
                "params": [private_key, min_value, auto_fee, is_privacy,
                           ],
                "id": 1}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        DEBUG(resp_json)
        print(resp_json)
        if resp_json['Error'] is None:
            return resp_json['Result']['TxID'], "SUCCESS"
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256]

    def count_serial_number_prv(self, private_key, min_value=0):
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "1.0", "method": "listunspentoutputcoins",
                "params": [0, 999999, [{"PrivateKey": private_key}]
                           ],
                "id": 1}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        DEBUG(resp_json)
        # print(resp_json)
        total_serial = len(resp_json['Result']['Outputs'][private_key])
        count = 0
        for i in range(0, total_serial):
            if int(resp_json['Result']['Outputs'][private_key][i]["Value"]) >= min_value:
                count = count + 1

        if resp_json['Error'] is None:
            return total_serial, count
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256]
