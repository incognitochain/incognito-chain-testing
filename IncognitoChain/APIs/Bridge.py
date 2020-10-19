from IncognitoChain.Configs import Constants
from IncognitoChain.Drivers import Connections


class BridgeRpc:
    def __init__(self, url):
        self.rpc_connection = Connections.RpcConnection(url=url)

    def get_bridge_token_list(self):
        return self.rpc_connection. \
            with_method("getallbridgetokens"). \
            with_params([]). \
            execute()

    def get_all_token_list(self):
        return self.rpc_connection. \
            with_method("listprivacycustomtoken"). \
            with_params([]). \
            execute()

    def get_bridge_request_status(self, tx_id):
        return self.rpc_connection. \
            with_method("getbridgereqwithstatus"). \
            with_params([{
            "TxReqID": tx_id
        }]). \
            execute()

    def issue_centralized_bridge_token(self, receiver, token_id, token_name, amount):
        return self.rpc_connection. \
            with_method("createandsendissuingrequest"). \
            with_params([Constants.DAO_PRIVATE_K,
                         None, 100, -1,
                         {
                             "ReceiveAddress": receiver,
                             "DepositedAmount": amount,
                             "TokenID": token_id,
                             "TokenName":
                                 token_name
                         }]). \
            execute()

    def withdraw_centralized_bridge_token(self, withdrawer_private_key, token_id, amount):
        return self.rpc_connection. \
            with_method("createandsendissuingrequest"). \
            with_params([withdrawer_private_key,
                         {
                             Constants.BURNING_ADDR: 0
                         }, 100, -1,
                         {
                             "TokenID": token_id,
                             "TokenTxType": 1,
                             "TokenName": "",
                             "TokenSymbol": "",
                             "TokenAmount": amount,
                             "TokenReceivers": {
                                 Constants.BURNING_ADDR: amount
                             },
                             "Privacy": True,
                             "TokenFee": 0
                         },
                         "withdrawal description", 0
                         ]). \
            execute()
