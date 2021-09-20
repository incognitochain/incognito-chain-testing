import json

from Configs.Configs import ChainConfig
from Helpers.Logging import INFO
from Objects import BlockChainInfoBaseClass


class TransactionDetail(BlockChainInfoBaseClass):
    """
    {
       "Id": 1,
       "Result": {
          "BlockHash": "1d7dda02a4b06aa6d333a8485963edbb25b0f42a4f627f993be75d6f405b7243",
          "BlockHeight": 25043,
          "TxSize": 2,
          "Index": 0,
          "ShardID": 0,
          "Hash": "4221c12eca87d7a6be99f70124a02c0eb9ad5e33d04a4ac10e2bf3c0a7bc4f25",
          "Version": 2,
          "Type": "n",
          "LockTime": "2020-07-20T02:38:30",
          "Fee": 2,
          "Image": "",
          "IsPrivacy": true,
          "Proof": "AgAAAuIB/n5tQJI+s1nCbdAqwZ2xOxkNW1X3TC0QiFlAZZkR3gSFf5IR6fTmhS+9sQaGgOEhS5TRtZ1y4+EHmz1IyHNYPqETz0LvWoeQS1UHpAv0NMbwSHx70PIa52PgvcUMhHBjeQSMGvzmoVgJNfP7MlLhS/OZr0Ye7OdkxqG06nuZIooMAlBLkUWIcMnNUry1Mdd3IF+2sRYD5MB4IqLVw/f1FPyIcnF/iTWT+Wjkvcpm83iP7K0rYtCKxdMCDO0gWrMOYMLVA3hUrjx3xHxehnOUpHJzDdx2T5OBUCWERvcX6Qp+YrOI/Yuxnc+c1BmBNKwSHXcQlr5pTDRO6D9vhpY2DgamUS+ZCaMxPmYBTaQlXC8pshwsSDHOG9P+uAUhWKxyzdM1mVlD6taZvl9Z85CB/iSmngzGr9EUkF/LycM1kg9PbGu0ymt/NM7503jFO6zF5c7Rq3KA71mMQ9Hz1OfsludPEOOacHx8vd4/a0L2CgqzTscmpe+gY8Lc6nlMW6kNbl3PhLts1brmlx4xJmHUhQnmLzl93QwTy5s/ie9AbLhD1Df+tS0MTgPa9LKdQXf2POOSDFlHGsxfk8Do+UN4d0uM47GVFDUw6Pn+s/Dci6wIRbqxKj/gp6CGKenYe0rlnXCKgXr/nX71Rl4adaZL9mww4OCG/M9JFW1zWDaiJtbxtqWrTX4TbTPTKJbdMkBraOSN2TFGJZtk1sC80mKdGO3gHItdnBICqEA8/oYMohZvVO+kyoHsKUWj4klwe2GgguDr7jovhDd5JZBydvmM8vl4ATIJBC7cNaLKRULenfVIjyltX51OSNIkqTIhpCP8FmJcoBJ0Ar9KUHfI+zDxIcplnssyX4x1KGptmoS7JZwksLrhdcuTlLzCsXr4+Y9BAGH1n0GzN/pkUOdqzMn35OeOh0vi+SeNUV7IrqtEVvkATaK/NJvK6J0cmVyJvBHuaMlAe7QMI9mWJaXunsPzehoBbQIAAAAg4vP7OESgDVRLZ/qmPdjgZ673TlWwAEWrx7l16934rH8AJAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABrQIAIJqHvleuvBCPCcxWC6WBcz/OBfLaVuKQf4SVFMxzjFGwIP5+bUCSPrNZwm3QKsGdsTsZDVtV90wtEIhZQGWZEd4EAAAkw/6DgEMe+y4zk7IDCAY0frH/KJrEPpziMTH1oW2YS6sAAAAFIL0osprZaKRMqQgEBaOSMyFeiE0Df42KjfkfUdfBJZwAID5FR+iK9OqmmyZq8sVSt3CLDdnNxMFAZIVq8qnBzT0L",
          "ProofDetail": {
             "InputCoins": [
                {
                   "Version": 2,
                   "Index": 0,
                   "Info": "",
                   "PublicKey": "",
                   "Commitment": "",
                   "KeyImage": "12ixDFBREXGjwtaqmRaExk5HEapxkZanxmq6jQSP3tki8FeMwus",
                   "TxRandom": "",
                   "Value": "0",
                   "Randomness": ""
                }
             ],
             "OutputCoins": [
                {
                   "Version": 2,
                   "Index": 5,
                   "Info": "",
                   "PublicKey": "12B4GXqXfE8218PEPYnVvNz5DktJpNYUBwkSb5F47AJJq4oaWu1",
                   "Commitment": "12w5hq5fAkigt61KgXjjZfwNNe7XUTHhC3egACTb55mnwZLGVFQ",
                   "KeyImage": "",
                   "TxRandom": "12VKQhea3VZ96UdvB3CDncACqZsFFtmxJeVfBy6kLFSpyN3XwqV",
                   "Value": "0",
                   "Randomness": "12SJp74NVqK6RZT6fn2kZxZz1RJnYpkyPfGiXDG7M1xmheweLmf"
                }
             ]
          },
          "InputCoinPubKey": "",
          "SigPubKey": "{\"Indexes\":[[110]]}",
          "Sig": "13PYJL4VmJe49Bfpqt4xChMp4DhiJYpvjGmRb7jdsP43kZjFEEUcYHzjQ7CiMKDBaSkR6SYRsNALjA8ceG9XVjW4Nntb5N3kvjYNCoHPd4T2RzDLKn9hrvGbPph212vuuPK8b71iiqWzsXhd",
          "Metadata": "{\n\t\"Type\": 110,\n\t\"Sig\": \"AcLFNWLVx1No4qJyQWQN62GXf9Y/3LpADH9Lv11Y4QI63o36INV0khOwz2q6nCTtzKBeDUGH6vR3ssbTHwFeAg==\",\n\t\"PaymentAddress\": \"12Rw9oesEgd8t5NGrfqxtWTCzh1eDif55miqZ1kFzj5zeQ6UQnNB9JXRn5Vc5QVbBaiFhoYdYPnQZ5tWwcBpse5EJXM3Av6qEV2wspv\",\n\t\"Amount\": 5000000000\n}",
          "CustomTokenData": "",
          "PrivacyCustomTokenID": "",
          "PrivacyCustomTokenName": "",
          "PrivacyCustomTokenSymbol": "",
          "PrivacyCustomTokenData": "",
          "PrivacyCustomTokenProofDetail": {
            "InputCoins": [
               {
                  "CoinDetails": {
                     "PublicKey": "1Hc7AkzLe7kHPZY3Ee7MMF6PuSGMTixqJCfki63H84QxhuWQTG",
                     "CoinCommitment": "1E9oX8UkmLivs2mAwRqVESDzfJMz5df9dJMKkyPJD1U353Y96b",
                     "SNDerivator": {},
                     "SerialNumber": "1XVe8nmnFshHP65Pvmq1GXRzLGD6cEPPjU5yWsH8rRMMLXLFGR",
                     "Randomness": {},
                     "Value": 979999997187620,
                     "Info": "13PMpZ4"
                  },
                  "CoinDetailsEncrypted": ""
               }
            ],
            "OutputCoins": [
               {
                  "CoinDetails": {
                     "PublicKey": "123vyG7GycRNSdNTxwUyUKE1jjGxWL77KhXMcoYvAKSYsr3Ff69",
                     "CoinCommitment": "12bZV7NkjKgiR8m2Si1uJ8jgvmQFqZdiAWRPKec7HbxZ6YcuF3z",
                     "SNDerivator": {},
                     "SerialNumber": "",
                     "Randomness": {},
                     "Value": 1238,
                     "Info": "13PMpZ4"
                  },
                  "CoinDetailsEncrypted": ""
               },
               {
                  "CoinDetails": {
                     "PublicKey": "1Hc7AkzLe7kHPZY3Ee7MMF6PuSGMTixqJCfki63H84QxhuWQTG",
                     "CoinCommitment": "1xGvUFogBA5gbKarRDBRsWoZ5vDSPB7G868n3oXT3tSnpBJr9t",
                     "SNDerivator": {},
                     "SerialNumber": "",
                     "Randomness": {},
                     "Value": 979999995786382,
                     "Info": "13PMpZ4"
                  },
                  "CoinDetailsEncrypted": ""
               }
            ]
          },
          "PrivacyCustomTokenIsPrivacy": false,
          "PrivacyCustomTokenFee": 0,
          "IsInMempool": false,
          "IsInBlock": true,
          "Info": ""
       },
       "Error": null,
       "Params": [
          "4221c12eca87d7a6be99f70124a02c0eb9ad5e33d04a4ac10e2bf3c0a7bc4f25"
       ],
       "Method": "gettransactionbyhash",
       "Jsonrpc": "1.0"
    }
    """

    class TxDetailProof(BlockChainInfoBaseClass):
        def _get_coin_list(self, coin_list_name):
            """

            @param coin_list_name: "InputCoins" or "OutputCoins"
            @return:
            """
            from Objects.CoinObject import TxOutPut
            raw_coins = self.dict_data[coin_list_name]
            list_coin_obj = []
            for raw in raw_coins:
                try:
                    coin_obj = TxOutPut(raw['CoinDetails'])
                except KeyError:
                    coin_obj = TxOutPut(raw)
                try:
                    coin_obj.dict_data['CoinDetailsEncrypted'] = raw['CoinDetailsEncrypted']
                except KeyError:
                    pass
                list_coin_obj.append(coin_obj)
            return list_coin_obj

        def get_input_coins(self):
            return self._get_coin_list('InputCoins')

        def get_output_coins(self):
            return self._get_coin_list('OutputCoins')

        def check_proof_privacy(self):
            input_coins = self.get_input_coins()
            for coin in input_coins:
                key = coin.get_public_key()
                value = coin.get_value()
                INFO(f'Coin {key} value = {value}')
                if value != 0:
                    return False

            return True

    class MetaData(BlockChainInfoBaseClass):
        """
        example:
        {\n\t\"Type\": 110,\n\t\"Sig\": \"AcLFNWLVx1No4qJyQWQN62GXf9Y/3LpADH9Lv11Y4QI63o36INV0khOwz2q6nCTtzKBeDUGH6vR3ssbTHwFeAg==\",\n\t\"PaymentAddress\": \"12Rw9oesEgd8t5NGrfqxtWTCzh1eDif55miqZ1kFzj5zeQ6UQnNB9JXRn5Vc5QVbBaiFhoYdYPnQZ5tWwcBpse5EJXM3Av6qEV2wspv\",\n\t\"Amount\": 5000000000\n}
        """

        def __init__(self, raw_data):
            super().__init__(raw_data)
            self.dict_data = json.loads(self.dict_data)

        def get_type(self):
            return self.dict_data['Type']

        def get_sig(self):
            return self.dict_data['Sig']

        def get_payment_address(self):
            return self.dict_data['PaymentAddress']

        def get_payment_address_reward_receiver(self):
            return self.dict_data["RewardReceiverPaymentAddress"]

        def get_funder_payment_address(self):
            return self.dict_data["FunderPaymentAddress"]

        def get_amount(self):
            return self.dict_data['Amount']

    def get_block_hash(self):
        return self.dict_data['BlockHash']

    def get_block_height(self):
        return self.dict_data['BlockHeight']

    def get_tx_size(self):
        return self.dict_data['TxSize']

    def get_index(self):
        return self.dict_data['Index']

    def get_shard_id(self):
        return self.dict_data['ShardID']

    def get_hash(self):
        return self.dict_data['Hash']

    def get_version(self):
        return self.dict_data['Version']

    def get_type(self):
        return self.dict_data['Type']

    def get_lock_time(self):
        return self.dict_data['LockTime']

    def get_fee(self):
        return self.dict_data['Fee']

    def get_image(self):
        return self.dict_data['Image']

    def is_privacy(self):
        return self.dict_data['IsPrivacy']

    def get_proof(self):
        return self.dict_data['Proof']

    def get_prv_proof_detail(self):
        """
        prv proof
        :return:
        """
        return TransactionDetail.TxDetailProof(self.dict_data['ProofDetail'])

    def get_input_coin_pub_key(self):
        return self.dict_data['InputCoinPubKey']

    def get_sig_pub_key(self):
        return self.dict_data['SigPubKey']

    def get_sig(self):
        return self.dict_data['Sig']

    def get_meta_data(self):
        return TransactionDetail.MetaData(self.dict_data['Metadata'])

    def get_custom_token_data(self):
        return self.dict_data['CustomTokenData']

    def get_privacy_custom_token_id(self):
        return self.dict_data['PrivacyCustomTokenID']

    def get_privacy_custom_token_name(self):
        return self.dict_data['PrivacyCustomTokenName']

    def get_privacy_custom_token_symbol(self):
        return self.dict_data['PrivacyCustomTokenSymbol']

    def get_privacy_custom_token_data(self):
        return self.dict_data['PrivacyCustomTokenData']

    def get_privacy_custom_token_proof_detail(self):
        """
        :return:
        """
        return TransactionDetail.TxDetailProof(self.dict_data['PrivacyCustomTokenProofDetail'])

    def is_privacy_custom_token(self):
        return self.dict_data['PrivacyCustomTokenIsPrivacy']

    def get_privacy_custom_token_fee(self):
        return self.dict_data['PrivacyCustomTokenFee']

    def is_in_mem_pool(self):
        in_mem_pool = True if self.dict_data["IsInMempool"] == 'true' else False
        return in_mem_pool

    def is_in_block(self):
        in_block = True if self.dict_data["IsInBlock"] == 'true' else False
        return in_block

    def get_info(self):
        return self.dict_data['Info']

    def get_tx_id(self):
        try:
            return self.dict_data['TxID']
        except KeyError:
            return self.get_hash()

    def get_transaction_by_hash(self, tx_hash=None):
        if tx_hash is None:
            tx_hash = self.get_tx_id()
        from Objects.IncognitoTestCase import SUT
        self.dict_data = SUT().transaction().get_tx_by_hash(tx_hash).get_result()
        return self

    def __verify_privacy(self, privacy_flag, detail_proof, expected_privacy=True):
        version = ChainConfig.PRIVACY_VERSION
        privacy = privacy_flag and detail_proof.check_proof_privacy()
        if version == 2:
            INFO(f'In v2, privacy must always be true no mater the hell you want')
            assert privacy, f'Expected privacy = True, actual = {privacy}'
        else:
            assert privacy == expected_privacy, f'Expected privacy = {expected_privacy} while actual = {privacy}'
        return self

    def verify_token_privacy(self, expected_privacy=True):
        INFO(f'Check tx token privacy: {self.get_tx_id()}')
        detail_proof = self.get_privacy_custom_token_proof_detail()
        privacy = self.is_privacy_custom_token()
        INFO(f'PrivacyCustomTokenIsPrivacy={privacy}')
        return self.__verify_privacy(privacy, detail_proof, expected_privacy)

    def verify_prv_privacy(self, expected_privacy=True):
        version = ChainConfig.PRIVACY_VERSION
        expected_privacy = bool(expected_privacy)
        INFO(f'Check tx prv privacy v{version}: {self.get_tx_id()}')
        detail_proof = self.get_prv_proof_detail()
        privacy = self.is_privacy()
        INFO(f'IsPrivacy={privacy}')
        return self.__verify_privacy(privacy, detail_proof, expected_privacy)

    def is_confirmed(self):
        return self.get_block_hash() and self.get_hash()