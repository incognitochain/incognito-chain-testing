from Drivers.Response import ResponseExtractor
from Helpers.Logging import config_logger
from Helpers.TestHelper import l6
from Objects import BlockChainInfoBaseClass

logger = config_logger(__name__)


class CoinInfoPublic(BlockChainInfoBaseClass):
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
            return self.dict_data["ID"]
        except KeyError:
            pass
        try:
            return self.dict_data["TokenID"]
        except KeyError:
            pass
        return self.dict_data["tokenId"]

    def get_network(self):
        return self.dict_data['network']

    def get_external_token_id(self):
        return self.dict_data['externalTokenId']

    def is_centralized(self):
        return self.dict_data['isCentralized']

    def get_token_name(self):
        return self.dict_data["Name"]

    def get_token_symbol(self):
        return self.dict_data["Symbol"]

    def get_token_image(self):
        return self.dict_data["Image"]

    def get_token_amount(self):
        try:
            return self.dict_data["Amount"]
        except KeyError:
            pass
        try:
            return self.dict_data["amount"]
        except KeyError:
            pass
        return 0

    def is_privacy(self):
        return self.dict_data["IsPrivacy"]

    def is_bridge_token(self):
        return self.dict_data["IsBridgeToken"]

    def get_list_txs(self):
        return self.dict_data["ListTxs"]

    def get_txs_count(self):
        return self.dict_data["CountTxs"]

    def get_initiator_pub_k(self):
        return self.dict_data["InitiatorPublicKey"]

    def get_tx_info(self):
        return self.dict_data["TxInfo"]


class BaseListTokenPublicInfo(ResponseExtractor):
    def __contains__(self, token):
        try:
            token_id = token.get_token_id()  # if 'token' is 'InChainPtokenInfo'
        except (AttributeError, TypeError):
            token_id = token
        return token_id in [info.get_token_id() for info in self.info_obj_list]

    def get_token_id_by_name(self, name) -> CoinInfoPublic:
        for token_inf in self.info_obj_list:
            if token_inf.get_token_name() == name:
                return token_inf.get_token_id()

    def get_info_by_token_id(self, token_id) -> CoinInfoPublic:
        for tok_info in self.info_obj_list:
            if tok_info.get_token_id() == token_id:
                return tok_info


class ListInChainToken(BaseListTokenPublicInfo):
    def __init__(self, response):
        """
        @param response: Response object
        from "listprivacycustomtoken" RPC
        """
        super().__init__(response)
        self._extract_dict_info_obj(response, 'ListCustomToken', CoinInfoPublic)


class ListOwnedToken(BaseListTokenPublicInfo):
    """
    from  "getlistprivacycustomtokenbalance" RPC
    """

    def __init__(self, response):
        super().__init__(response)
        self._extract_dict_info_obj(response, 'ListCustomTokenBalance', CoinInfoPublic)


class ListInChainBridgeToken(BaseListTokenPublicInfo):
    def __init__(self, response):
        super().__init__(response)
        self._extract_dict_info_obj(response, None, CoinInfoPublic)


# -----------------------------------------------------------------------#

