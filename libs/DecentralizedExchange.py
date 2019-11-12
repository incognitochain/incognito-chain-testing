import json

import requests, re

from libs.AutoLog import WARN, DEBUG


class DEX():
    def __init__(self, ip, rpc):
        self.url = "http://" + ip + ":" + str(rpc)

    def contribute_prv(self, privatekey, paymentaddress, amount_toContribute, contribution_pairID):
        headers = {'Content-Type': 'application/json'}
        data = {"id": 1, "jsonrpc": "1.0", "method": "createandsendtxwithprvcontribution",
                "params": [
                    privatekey,
                    {
                        "15pABFiJVeh9D5uiQEhQX4SVibGGbdAVipQxBdxkmDqAJaoG1EdFKHBrNfs": amount_toContribute
                    },
                    100, -1,
                    {
                        "PDEContributionPairID": contribution_pairID,
                        "ContributorAddressStr":
                            paymentaddress,
                        "ContributedAmount": amount_toContribute,
                        "TokenIDStr": "0000000000000000000000000000000000000000000000000000000000000004"
                    }
                ]}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        DEBUG(response.text)
        resp_json = json.loads(response.text)

        if resp_json['Error'] is None:
            return resp_json['Result']['TxID']
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message']

    def contribute_token(self, privatekey, paymentaddress, tokenid_toContribute, amount_toContribute,
                         contribution_pairID):
        headers = {'Content-Type': 'application/json'}
        data = {"id": 1, "jsonrpc": "1.0", "method": "createandsendtxwithptokencontribution",
                "params": [
                    privatekey,
                    None, 100, -1,
                    {
                        "Privacy": True,
                        "TokenID": tokenid_toContribute,
                        "TokenTxType": 1,
                        "TokenName": "",
                        "TokenSymbol": "",
                        "TokenAmount": amount_toContribute,
                        "TokenReceivers": {
                            "15pABFiJVeh9D5uiQEhQX4SVibGGbdAVipQxBdxkmDqAJaoG1EdFKHBrNfs": amount_toContribute
                        },
                        "TokenFee": 0,
                        "PDEContributionPairID": contribution_pairID,
                        "ContributorAddressStr":
                            paymentaddress,
                        "ContributedAmount": amount_toContribute,
                        "TokenIDStr": tokenid_toContribute
                    },
                    "", 0
                ]}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        DEBUG(response.text)
        resp_json = json.loads(response.text)

        if resp_json['Error'] is None:
            return resp_json['Result']['TxID']
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message']

    def trade_token(self, privatekey, paymentaddress, tokenid_toSell, amount_toSell, tokenid_toBuy,
                    minAmount_toBuy, trading_fee = 0):
        headers = {'Content-Type': 'application/json'}
        data = {"id": 1, "jsonrpc": "1.0", "method": "createandsendtxwithptokentradereq",
                "params": [
                    privatekey,
                    None,
                    2,
                    -1,
                    {
                        "Privacy": True,
                        "TokenID": tokenid_toSell,
                        "TokenTxType": 1,
                        "TokenName": "",
                        "TokenSymbol": "",
                        "TokenAmount": amount_toSell,
                        "TokenReceivers": {
                            "15pABFiJVeh9D5uiQEhQX4SVibGGbdAVipQxBdxkmDqAJaoG1EdFKHBrNfs": amount_toSell
                        },
                        "TokenFee": 0,

                        "TokenIDToBuyStr": tokenid_toBuy,
                        "TokenIDToSellStr": tokenid_toSell,
                        "SellAmount": amount_toSell,
                        "MinAcceptableAmount": minAmount_toBuy,
                        "TradingFee": trading_fee,
                        "TraderAddressStr":
                            paymentaddress
                    },
                    "",
                    0
                ]}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        # DEBUG(response.text)
        resp_json = json.loads(response.text)
        DEBUG(resp_json)

        if resp_json['Error'] is None:
            return resp_json['Result']['TxID']
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message']

    def trade_prv(self, privatekey, paymentaddress, amount_toSell, tokenid_toBuy, minAmount_toBuy):
        headers = {'Content-Type': 'application/json'}
        data = {"id": 1, "jsonrpc": "1.0", "method": "createandsendtxwithprvtradereq",
                "params": [
                    privatekey,
                    {
                        "15pABFiJVeh9D5uiQEhQX4SVibGGbdAVipQxBdxkmDqAJaoG1EdFKHBrNfs": amount_toSell
                    },
                    5,
                    -1,
                    {
                        "TokenIDToBuyStr": tokenid_toBuy,
                        "TokenIDToSellStr": "0000000000000000000000000000000000000000000000000000000000000004",
                        "SellAmount": amount_toSell,
                        "MinAcceptableAmount": minAmount_toBuy,
                        "TraderAddressStr":
                            paymentaddress
                    }
                ]}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads()
        DEBUG(resp_json)

        if resp_json['Error'] is None:
            return resp_json['Result']['TxID']
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message']

    def withdrawal_contribution(self, privatekey, paymentaddress, amount_toSell, tokenid1, tokenid2,
                                amount_withdrawal=25000000000000):
        headers = {'Content-Type': 'application/json'}
        data = {"id": 1, "jsonrpc": "1.0", "method": "createandsendtxwithwithdrawalreq",
                "params": [
                    privatekey,
                    {
                        "15pABFiJVeh9D5uiQEhQX4SVibGGbdAVipQxBdxkmDqAJaoG1EdFKHBrNfs": 0
                    },
                    5,
                    -1,
                    {
                        "WithdrawerAddressStr":
                            paymentaddress,
                        "WithdrawalToken1IDStr": tokenid1,

                        "WithdrawalToken2IDStr": tokenid2,
                        "WithdrawalShareAmt": amount_withdrawal
                    }
                ]}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        DEBUG(response.text)

        if resp_json['Error'] is None:
            return resp_json['Result']['TxID']
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message']

    def get_latestRate(self, tokenid1, tokenid2):
        headers = {'Content-Type': 'application/json'}
        data = {"id": 1, "jsonrpc": "1.0", "method": "getbeaconbeststate", "params": []}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        # DEBUG(response.text)

        if resp_json['Error'] is None:
            beacon_height = resp_json['Result']['BeaconHeight']
            DEBUG("beacon_height: " + str(beacon_height))
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message']
        # get rate according to beacon height
        pairkey = "pdepool-" + str(beacon_height) + "-" + tokenid1 + "-" + tokenid2
        pairkey2 = "pdepool-" + str(beacon_height) + "-" + tokenid2 + "-" + tokenid1

        data = {"id": 1, "jsonrpc": "1.0", "method": "getpdestate",
                "params": [{"BeaconHeight": beacon_height}]}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        # DEBUG(response.text)
        DEBUG(resp_json)

        if resp_json['Error'] is None:
            if re.search(pairkey, str(resp_json['Result']['PDEPoolPairs'])):
                pair = resp_json['Result']['PDEPoolPairs'][pairkey]
                return [pair["Token1PoolValue"], pair["Token2PoolValue"]]
            else:
                if re.search(pairkey2, str(resp_json['Result']['PDEPoolPairs'])):
                    pair = resp_json['Result']['PDEPoolPairs'][pairkey2]
                    return [pair["Token2PoolValue"], pair["Token1PoolValue"]]
                else:
                    WARN(pairkey + " or " + pairkey2 + " NOT found")
                    DEBUG(resp_json['Result']['PDEPoolPairs'])
                    return False
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message']

    def get_waitingContribution(self, tokenid, paymentaddress):
        headers = {'Content-Type': 'application/json'}
        data = {"id": 1, "jsonrpc": "1.0", "method": "getbeaconbeststate", "params": []}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        # DEBUG(response.text)

        if resp_json['Error'] is None:
            beacon_height = resp_json['Result']['BeaconHeight']
            DEBUG("beacon_height: " + str(beacon_height))
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message']
        # get WaitingPDEContributions according to beacon height
        data = {"id": 1, "jsonrpc": "1.0", "method": "getpdestate",
                "params": [{"BeaconHeight": beacon_height}]}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        # DEBUG(response.text)
        DEBUG(resp_json)

        if resp_json['Error'] is None:
            waiting_contributions = str(resp_json['Result']['WaitingPDEContributions'])
            waiting_contributionList = waiting_contributions.split("waitingpdecontribution")

            for contribution in waiting_contributionList:
                if re.search(tokenid, str(contribution)):
                    if re.search(paymentaddress, str(contribution)):
                        DEBUG("Found the waiting tokenid here: " + str(contribution))
                        return True
            WARN("payment address and tokenid NOT found")
            return False
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message']
