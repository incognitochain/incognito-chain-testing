import json

from libs.AutoLog import *


class SubscriptionWs:
    def __init__(self, url):
        from IncognitoChain.Drivers.Connections import WebSocket
        self.ws_conn = WebSocket(url=url)

    def subscribe_new_shard_block(self):
        return self.ws_conn.with_method("subcribenewshardblock").with_params([0]).execute()

    def subscribe_pending_transaction(self, tx_id):
        return self.ws_conn.with_method("subcribependingtransaction").with_params([tx_id]).execute()

    def subscribe_cross_output_coin_by_private_key(self, private_key):
        return self.ws_conn.with_method("subcribecrossoutputcoinbyprivatekey").with_params([private_key])

    def subscribe_cross_custom_token_privacy_by_private_key(self, private_key):
        return self.ws_conn.with_method("subcribecrosscustomtokenprivacybyprivatekey").with_params([private_key])

    def close_web_socket(self):
        self.ws_conn.close()