class TxOutPut(BlockChainInfoBaseClass):
    """
    sample: coin v1
        {
            "PublicKey": "1oQKfimdKiDzfhD5qLA1L2AJbemf98ptG2fBvefjdZSnQvN53j",
            "CoinCommitment": "1Q6fdoVgt41ghd4nZfWnEHjqiArFwTdcSbwEAsPZSNj1q7Cgbj",
            "SNDerivator": "1dBfNj4W8rp9VCaa1uXEuF8tGySA5vDdt6qPzSiaZ7d8J61ZC3",
            "SerialNumber": "12goiYnQ9Xp98nVrKFUSSxNy3x2acoRnBviacMjCo57ZeLtkkaZ",
            "Randomness": "12oodDDkWsR1BAFHYz3sx1mAaEjdPcFabmE5pTHheyUbCxawh4G",
            "Value": "1000",
            "Info": "13PMpZ4",
            "CoinDetailsEncrypted": "13PMpZ4"
        }
        or coin v2
        {
            "Version": "2",
            "Index": "",
            "PublicKey": "1E3f9obsu5KGRuvCU9CSsv7eDQwdp2J4osevYvJ6RBzDWGFFY2",
            "Commitment": "1Xm5xT9eCYYXXSHJD94oaq2w5yh3s2zUC2MWKR1kQnA59nk5xz",
            "SNDerivator": "",
            "KeyImage": "12FMyCuxYkZWWbCNnUP2sdAx63oRbuzLtXx7dv9q9ZcJczdSBSg",
            "Randomness": "12fFPJsmqmFcKiiKJzeSkCV1xSbvTdwQZqzLSSWjhoD5KmouVRP",
            "Value": "1004",
            "Info": ""
        },
    """

    def __str__(self):
        serial_num = l6(str(self.get_serial_num()))
        k_image = l6(str(self.get_key_image()))
        ver = f'v{self.get_version()}'
        value = self.get_value()
        return "%6s : %6s : %2s : %s" % (serial_num, k_image, ver, value)

    def __add__(self, other):
        if type(other) is TxOutPut:
            x = other.get_value()
        else:
            try:
                x = int(other)
            except ValueError:
                x = 0
        return self.get_value() + x

    def __radd__(self, other):
        return self.get_value() + int(other)

    def get_index(self):
        try:  # new
            return self.dict_data['Index']
        except KeyError:  # old coin has no index
            return None

    def get_public_key(self):
        return self.dict_data['PublicKey']

    def get_commitment(self):
        try:
            return self.dict_data['CoinCommitment']
        except KeyError:
            return self.dict_data['Commitment']

    def get_serial_num(self):
        try:  # old
            return self.dict_data['SerialNumber']
        except:  # new coin's SN is now key image
            return None

    def get_serial_num_derivator(self):
        return self.dict_data['SNDerivator']

    def get_randomness(self):
        return self.dict_data['Randomness']

    def get_value(self):
        return int(self.dict_data['Value'])

    def get_info(self):
        return self.dict_data['Info']

    def get_detail_encrypted(self):
        try:  # old
            return self.dict_data['CoinDetailsEncrypted']
        except KeyError:  # new
            return None

    def get_key_image(self):
        try:  # new
            return self.dict_data['KeyImage']
        except KeyError:  # old
            return None

    def get_version(self):
        try:
            return int(self.dict_data['Version'])
        except KeyError:
            logger.debug('Error while get coin version. Assume ver=1')
            return 1


class BaseListTxOutput(ResponseExtractor):
    def __len__(self):
        return len(self.info_obj_list)

    def __contains__(self, token):
        try:
            token_id = token.get_token_id()  # if 'token' is 'InChainPtokenInfo'
        except (AttributeError, TypeError):
            token_id = token
        return token_id in [info.get_token_id() for info in self.info_obj_list]

    def find_txo_with_value(self, value):
        """
        @param value:
        @return: a TxOutPut or list of TxOutPut if found any TxOutPut which has value
        """
        result = []
        for txo in self.info_obj_list:
            txo: TxOutPut
            if txo.get_value() == value:
                result.append(txo)
        if len(result) == 1:
            return result[0]
        return result


class ListPrvTXO(BaseListTxOutput):
    def __init__(self, response):
        super().__init__(response)
        # list of PRV UTXO response is a dict of {private key: [list of UTXO]}, this is a bit redundant,
        # (it should be [list of UTXO] only). Thus, cannot use _extract_dict_info_obj method here
        all_value = response.get_result('Outputs').values()
        if len(all_value) == 0:
            return
        raw_data = list(all_value)[0]
        for datum in raw_data:
            self.info_obj_list.append(TxOutPut(datum))
