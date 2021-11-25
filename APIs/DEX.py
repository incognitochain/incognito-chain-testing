from APIs import BaseRpcApi
from Configs import Constants as Const


class DexRpc(BaseRpcApi):
    def contribute_prv(self, private_key, payment_address, amount_to_contribute, contribution_pair_id, tx_ver):
        return self.rpc_connection.with_method("createandsendtxwithprvcontribution"). \
            with_params([private_key,
                         {Const.BURNING_ADDR: amount_to_contribute}, 100, -1,
                         {
                             "PDEContributionPairID": contribution_pair_id,
                             "ContributorAddressStr": payment_address,
                             "ContributedAmount": amount_to_contribute,
                             "TokenIDStr": Const.PRV_ID,
                             "TxVersion": tx_ver
                         }
                         ]). \
            execute()

    def contribute_prv_v2(self, private_key, payment_address, amount_to_contribute, contribution_pair_id, tx_ver=2):
        amount_to_contribute = str(amount_to_contribute)
        return self.rpc_connection.with_method("createandsendtxwithprvcontributionv2"). \
            with_params([private_key,
                         {Const.BURNING_ADDR: amount_to_contribute}, -1, 1,
                         {
                             "PDEContributionPairID": contribution_pair_id,
                             "ContributorAddressStr": payment_address,
                             "ContributedAmount": amount_to_contribute,
                             "TokenIDStr": Const.PRV_ID,
                             "TxVersion": tx_ver
                         }
                         ]). \
            execute()

    def contribute_token(self, private_key, payment_address, token_id_to_contribute, amount_to_contribute,
                         contribution_pair_id, tx_ver=2):
        return self.rpc_connection. \
            with_method("createandsendtxwithptokencontribution"). \
            with_params([private_key,
                         None, 100, 0,
                         {
                             "Privacy": True,
                             "TokenID": token_id_to_contribute,
                             "TokenTxType": 1,
                             "TokenName": "",
                             "TokenSymbol": "",
                             "TokenAmount": amount_to_contribute,
                             "TokenReceivers": {
                                 Const.BURNING_ADDR: amount_to_contribute
                             },
                             "TokenFee": 0,
                             "PDEContributionPairID": contribution_pair_id,
                             "ContributorAddressStr": payment_address,
                             "ContributedAmount": amount_to_contribute,
                             "TokenIDStr": token_id_to_contribute,
                             "TxVersion": tx_ver
                         },
                         "", 0
                         ]). \
            execute()

    def contribute_token_v2(self, private_key, payment_address, token_id_to_contribute, amount_to_contribute,
                            contribution_pair_id, tx_ver):
        amount_to_contribute = str(amount_to_contribute)
        return self.rpc_connection. \
            with_method("createandsendtxwithptokencontributionv2"). \
            with_params([private_key,
                         None, 100, 0,
                         {
                             "Privacy": True,
                             "TokenID": token_id_to_contribute,
                             "TokenTxType": 1,
                             "TokenName": "",
                             "TokenSymbol": "",
                             "TokenAmount": amount_to_contribute,
                             "TokenReceivers": {
                                 Const.BURNING_ADDR: amount_to_contribute
                             },
                             "TokenFee": "0",
                             "PDEContributionPairID": contribution_pair_id,
                             "ContributorAddressStr": payment_address,
                             "ContributedAmount": amount_to_contribute,
                             "TokenIDStr": token_id_to_contribute,
                             "TxVersion": tx_ver
                         },
                         "", 0
                         ]). \
            execute()

    def trade_token(self, private_key, payment_address, token_id_to_sell, amount_to_sell, token_id_to_buy,
                    min_amount_to_buy, trading_fee=0, tx_ver=2):
        total_amount = amount_to_sell + trading_fee
        return self.rpc_connection. \
            with_method("createandsendtxwithptokentradereq"). \
            with_params([private_key, None, 2, -1,
                         {
                             "Privacy": True,
                             "TokenID": token_id_to_sell,
                             "TokenTxType": 1,
                             "TokenName": "",
                             "TokenSymbol": "",
                             "TokenAmount": total_amount,
                             "TokenReceivers": {
                                 Const.BURNING_ADDR: total_amount
                             },
                             "TokenFee": 0,

                             "TokenIDToBuyStr": token_id_to_buy,
                             "TokenIDToSellStr": token_id_to_sell,
                             "SellAmount": amount_to_sell,
                             "MinAcceptableAmount": min_amount_to_buy,
                             "TradingFee": trading_fee,
                             "TraderAddressStr": payment_address,
                             "TxVersion": tx_ver
                         }, "", 0]).execute()

    def trade_token_v2(self, private_k, payment_k, token_to_sell, amount_to_sell, token_to_buy, trading_fee,
                       min_acceptable_amount=1, tx_ver=2):
        return self.rpc_connection.with_method('createandsendtxwithptokencrosspooltradereq').with_params([
            private_k,
            {
                Const.BURNING_ADDR: str(trading_fee)
            }, -1, 0,
            {
                "Privacy": True,
                "TokenID": token_to_sell,
                "TokenTxType": 1,
                "TokenName": "",
                "TokenSymbol": "",
                "TokenAmount": str(amount_to_sell),
                "TokenReceivers": {
                    Const.BURNING_ADDR: str(amount_to_sell)
                },
                "TokenFee": "0",
                "TokenIDToBuyStr": token_to_buy,
                "TokenIDToSellStr": token_to_sell,
                "SellAmount": str(amount_to_sell),
                "MinAcceptableAmount": str(min_acceptable_amount),
                "TradingFee": str(trading_fee),
                "TraderAddressStr": payment_k,
                "TxVersion": tx_ver,
            }, "", 0
        ]).execute()

    def trade_prv(self, private_key, payment_address, amount_to_sell, token_id_to_buy, min_amount_to_buy, trading_fee,
                  tx_ver=2):
        return self.rpc_connection. \
            with_method("createandsendtxwithprvtradereq"). \
            with_params([private_key,
                         {Const.BURNING_ADDR: amount_to_sell + trading_fee}, -1, -1,
                         {
                             "TokenIDToBuyStr": token_id_to_buy,
                             "TokenIDToSellStr": Const.PRV_ID,
                             "SellAmount": amount_to_sell,
                             "MinAcceptableAmount": min_amount_to_buy,
                             "TraderAddressStr": payment_address,
                             "TradingFee": trading_fee,
                             "TxVersion": tx_ver
                         }]).execute()

    def trade_prv_v2(self, private_k, payment_k, amount_to_sell, token_to_buy, trading_fee, acceptable_amount=1,
                     burn_amount=None, tx_ver=2):
        if burn_amount is None:
            burn_amount = amount_to_sell + trading_fee
        return self.rpc_connection.with_method('createandsendtxwithprvcrosspooltradereq').with_params([
            private_k,
            {
                Const.BURNING_ADDR: str(burn_amount)
            }, -1, -1,
            {
                "TokenIDToBuyStr": token_to_buy,
                "TokenIDToSellStr": Const.PRV_ID,
                "SellAmount": str(amount_to_sell),
                "MinAcceptableAmount": str(acceptable_amount),
                "TradingFee": str(trading_fee),
                "TraderAddressStr": payment_k,
                "TxVersion": tx_ver
            }
        ]).execute()

    def withdrawal_contribution(self, private_key, payment_address, token_id_1, token_id_2, amount_withdrawal,
                                tx_ver=2):
        return self.rpc_connection. \
            with_method("createandsendtxwithwithdrawalreq"). \
            with_params([private_key,
                         {
                             Const.BURNING_ADDR: 0
                         }, -1, 0,
                         {
                             "WithdrawerAddressStr": payment_address,
                             "WithdrawalToken1IDStr": token_id_1,
                             "WithdrawalToken2IDStr": token_id_2,
                             "WithdrawalShareAmt": amount_withdrawal,
                             "TxVersion": tx_ver
                         }
                         ]). \
            execute()

    def get_pde_state(self, beacon_height):
        return self.rpc_connection. \
            with_method("getpdestate"). \
            with_params([{"BeaconHeight": beacon_height}]). \
            execute()

    def get_contribution_status(self, pair_id):
        return self.rpc_connection. \
            with_method("getpdecontributionstatusv2"). \
            with_params([{"ContributionPairID": pair_id}]). \
            execute()

    def get_trade_status(self, txrq_id):
        return self.rpc_connection. \
            with_method("getpdetradestatus"). \
            with_params([{"TxRequestIDStr": txrq_id}]). \
            execute()

    def withdrawal_contribution_v2(self, private_k, payment_k, token1, token2, amount):
        return self.rpc_connection. \
            with_method('createandsendtxwithwithdrawalreqv2'). \
            with_params([private_k,
                         {Const.BURNING_ADDR: '0'}, -1, 0,
                         {
                             "WithdrawerAddressStr": payment_k,
                             "WithdrawalToken1IDStr": token1,
                             "WithdrawalToken2IDStr": token2,
                             "WithdrawalShareAmt": str(amount)
                         }]). \
            execute()

    def withdraw_reward_v2(self, private_k, payment_k, token1, token2, amount, tx_ver=2):
        return self.rpc_connection. \
            with_method('createandsendtxwithpdefeewithdrawalreq'). \
            with_params([private_k, None, -1, 0,
                         {
                             "WithdrawerAddressStr": payment_k,
                             "WithdrawalToken1IDStr": token1,
                             "WithdrawalToken2IDStr": token2,
                             "WithdrawalFeeAmt": str(amount),
                             "TxVersion": tx_ver
                         }
                         ]). \
            execute()
