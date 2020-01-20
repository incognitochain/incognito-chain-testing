from IncognitoChain.Configs import Constants as Const
from IncognitoChain.Drivers.Connections import RpcConnection


class DexRpc:
    def __init__(self, url):
        self.rpc_connection = RpcConnection(url=url)

    def contribute_prv(self, private_key, payment_address, amount_to_contribute, contribution_pair_id):
        return self.rpc_connection.with_method("createandsendtxwithprvcontribution"). \
            with_params([private_key,
                         {
                             Const.burning_address: amount_to_contribute
                         },
                         100, -1,
                         {
                             "PDEContributionPairID": contribution_pair_id,
                             "ContributorAddressStr":
                                 payment_address,
                             "ContributedAmount": amount_to_contribute,
                             "TokenIDStr": Const.prv_token_id
                         }
                         ]). \
            execute()

    def contribute_token(self, private_key, payment_address, token_id_to_contribute, amount_to_contribute,
                         contribution_pair_id):
        return self.rpc_connection. \
            with_method("createandsendtxwithptokencontribution"). \
            with_params([private_key,
                         None, 100, -1,
                         {
                             "Privacy": True,
                             "TokenID": token_id_to_contribute,
                             "TokenTxType": 1,
                             "TokenName": "",
                             "TokenSymbol": "",
                             "TokenAmount": amount_to_contribute,
                             "TokenReceivers": {
                                 Const.burning_address: amount_to_contribute
                             },
                             "TokenFee": 0,
                             "PDEContributionPairID": contribution_pair_id,
                             "ContributorAddressStr": payment_address,
                             "ContributedAmount": amount_to_contribute,
                             "TokenIDStr": token_id_to_contribute
                         },
                         "", 0
                         ]). \
            execute()

    def trade_token(self, private_key, payment_address, token_id_to_sell, amount_to_sell, token_id_to_buy,
                    min_amount_to_buy, trading_fee=0):
        total_amount = amount_to_sell + trading_fee
        return self.rpc_connection. \
            with_method("createandsendtxwithptokentradereq"). \
            with_params([private_key,
                         None,
                         2,
                         -1,
                         {
                             "Privacy": True,
                             "TokenID": token_id_to_sell,
                             "TokenTxType": 1,
                             "TokenName": "",
                             "TokenSymbol": "",
                             "TokenAmount": total_amount,
                             "TokenReceivers": {
                                 Const.burning_address: total_amount
                             },
                             "TokenFee": 0,

                             "TokenIDToBuyStr": token_id_to_buy,
                             "TokenIDToSellStr": token_id_to_sell,
                             "SellAmount": amount_to_sell,
                             "MinAcceptableAmount": min_amount_to_buy,
                             "TradingFee": trading_fee,
                             "TraderAddressStr":
                                 payment_address
                         },
                         "",
                         0
                         ]). \
            execute()

    def trade_prv(self, private_key, payment_address, amount_to_sell, token_id_to_buy, min_amount_to_buy):
        return self.rpc_connection. \
            with_method("createandsendtxwithprvtradereq"). \
            with_params([private_key,
                         {
                             Const.burning_address: amount_to_sell
                         }, -1, -1,
                         {
                             "TokenIDToBuyStr": token_id_to_buy,
                             "TokenIDToSellStr": Const.prv_token_id,
                             "SellAmount": amount_to_sell,
                             "MinAcceptableAmount": min_amount_to_buy,
                             "TraderAddressStr": payment_address
                         }
                         ]). \
            execute()

    def withdrawal_contribution(self, private_key, payment_address, token_id_1, token_id_2, amount_withdrawal):
        return self.rpc_connection. \
            with_method("createandsendtxwithwithdrawalreq"). \
            with_params([private_key,
                         {
                             Const.burning_address: 0
                         }, -1, 0,
                         {
                             "WithdrawerAddressStr": payment_address,
                             "WithdrawalToken1IDStr": token_id_1,
                             "WithdrawalToken2IDStr": token_id_2,
                             "WithdrawalShareAmt": amount_withdrawal
                         }
                         ]). \
            execute()

    def get_beacon_best_state(self):
        return self.rpc_connection. \
            with_method("getbeaconbeststate"). \
            with_params([]). \
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
