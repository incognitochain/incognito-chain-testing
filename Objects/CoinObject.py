from typing import Union, List

from Drivers.Response import RPCResponseBase
from Helpers.Logging import config_logger
from Helpers.TestHelper import l6
from Objects import BlockChainInfoBaseClass

logger = config_logger(__name__)


class CoinInfoPublic(BlockChainInfoBaseClass):
    """
        from "listprivacycustomtoken" RPC
        or "getlistprivacycustomtokenbalance" RPC
        or "getallbridgetokens"
    """

    def __str__(self):
        return f'{self.get_token_name()} | {self.get_token_id()} | {self.get_token_amount()}'

    def get_token_id(self):
        return self.dict_data.get("ID", self.dict_data.get("TokenID", self.dict_data.get("tokenId")))

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

    def get_public_key_base64(self):
        return self.dict_data['PublicKeyBase64']

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


class ListCoinResponseBase(RPCResponseBase):
    def _get_all_tokens_info(self):
        raise RuntimeError("This method must be override by sub class")

    def get_tokens_info(self, **by) -> Union[CoinInfoPublic, List[CoinInfoPublic], None]:
        by_name = by.get("name", "").lower()
        by_id = by.get("id")
        by_symbol = by.get("symbol", "").lower()
        by_bal = by.get("balance")
        all_token_info = self._get_all_tokens_info()
        if by_id:
            for obj in all_token_info:
                if obj.get_token_id() == by_id:
                    return obj
            return None

        filtered_result = []
        for obj in all_token_info:
            included = True
            included = included and by_name in obj.get_token_name().lower() if by_name else included
            included = included and by_symbol in obj.get_token_symbol().lower() if by_symbol else included
            included = included and obj.get_vaue() == by_bal if by_bal else included
            filtered_result.append(obj) if included else None
        return filtered_result


class CustomTokenBalanceResponse(ListCoinResponseBase):
    def _get_all_tokens_info(self):
        try:
            return [CoinInfoPublic(data) for data in self.get_result("ListCustomTokenBalance")]
        except TypeError:
            return []


class BridgeTokenResponse(ListCoinResponseBase):
    def _get_all_tokens_info(self):
        return [CoinInfoPublic(data) for data in self.get_result()]


class InChainTokenResponse(ListCoinResponseBase):
    def _get_all_tokens_info(self):
        return [CoinInfoPublic(data) for data in self.get_result("ListCustomToken")]


class TXOResponse(RPCResponseBase):
    def get_coins(self, **by):
        try:
            key = list(self.get_result("Outputs").keys())[0]
        except IndexError:
            logger.error("No coin data in response")
            return []
        return [TxOutPut(data) for data in self.get_result("Outputs")[key]]
