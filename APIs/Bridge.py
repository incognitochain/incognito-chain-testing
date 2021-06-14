from APIs import BaseRpcApi
from Configs import Constants


class BridgeRpc(BaseRpcApi):

    def get_bridge_token_list(self):
        return self.rpc_connection. \
            with_method("getallbridgetokens"). \
            with_params([]). \
            execute()

    def get_bridge_request_status(self, tx_id):
        return self.rpc_connection. \
            with_method("getbridgereqwithstatus"). \
            with_params([{
            "TxReqID": tx_id
        }]). \
            execute()

    def issue_centralized_bridge_token(self, DAO_private_key, receiver_payment_key,
                                       token_id, token_name, amount, tx_ver=2):
        return self.rpc_connection. \
            with_method("createandsendissuingrequest"). \
            with_params([DAO_private_key,
                         None, 100, -1,
                         {
                             "ReceiveAddress": receiver_payment_key,
                             "DepositedAmount": amount,
                             "TokenID": token_id,
                             "TokenName":
                                 token_name,
                             "TxVersion": tx_ver  # only mater with privacy v2, backward compatible with privacy v1
                         }]). \
            execute()

    def withdraw_centralized_bridge_token(self, withdrawer_private_key, token_id, amount, tx_ver=1):
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
                             "TokenFee": 0,
                             "TxVersion": tx_ver  # only mater with privacy v2, backward compatible with privacy v1
                         },
                         "withdrawal description", 0
                         ]). \
            execute()
