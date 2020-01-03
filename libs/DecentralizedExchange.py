import json
import re

import requests

from libs.AutoLog import WARN, DEBUG, INFO


class DEX():
    def __init__(self, ip, rpc):
        self.url = "http://" + ip + ":" + str(rpc)

    def contribute_prv(self, privatekey, paymentaddress, amount_toContribute, contribution_pairID):
        headers = {'Content-Type': 'application/json'}
        data = {"id": 1, "jsonrpc": "1.0", "method": "createandsendtxwithprvcontribution",
                "params": [
                    privatekey,
                    {
                        "12RxahVABnAVCGP3LGwCn8jkQxgw7z1x14wztHzn455TTVpi1wBq9YGwkRMQg3J4e657AbAnCvYCJSdA9czBUNuCKwGSRQt55Xwz8WA": amount_toContribute
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
            return str(resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256])

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
                            "12RxahVABnAVCGP3LGwCn8jkQxgw7z1x14wztHzn455TTVpi1wBq9YGwkRMQg3J4e657AbAnCvYCJSdA9czBUNuCKwGSRQt55Xwz8WA": amount_toContribute
                        },
                        "TokenFee": 0,
                        "PDEContributionPairID": contribution_pairID,
                        "ContributorAddressStr": paymentaddress,
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
            return str(resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256])

    def trade_token(self, privatekey, paymentaddress, tokenid_toSell, amount_toSell, tokenid_toBuy,
                    minAmount_toBuy, trading_fee=0):

        total_amount = amount_toSell + trading_fee
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
                        "TokenAmount": total_amount,
                        "TokenReceivers": {
                            "12RxahVABnAVCGP3LGwCn8jkQxgw7z1x14wztHzn455TTVpi1wBq9YGwkRMQg3J4e657AbAnCvYCJSdA9czBUNuCKwGSRQt55Xwz8WA": total_amount
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
            return str(resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256])

    def trade_prv(self, privatekey, paymentaddress, amount_toSell, tokenid_toBuy, minAmount_toBuy):
        headers = {'Content-Type': 'application/json'}
        data = {"id": 1, "jsonrpc": "1.0", "method": "createandsendtxwithprvtradereq",
                "params": [
                    privatekey,
                    {
                        "12RxahVABnAVCGP3LGwCn8jkQxgw7z1x14wztHzn455TTVpi1wBq9YGwkRMQg3J4e657AbAnCvYCJSdA9czBUNuCKwGSRQt55Xwz8WA": amount_toSell
                    }, -1, -1,
                    {
                        "TokenIDToBuyStr": tokenid_toBuy,
                        "TokenIDToSellStr": "0000000000000000000000000000000000000000000000000000000000000004",
                        "SellAmount": amount_toSell,
                        "MinAcceptableAmount": minAmount_toBuy,
                        "TraderAddressStr": paymentaddress
                    }
                ]}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads()
        DEBUG(resp_json)

        if resp_json['Error'] is None:
            return resp_json['Result']['TxID']
        else:
            WARN(resp_json['Error']['Message'])
            return str(resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256])

    def withdrawal_contribution(self, privatekey, paymentaddress, tokenid1, tokenid2, amount_withdrawal):
        headers = {'Content-Type': 'application/json'}
        data = {"id": 1, "jsonrpc": "1.0", "method": "createandsendtxwithwithdrawalreq",
                "params": [
                    privatekey,
                    None, -1, 0,
                    {
                        "WithdrawerAddressStr": paymentaddress,
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
            return str(resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256])

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
                INFO("Rate of %s-%s is: %d-%d" % (
                    tokenid1[-6:], tokenid2[-6:], pair["Token1PoolValue"], pair["Token2PoolValue"]))
                return [pair["Token1PoolValue"], pair["Token2PoolValue"]]
            else:
                if re.search(pairkey2, str(resp_json['Result']['PDEPoolPairs'])):
                    pair = resp_json['Result']['PDEPoolPairs'][pairkey2]
                    INFO("Rate of %s-%s is: %d-%d" % (
                        tokenid2[-6:], tokenid1[-6:], pair["Token2PoolValue"], pair["Token1PoolValue"]))
                    return [pair["Token2PoolValue"], pair["Token1PoolValue"]]
                else:
                    WARN(pairkey + " or\n " + pairkey2 + " NOT found")
                    DEBUG(resp_json['Result']['PDEPoolPairs'])
                    return [0, 0]
        else:
            WARN(resp_json['Error']['Message'])
            return str(resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256])

    def get_pdestatus(self):
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
        return response.text, beacon_height

    def get_waitingContribution(self, tokenid, paymentaddress):
        resp_json = json.loads(self.get_pdestatus()[0])
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
            return str(resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256])

    def get_pdeshares(self, tokenid1, tokenid2, paymentaddress_list):
        pdestatus = self.get_pdestatus()
        resp_json = json.loads(pdestatus[0])
        beacon_height = pdestatus[1]
        DEBUG(resp_json)

        pde_share_list = []
        if resp_json['Error'] is None:
            for paymentaddress in paymentaddress_list:
                sharekey = "pdeshare-" + str(beacon_height) + "-" + tokenid1 + "-" + tokenid2 + "-" + paymentaddress
                sharekey2 = "pdeshare-" + str(beacon_height) + "-" + tokenid2 + "-" + tokenid1 + "-" + paymentaddress
                if re.search(sharekey, str(resp_json['Result']['PDEShares'])):
                    share = resp_json['Result']['PDEShares'][sharekey]
                    DEBUG("Share of %s-%s-%s is: %d" % (tokenid1[-6:], tokenid2[-6:], paymentaddress[-6:], share))
                    pde_share_list.append(share)
                else:
                    if re.search(sharekey2, str(resp_json['Result']['PDEShares'])):
                        share = resp_json['Result']['PDEShares'][sharekey2]
                        DEBUG("Share of %s-%s-%s is: %d" % (tokenid2[-6:], tokenid1[-6:], paymentaddress[-6:], share))
                        pde_share_list.append(share)
                    else:
                        WARN(sharekey + " or\n " + sharekey2 + " NOT found")
                        DEBUG(resp_json['Result']['PDEShares'])
                        pde_share_list.append(0)
            return pde_share_list
        else:
            WARN(resp_json['Error']['Message'])
            return str(resp_json['Error']['Message'], resp_json['Error']['StackTrace'][0:256])

    def get_contributionStatus(self, pairId):
        headers = {'Content-Type': 'application/json'}
        data = {"id": 1, "jsonrpc": "1.0", "method": "getpdecontributionstatusv2", "params": [{
            "ContributionPairID": pairId}]}
        response = requests.post(self.url, data=json.dumps(data), headers=headers)
        resp_json = json.loads(response.text)
        # DEBUG(response.text)

        if resp_json['Error'] is None:
            status_code = resp_json['Result']['Status']
            if status_code == 4:
                return resp_json['Result']['TokenID1Str'], resp_json['Result']['Contributed1Amount'], \
                       resp_json['Result']['Returned1Amount'], \
                       resp_json['Result']['TokenID2Str'], resp_json['Result']['Contributed2Amount'], \
                       resp_json['Result']['Returned2Amount']
            else:
                return "TODOS"
        else:
            WARN(resp_json['Error']['Message'])
            return resp_json['Error']['Message']
