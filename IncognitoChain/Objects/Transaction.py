from IncognitoChain.Objects import BlockChainInfoBaseClass
from IncognitoChain.Objects.CoinObject import Coin


class TransactionDetail(BlockChainInfoBaseClass):
    """
    {
        "BlockHash": "71ae9a6137a9475f4f0c11e77899d0638d88a289bef4fed96ec18d05f8157d79",
        "BlockHeight": 1709753,
        "TxSize": 3,
        "Index": 0,
        "ShardID": 0,
        "Hash": "8dfc3985bd06a534c42d3b29d5e696190ff7463ae5b2af210673c57d4dcfbf6c",
        "Version": 1,
        "Type": "n",
        "LockTime": "2020-07-06T07:38:52",
        "Fee": 4,
        "Image": "",
        "IsPrivacy": true,
        "Proof": "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",
        "ProofDetail": {
        "InputCoins": [
            {
               "CoinDetails": {
                  "PublicKey": "",
                  "CoinCommitment": "",
                  "SNDerivator": {},
                  "SerialNumber": "1mGuvgLuMaFR1rxLhL2bpqWvjNCo7uYz8gdMseHibzdzuzc6ce",
                  "Randomness": {},
                  "Value": 0,
                  "Info": "13PMpZ4"
               },
               "CoinDetailsEncrypted": ""
            }
         ],
         "OutputCoins": [
            {
               "CoinDetails": {
                  "PublicKey": "1vhaytfYK4NG5M1SiZna1eReg5igfGz5nZGbHwJQRit1heuF5n",
                  "CoinCommitment": "12a1w3dhvgwYHqrQuBnFUMvvK26DGLtCEGAqC25fxbP6cR2YPL5",
                  "SNDerivator": {},
                  "SerialNumber": "",
                  "Randomness": {},
                  "Value": 0,
                  "Info": "13PMpZ4"
               },
               "CoinDetailsEncrypted": "1MGaVtW1Hf6TZSbakwq8KvJe1o27xuhrpHcjTdb8yBzuvUVX6LZpucX9dDv169DD8ZfkruTt6QoxBzPnKYN1GTLmPvhwLrTrwevhxz2eguGTcWCSoG8gEJnVEuDvw2LMKBu1SciK6MpWTWv33X17Je8x1i4ASxBXg"
            },
            {
               "CoinDetails": {
                  "PublicKey": "12kmiLFDSxaezVQe32Ze7D9TFm9TLs1Rx5cgh4ix5Eh4hZrvtXB",
                  "CoinCommitment": "1aozTcrA2W7eC7dyHeW61xAxfgGnv1cbR7WVP67feWd69aCEL3",
                  "SNDerivator": {},
                  "SerialNumber": "",
                  "Randomness": {},
                  "Value": 0,
                  "Info": "13PMpZ4"
               },
               "CoinDetailsEncrypted": "14oWumHK8XVJLudJ1mY88MssUzEoXxfa3YgspKm5kbXyky5UHziWCJsxPayqesiw2UP3sHsAEy8Xip3BNUyHabg4ovzMS7jRpt9VhacPk9iivgp2d62btgo8SVxMABUmP7jdioKQ64JGK1nuBjKsPLyQBLEZx4pEpeJ7bzhs"
            }
         ]
        },
        "InputCoinPubKey": "",
        "SigPubKey": "13Msj6tLW3U27YHWQJEGRAo7gYem3tWVQeoEkg74W2qv9Yk7x7",
        "Sig": "14BS89QAtZiXiHd7hLhpXM79m6rWekzteayuxfwTpr628VpNkCFMiHKuhdeBeo1jqku7iDd9vNBrV35bci1zG1JwY58P656KHx9nxrKBz7oQU4cyNsWnNJB5v27jLszvu4fQCTVKQT",
        "Metadata": "",
        "CustomTokenData": "",
        "PrivacyCustomTokenID": "",
        "PrivacyCustomTokenName": "",
        "PrivacyCustomTokenSymbol": "",
        "PrivacyCustomTokenData": "",
        "PrivacyCustomTokenProofDetail": {
         "InputCoins": null,
         "OutputCoins": null
        },
        "PrivacyCustomTokenIsPrivacy": false,
        "PrivacyCustomTokenFee": 0,
        "IsInMempool": false,
        "IsInBlock": true,
        "Info": ""
    }
    """

    def get_block_hash(self):
        return self.data['BlockHash']

    def get_block_height(self):
        return self.data['BlockHeight']

    def get_tx_size(self):
        return self.data['TxSize']

    def get_index(self):
        return self.data['Index']

    def get_shard_id(self):
        return self.data['ShardID']

    def get_hash(self):
        return self.data['Hash']

    def get_version(self):
        return self.data['Version']

    def get_type(self):
        return self.data['Type']

    def get_lock_time(self):
        return self.data['LockTime']

    def get_fee(self):
        return self.data['Fee']

    def get_image(self):
        return self.data['Image']

    def is_privacy(self):
        privacy = True if self.data['IsPrivacy'] == 'true' else False
        return privacy

    def get_proof(self):
        return self.data['Proof']

    def get_proof_detail(self):
        return TxDetailProof(self.data['ProofDetail'])

    def get_input_coin_pub_key(self):
        return self.data['InputCoinPubKey']

    def get_sig_pub_key(self):
        return self.data['SigPubKey']

    def get_sig(self):
        return self.data['Sig']

    def get_meta_data(self):
        return self.data['Metadata']

    def get_custom_token_data(self):
        return self.data['CustomTokenData']

    def get_privacy_custom_token_id(self):
        return self.data['PrivacyCustomTokenID']

    def get_privacy_custom_token_name(self):
        return self.data['PrivacyCustomTokenName']

    def get_privacy_custom_token_symbol(self):
        return self.data['PrivacyCustomTokenSymbol']

    def get_privacy_custom_token_data(self):
        return self.data['PrivacyCustomTokenData']

    def get_privacy_custom_token_proof_detail(self):
        """
        "PrivacyCustomTokenProofDetail": {
            "InputCoins": null,
            "OutputCoins": null
        },
        :return:
        """
        return self.data['PrivacyCustomTokenProofDetail']  # is object??

    def is_privacy_custom_token(self):
        privacy = True if self.data['PrivacyCustomTokenIsPrivacy'] == 'true' else False
        return privacy

    def privacy_custom_token_fee(self):
        return self.data['PrivacyCustomTokenFee']

    def is_in_mem_pool(self):
        in_mem_pool = True if self.data["IsInMempool"] == 'true' else False
        return in_mem_pool

    def is_in_block(self):
        in_block = True if self.data["IsInBlock"] == 'true' else False
        return in_block

    def get_info(self):
        return self.data['Info']


class TxDetailProof(BlockChainInfoBaseClass):
    def _get_coin_list(self, coin_list_data_raw):
        raw_coins = self.data[coin_list_data_raw]
        list_coin_obj = []
        for raw in raw_coins:
            coin_obj = Coin(raw['CoinDetails'])
            coin_obj.data['CoinDetailsEncrypted'] = raw['CoinDetailsEncrypted']
            list_coin_obj.append(coin_obj)
        return list_coin_obj

    def get_input_coins(self):
        return self._get_coin_list('InputCoins')

    def get_output_coins(self):
        return self._get_coin_list('OutputCoins')
