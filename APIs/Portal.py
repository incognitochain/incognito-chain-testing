from APIs import BaseRpcApi
from Configs.Constants import BURNING_ADDR


class PortalRpc(BaseRpcApi):
    # rate ########################################################################################
    def get_portal_final_exchange_rates(self, beacon_height):
        return self.rpc_connection.with_method('getportalfinalexchangerates'). \
            with_params([{"BeaconHeight": str(beacon_height)}]).execute()

    def create_n_send_portal_exchange_rates(self, signer_private_key, signer_payment_key, rate_dict):
        """
        @param signer_private_key:
        @param signer_payment_key:
        @param rate_dict: dictionary of {
            'tokenid1': USDT price of the token1,
            'tokenid2': USDT price of the token2,
             ...
         }
        @return: Response object
        """

        return self.rpc_connection.with_method('createandsendportalexchangerates'). \
            with_params([signer_private_key, None, -1, 0,
                         {
                             'SenderAddress': signer_payment_key,
                             'Rates': rate_dict
                         }]).execute()

    def convert_exchange_rates(self, amount, token_id, beacon_height):
        return self.rpc_connection.with_method('convertexchangerates'). \
            with_params([{'ValuePToken': str(amount),
                          'TokenID': token_id,
                          'BeaconHeight': str(beacon_height)
                          }]).execute()

    # porting ########################################################################################

    def create_n_send_reg_porting_public_tokens(self, requester_private_key, requester_payment_key, token_id,
                                                amount, burn_fee, port_fee, register_id, ):
        return self.rpc_connection.with_method('createandsendregisterportingpublictokens'). \
            with_params([requester_private_key,
                         {BURNING_ADDR: str(burn_fee)},
                         -1, 0,
                         {
                             "UniqueRegisterId": register_id,
                             "IncogAddressStr": requester_payment_key,
                             "PTokenId": token_id,
                             "RegisterAmount": str(amount),
                             "PortingFee": str(port_fee)
                         }
                         ]).execute()

    def get_portal_porting_req_by_key(self, tx_hash):
        return self.rpc_connection.with_method('getportalportingrequestbykey'). \
            with_params([{'TxHash': tx_hash}]). \
            execute()

    def get_portal_porting_req_by_porting_id(self, porting_id):
        return self.rpc_connection.with_method('getportalportingrequestbyportingid'). \
            with_params([{'PortingId': porting_id}]).execute()

    def get_porting_req_fees(self, token_id, amount, beacon_height):
        return self.rpc_connection.with_method('getportingrequestfees'). \
            with_params([{"BeaconHeight": str(beacon_height),
                          "ValuePToken": str(amount),
                          "TokenID": token_id
                          }]).execute()

    # custodian deposit ########################################################################################
    def create_n_send_tx_with_custodian_deposit(self, private_key, payment_key, deposit_amount,
                                                ptoken_id_remote_addr_dict):
        """

        @param private_key: custodian private key
        @param payment_key: custodian payment key
        @param deposit_amount:
        @param ptoken_id_remote_addr_dict: dict of {ptoken id : remote payment address}  of custodian
        @return:
        """
        return self.rpc_connection.with_method('createandsendtxwithcustodiandeposit'). \
            with_params([private_key,
                         {BURNING_ADDR: str(deposit_amount)},
                         -1, 0,
                         {"IncognitoAddress": payment_key,
                          "RemoteAddresses": ptoken_id_remote_addr_dict,
                          "DepositedAmount": str(deposit_amount)}]).execute()

    def get_portal_custodian_deposit_status(self, deposit_tx_id):
        return self.rpc_connection.with_method('getportalcustodiandepositstatus'). \
            with_params([{"DepositTxID": deposit_tx_id}]). \
            execute()

    # user request token ########################################################################################
    def create_n_send_tx_with_req_ptoken(self, requester_private_key, requester_payment_key, porting_id, token_id,
                                         amount,
                                         proof):
        return self.rpc_connection.with_method('createandsendtxwithreqptoken'). \
            with_params([requester_private_key,
                         None, -1, 0,
                         {
                             "UniquePortingID": porting_id,
                             "IncogAddressStr": requester_payment_key,
                             "TokenID": token_id,
                             "PortingAmount": str(amount),
                             "PortingProof": proof
                         }
                         ]).execute()

    def get_portal_req_ptoken_status(self, request_tx_id):
        return self.rpc_connection.with_method('getportalreqptokenstatus'). \
            with_params([{"ReqTxID": request_tx_id}]).execute()

    # redeem request ########################################################################################
    def create_n_send_tx_with_redeem_req(self, redeemer_private_key, redeemer_payment_addr, remote_addr,
                                         token_id, redeem_amount, redeem_fee, redeem_id, privacy=True):
        return self.rpc_connection.with_method('createandsendtxwithredeemreq'). \
            with_params([redeemer_private_key,
                         {
                             BURNING_ADDR: str(redeem_fee)},
                         -1, -1,
                         {
                             "Privacy": privacy,
                             "TokenID": token_id,
                             "TokenTxType": 1,
                             "TokenName": "",
                             "TokenSymbol": "",
                             "TokenAmount": str(redeem_amount),
                             "TokenReceivers": {BURNING_ADDR: str(redeem_amount)},
                             "TokenFee": "0",
                             "UniqueRedeemID": redeem_id,
                             "RedeemTokenID": token_id,
                             "RedeemAmount": str(redeem_amount),
                             "RedeemFee": str(redeem_fee),
                             "RedeemerIncAddressStr": redeemer_payment_addr,
                             "RemoteAddress": remote_addr},
                         "", 0]).execute()

    def get_portal_redeem_status(self, redeem_id):
        return self.rpc_connection.with_method('getportalreqredeemstatus'). \
            with_params([{"RedeemID": redeem_id}]).execute()

    # request unlock collateral ############################################################################
    def get_portal_req_unlock_collateral_status(self, req_tx_id):
        return self.rpc_connection.with_method('getportalrequnlockcollateralstatus'). \
            with_params([{"ReqTxID": req_tx_id}]).execute()

    def create_n_send_tx_with_req_unlock_collateral(self, requester_private_key, custodian_payment_key, token_id,
                                                    amount_redeem, redeem_id, proof):
        return self.rpc_connection.with_method('createandsendtxwithrequnlockcollateral'). \
            with_params([requester_private_key, None, -1, 0,
                         {
                             "UniqueRedeemID": redeem_id,
                             "CustodianAddressStr": custodian_payment_key,
                             "TokenID": token_id,
                             "RedeemAmount": str(amount_redeem),
                             "RedeemProof": proof
                         }]).execute()

    # liquidation ########################################################################################
    def get_custodian_liquidation_status(self, custodian_payment_addr, redeem_id):
        return self.rpc_connection.with_method('getcustodianliquidationstatus'). \
            with_params([{"RedeemID": redeem_id,
                          "CustodianIncAddress": custodian_payment_addr
                          }]).execute()

    def get_liquidation_tp_exchange_rates(self, custodian_payment_key, beacon_height):
        return self.rpc_connection.with_method('getliquidationtpexchangerates'). \
            with_params([{"BeaconHeight": str(beacon_height),
                          "CustodianAddress": custodian_payment_key
                          }]).execute()

    def get_liquidation_exchange_rates_by_token_id(self, custodian_payment_key, token_id, beacon_height):
        return self.rpc_connection.with_method('getliquidationexchangeratesbytokenid'). \
            with_params([{"BeaconHeight": str(beacon_height),
                          "TokenID": token_id,
                          "CustodianAddress": custodian_payment_key
                          }]).execute()

    def create_n_send_liquidation_custodian_deposit(self, private_key, payment_key, amount, token_id,
                                                    free_collateral_selected=False):
        return self.rpc_connection.with_method('createandsendliquidationcustodiandeposit'). \
            with_params([private_key,
                         {BURNING_ADDR: str(amount)},
                         -1, 0, {
                             "IncognitoAddress": payment_key,
                             "DepositedAmount": str(amount),
                             "PTokenId": token_id,
                             "FreeCollateralSelected": free_collateral_selected
                         }]).execute()

    def get_amount_needed_for_custodian_deposit_liquidation(self, beacon_height, token_id, payment_key,
                                                            is_free_collateral_selected=False):
        return self.rpc_connection.with_method('getamountneededforcustodiandepositliquidation'). \
            with_params([{"BeaconHeight": str(beacon_height),
                          "IsFreeCollateralSelected": is_free_collateral_selected,
                          "TokenID": token_id,
                          "CustodianAddress": payment_key}]).execute()

    def create_n_send_redeem_liquidation_exchange_rates(self, private_key, payment_key,
                                                        token_amount, token_id, privacy=True):
        return self.rpc_connection.with_method('createandsendredeemliquidationexchangerates'). \
            with_params([private_key, None, -1, -1,
                         {
                             "Privacy": privacy,
                             "TokenID": token_id,
                             "TokenTxType": 1,
                             "TokenName": "",
                             "TokenSymbol": "",
                             "TokenAmount": str(token_amount),
                             "TokenReceivers": {BURNING_ADDR: str(token_amount)},
                             "TokenFee": "0",
                             "RedeemTokenID": token_id,
                             "RedeemAmount": str(token_amount),
                             "RedeemerIncAddressStr": payment_key,
                         }, "", 0]).execute()

    def get_liquidation_tp_exchange_rates_pool(self, token_id, beacon_height):
        return self.rpc_connection.with_method('getliquidationtpexchangeratespool'). \
            with_params([{"BeaconHeight": str(beacon_height),
                          "TokenID": token_id
                          }]).execute()

    # custodian req withdraw collateral ########################################################################
    def create_n_send_custodian_withdraw_req(self, private_key, payment_key, amount):
        return self.rpc_connection.with_method("createandsendcustodianwithdrawrequest"). \
            with_params([private_key, None, -1, 0,
                         {"Amount": str(amount),
                          "PaymentAddress": payment_key}]).execute()

    def get_custodian_withdraw_by_tx_id(self, tx_id):
        return self.rpc_connection.with_method("getcustodianwithdrawbytxid"). \
            with_params([{"TxId": tx_id}]).execute()

    # relaying ########################################################################################
    # custodian manual redeem picking
    def create_n_send_tx_with_req_matching_redeem(self, private_key, payment_key, redeem_id):
        return self.rpc_connection.with_method("createandsendtxwithreqmatchingredeem"). \
            with_params([private_key, None, -1, 0,
                         {
                             "CustodianAddressStr": payment_key,
                             "RedeemID": str(redeem_id)}]).execute()

    def get_req_matching_redeem_status(self, tx_id):
        return self.rpc_connection.with_method("getreqmatchingredeemstatus"). \
            with_params([{"ReqTxID": tx_id}]).execute()

    # get state #####################################
    def get_portal_state(self, beacon_height):
        return self.rpc_connection.with_method('getportalstate'). \
            with_params([{"BeaconHeight": str(beacon_height)}]).execute()

    # custodian reward ########################################################################
    def create_n_send_tx_with_req_withdraw_reward_portal(self, private_key, payment_key, token_id):
        return self.rpc_connection.with_method('createandsendtxwithreqwithdrawrewardportal'). \
            with_params([private_key, None, -1, 0,
                         {
                             "CustodianAddressStr": payment_key,
                             "TokenID": token_id}]).execute()

    def get_portal_reward(self, payment_key):
        return self.rpc_connection.with_method('getportalreward'). \
            with_params([{"IncognitoAddress": payment_key}]).execute()

    def get_request_withdraw_portal_reward_status(self, tx_id):
        return self.rpc_connection.with_method('getrequestwithdrawportalrewardstatus'). \
            with_params([{"ReqTxID": tx_id}]).execute()

    def get_btc_relaying_state(self):
        return self.rpc_connection.with_method('getbtcrelayingbeststate'). \
            with_params([]).execute()
