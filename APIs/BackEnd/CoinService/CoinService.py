from APIs.BackEnd import BackEndApiBase
from Drivers import ResponseBase

OFFSET = 0
LIMIT = 10000
VERSION = 2


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
        return self.get('getkeyinfo', key=key, version=version)

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

    # v2 only
    def submit_ota_key(self, ota_private_k, shard_id, from_now=True):
        return self.post('submitotakey', {'OTAKey': ota_private_k, "FromNow": from_now, 'ShardID': shard_id})

    def parse_token_id(self, ota_key, asset_tags, ota_randoms):
        return self.post('parsetokenid', {'OTARandoms': ota_randoms, 'OTAKey': ota_key, 'AssetTags': asset_tags})

    def request_drop_nft(self, paymentkey):
        return self.get('nftdrop-service/requestdrop-nft', paymentkey=paymentkey)


class KeyInfoResponse(ResponseBase):
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
