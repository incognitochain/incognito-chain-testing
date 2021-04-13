from APIs import BaseRpcApi
from Configs.Constants import BURNING_ADDR


class Portalv4Rpc(BaseRpcApi):

    # user request token ########################################################################################
    def create_n_send_tx_shield_req(self, requester_private_key, requester_payment_key, token_id,
                                    proof):
        return self.rpc_connection.with_method('createandsendtxshieldingrequest'). \
            with_params([requester_private_key,
                         None, -1, 0,
                         {
                             "IncogAddressStr": requester_payment_key,
                             "TokenID": token_id,
                             "ShieldingProof": proof
                         }
                         ]).execute()

    def get_portal_shield_status(self, request_tx_id):
        return self.rpc_connection.with_method('getportalshieldingrequeststatus'). \
            with_params([{"ReqTxID": request_tx_id}]).execute()

    # # unshield request ########################################################################################
    def create_n_send_tx_with_unshield_req(self, unshield_private_key, unshield_payment_addr, remote_addr,
                                           token_id, unshield_amount, privacy=True):
        return self.rpc_connection.with_method('createandsendtxwithportalv4unshieldrequest'). \
            with_params([unshield_private_key, None, -1, -1,
                         {
                             "Privacy": privacy,
                             "TokenID": token_id,
                             "TokenTxType": 1,
                             "TokenName": "",
                             "TokenSymbol": "",
                             "TokenAmount": str(unshield_amount),
                             "TokenReceivers": {BURNING_ADDR: str(unshield_amount)},
                             "TokenFee": "0",
                             "PortalTokenID": token_id,
                             "UnshieldAmount": str(unshield_amount),
                             "IncAddressStr": unshield_payment_addr,
                             "RemoteAddress": remote_addr},
                         "", 0]).execute()

    # unshield status : Status (Number):  0 - waiting, 1 - processed, 2 - completed, 3 - refunded.
    def get_unsheild_status(self, unshield_id):
        return self.rpc_connection.with_method('getportalunshieldrequeststatus'). \
            with_params([{"UnshieldID": unshield_id}]).execute()

    # get batch process : Status (Number):  0 - processed, 1 - completed.
    def get_unshield_batch_status(self, batch_id):
        return self.rpc_connection.with_method('getportalbatchunshieldrequeststatus'). \
            with_params([{"BatchID": batch_id}]).execute()

    def get_signed_raw_transaction(self, batch_id):
        return self.rpc_connection.with_method('getportalsignedrawtransaction'). \
            with_params([{"BatchID": batch_id}]).execute()  # return hex raw transaction

    #  submit confirmed transaction
    def create_n_send_tx_portal_submit_confirmtx(self, user_private_key, unshield_btc_proof, token_id, batch_id):
        return self.rpc_connection.with_method("createandsendtxwithportalsubmitconfirmedtx").with_params([
            user_private_key,
            None,
            -1,
            0,
            {
                "UnshieldProof": unshield_btc_proof,
                "PortalTokenID": token_id,
                "BatchID": batch_id
            }
        ]).execute()

    # get status of submit confirmed tx by transaction ID
    def get_portal_submit_confirm_status(self, txid):
        return self.rpc_connection.with_method("getportalsubmitconfirmedtxstatus").with_params(
            [{"ReqTxID": txid}]).execute()

    # request replacement fee
    def create_n_send_tx_portal_replace_fee(self, private_key, token_id, batch_id, replace_fee):
        return self.rpc_connection.with_method("createandsendtxwithportalreplacebyfee").with_params([
            private_key,
            None,
            -1,
            0,
            {
                "PortalTokenID": token_id,
                "BatchID": batch_id,
                "ReplacementFee": str(replace_fee)
            }
        ]).execute()

    # get status replace fee tx
    def get_replace_fee_status(self, txhash):
        return self.rpc_connection.with_method("getportalreplacebyfeestatus").with_params(
            [{"ReqTxID": txhash}]).execute()

    # get raw transaction replace fee
    def get_signed_raw_replace_fee_transaction(self,txhash_rpl_fee):
        return self.rpc_connection.with_method("getporalsignedrawreplacebyfeetransaction").with_params(
            [{"TxID": txhash_rpl_fee}]).execute()

    # get state #

    def get_portal_v4_state(self, beacon_height):
        return self.rpc_connection.with_method('getportalv4state'). \
            with_params([{"BeaconHeight": str(beacon_height)}]).execute()
