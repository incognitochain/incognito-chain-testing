import json
from abc import ABC


class BlockChainInfoBaseClass(ABC):
    def __init__(self, dict_data=None):
        self.data: dict = dict_data
        self.err = None

    def __eq__(self, other):
        return self.data == other.data

    def __ne__(self, other):
        return self.data != other.data

    def is_none(self):
        return bool(self.data)

    def pretty_format(self):
        return json.dumps(self.data, indent=3)

    def pretty_print(self):
        print(self.pretty_format())

    def __str__(self):
        return self.pretty_format()


class InChainPtokenInfo(BlockChainInfoBaseClass):
    """
        from "listprivacycustomtoken" RPC
            {
                "ID": "64f1539586983b9799d4819874e2635174c227c572f1fbf3649819c770f30e27",
                "Name": "030221153617_030221153617",
                "Symbol": "030221153617",
                "Image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAaQAAAGkAQMAAABEgsN2AAAABlBMVEXw8PDQ9UWcU3P7AAAAn0lEQVR4nOzYMQ7CIBjHUZw8hkfVo3oMp9YIC+QLCUFIl/ebaP95nUmTJEna1eP89cnn2xlqhhdFURRFURRFbVLdKIqiKIqiKGqD6o5Dn6MoiqIoiqKoeVXG0lFePfPDO5/v1RzuvRRFURRFURT1j0rVeKRQd6AoiqIoiqKoNUqSJEm6quaiGv+mjtx7KYqiKIqiKGpKSZKkZX0DAAD//xJ/A8gpbqRrAAAAAElFTkSuQmCC",
                "Amount": 1000000000000000,
                "IsPrivacy": true,
                "IsBridgeToken": false,
                "ListTxs": [],
                "CountTxs": 0,
                "InitiatorPublicKey": "",
                "TxInfo": "13PMpZ4"
            },
        or from  "getlistprivacycustomtokenbalance" RPC
              {
                "Name": "random_u1xvsGI5",
                "Symbol": "random_MFqCPTF",
                "Amount": 1000000000000000,
                "TokenID": "4485851541abe8ab41bd6d4e7eb714407652322aae830f689a41c4101cf4c3b9",
                "TokenImage": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAaQAAAGkAQMAAABEgsN2AAAABlBMVEXw8PCrAvbNYmEGAAAAm0lEQVR4nOzasQ3CMBBAUbtiDEaFURmDyiDdURhhlCJOpETvV3YuL/UVKZIkaY/qK7rH5RrnJ0VRFEVRFEVtpXKYtXx0i8sjzpdu/PkcRVEURVEURc1RpRv+Va0MoyiKoiiKoqg1qt9glxrvvRRFURRFURRFURRFURRFUUdU+TNp/X3xa0BRFEVRFEVRM5UkSZIkSZJO0jsAAP//RFMyQtu4rQAAAAAASUVORK5CYII=",
                "IsPrivacy": true,
                "IsBridgeToken": false
             }
        or from "getallbridgetokens"
            {
                "tokenId": "0000000000000000000000000000000000000000000000000000020421161225",
                "amount": 20421161225,
                "externalTokenId": null,
                "network": "",
                "isCentralized": true
            },
    """

    def __str__(self):
        return f'{self.get_token_name()} | {self.get_token_id()} | {self.get_token_amount()}'

    def get_token_id(self):
        try:
            return self.data["ID"]
        except KeyError:
            pass
        try:
            return self.data["TokenID"]
        except KeyError:
            pass
        return self.data["tokenId"]

    def get_network(self):
        return self.data['network']

    def get_external_token_id(self):
        return self.data['externalTokenId']

    def is_centralized(self):
        return self.data['isCentralized']

    def get_token_name(self):
        return self.data["Name"]

    def get_token_symbol(self):
        return self.data["Symbol"]

    def get_token_image(self):
        return self.data["Image"]

    def get_token_amount(self):
        try:
            return self.data["Amount"]
        except KeyError:
            pass
        try:
            return self.data["amount"]
        except KeyError:
            pass
        return 0

    def is_privacy(self):
        return self.data["IsPrivacy"]

    def is_bridge_token(self):
        return self.data["IsBridgeToken"]

    def get_list_txs(self):
        return self.data["ListTxs"]

    def get_txs_count(self):
        return self.data["CountTxs"]

    def get_initiator_pub_k(self):
        return self.data["InitiatorPublicKey"]

    def get_tx_info(self):
        return self.data["TxInfo"]


class TokenListInfoBase(ABC):
    def __init__(self, response):
        from Drivers.Response import Response
        if type(response) is not Response:
            raise TypeError(f'Input must be a Drivers.Response.Response, not {type(response)}')

    def __len__(self):
        return len(self.tok_info_obj_list)

    def __iter__(self):
        self.__current_index = 0
        return iter(self.tok_info_obj_list)

    def __next__(self):
        if self.__current_index >= len(self.tok_info_obj_list):
            raise StopIteration
        else:
            self.__current_index += 1
            return self[self.__current_index]

    def __getitem__(self, item):
        return self.tok_info_obj_list[item]

    def __contains__(self, token):
        try:
            token_id = token.get_token_id()  # if 'token' is 'InChainPtokenInfo'
        except (AttributeError, TypeError):
            token_id = token
        return token_id in [info.get_token_id() for info in self.tok_info_obj_list]

    def get_token_id_by_name(self, name) -> InChainPtokenInfo:
        for token_inf in self.tok_info_obj_list:
            if token_inf.get_token_name() == name:
                return token_inf.get_token_id()

    def get_info_by_token_id(self, token_id) -> InChainPtokenInfo:
        for tok_info in self.tok_info_obj_list:
            if tok_info.get_token_id() == token_id:
                return tok_info
