from APIs.BackEnd import BackEndApiBase
from Drivers import ResponseBase
from Objects import BlockChainInfoBaseClass

OFFSET = 0
LIMIT = 10000
VERSION = 2
K_TYPE_PAYMENT = "paymentkey"
K_TYPE_VIEW = "viewkey"
K_TYPE_OTA = "otakey"


class CoinServiceApi(BackEndApiBase):
    def get_coins(self, token_id, version=VERSION, offset=OFFSET, limit=LIMIT, **key):
        """
        @param limit:
        @param offset:
        @param version:
        @param token_id:
        @param key: key_type=value (paymentkey | viewkey | otakey)
        @return:
        """
        params = {**{'offset': offset, 'limit': limit, 'tokenid': token_id, 'version': version}, **key}
        return self.get('getcoins', **params)

    def check_key_images(self, k_image_list, shard_id):
        """
        @param k_image_list: list of key images
        @param shard_id:
        @return:
        """
        return self.post('checkkeyimages', {"Keyimages": k_image_list, "ShardID": shard_id})

    def get_key_info(self, key, version=VERSION):
        """
        @param key: Ota private key (privacy v2) or payment key (privacy v1)
        @param version: privacy version
        @return:
        """
        return KeyInfoResponse(self.get('getkeyinfo', key=key, version=version))

    def get_coins_pending(self):
        return self.get('getcoinspending')

    def get_txs_history(self, key, token_id, offset=OFFSET, limit=LIMIT):
        """
        @param key: Ota private key (privacy v2) or payment key (privacy v1)
        @param token_id:
        @param offset:
        @param limit:
        @return:
        """
        return self.get('gettxshistory', paymentkey=key, tokenid=token_id, offset=offset, limit=limit)

    def get_token_list(self):
        return self.get("coins/tokenlist")

    def get_list_pool(self, pair="all", verify=True):
        return ListPoolResponse(self.get("pdex/v3/listpools", pair=pair, verify=verify))

    def get_pending_order(self, pool_id):
        return self.get("pdex/v3/pendingorder", poolid=pool_id)

    # v2 only
    def submit_ota_key(self, ota_private_k, shard_id, from_now=True):
        return self.post('submitotakey', {'OTAKey': ota_private_k, "FromNow": from_now, 'ShardID': shard_id})

    def parse_token_id(self, ota_key, asset_tags, ota_randoms):
        return self.post('parsetokenid', {'OTARandoms': ota_randoms, 'OTAKey': ota_key, 'AssetTags': asset_tags})

    def request_drop_nft(self, paymentkey):
        return self.get('nftdrop-service/requestdrop-nft', paymentkey=paymentkey)

    def get_order_book_history(self, pool_id, nft_id, limit=1000000000, offset=0):
        return self.get("pdex/v3/tradehistory", poolid=pool_id, nftid=nft_id, limit=limit, offset=offset)

    def get_trade_history(self, ota_key, limit=1000, offset=0):
        return self.get("pdex/v3/tradehistory", otakey=ota_key, limit=limit, offset=offset)

    def get_contribute_history(self, nft_id, limit=1000000000, offset=0):
        return self.get("pdex/v3/contributehistory", nftid=nft_id, limit=limit, offset=offset)

    def get_withdraw_fee_history(self, nft_id, limit=1000000000, offset=0):
        return self.get("pdex/v3/withdrawfeehistory", nftid=nft_id, limit=limit, offset=offset)

    def get_withdraw_history(self, nft_id, limit=1000000000, offset=0):
        return self.get("pdex/v3/withdrawhistory", nftid=nft_id, limit=limit, offset=offset)

    def get_swap_history(self, ota_k, limit=1000, offset=0):
        return self.get("pdex/v3/withdrawhistory", otakey=ota_k, limit=limit, offset=offset)

    def get_pool_share(self, nft_id):
        return self.get("pdex/v3/poolshare", nftid=nft_id)


class KeyInfoResponse(ResponseBase):
    class Coin(BlockChainInfoBaseClass):
        pass  # todo

    @property
    def id(self):
        return self.get_result("id")

    @property
    def created_time(self):
        return self.get_result("created_at")

    @property
    def updated_time(self):
        return self.get_result("updated_at")

    @property
    def pubkey(self):
        return self.get_result("pubkey")

    @property
    def otakey(self):
        return self.get_result("otakey")

    def get_nft_id(self):
        return list(self.get_result("nftindex").keys())


class ListPoolResponse(ResponseBase):

    def get_pool_info(self, extract=None):
        """
        @param extract: must be 1 of ['PoolID', 'Token1ID', 'Token2ID', 'Token1Value', 'Token2Value', 'Virtual1Value',
         'Virtual2Value', 'TotalShare', 'AMP', 'Price', 'Volume', 'PriceChange24h', 'APY', 'IsVerify']
        @return:
        """
        return [item[extract] for item in self.get_result()] if extract else self.get_result()
