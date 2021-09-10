from APIs import BaseRpcApi, unspecified
from Configs import Constants


class DEXv3RPC(BaseRpcApi):
    def get_trade_status(self, tx_id):
        return self.rpc_connection.with_method('pdexv3_getTradeStatus').with_params([tx_id]).execute()

    def get_add_order_status(self, tx_id):
        return self.rpc_connection.with_method('pdexv3_getAddOrderStatus').with_params([tx_id]).execute()

    def get_withdraw_order_status(self, tx_id):
        return self.rpc_connection.with_method('pdexv3_getWithdrawOrderStatus').with_params([tx_id]).execute()

    def add_order(self, private_k, nft_id, token_sell, pool_pair_id, sell_amount, min_acceptable, tx_fee=-1,
                  tx_privacy=1):
        return self.rpc_connection.with_method('pdexv3_txAddOrder') \
            .with_params([private_k, None, tx_fee, tx_privacy,
                          {"TokenToSell": token_sell,
                           "PoolPairID": pool_pair_id,
                           "NftID": nft_id,
                           "SellAmount": sell_amount,
                           "MinAcceptableAmount": min_acceptable}
                          ]).execute()

    def withdraw_order(self, private_k, token_id, amount, nft_id, pair_id, order_id, tx_fee=-1, tx_privacy=1):
        return self.rpc_connection.with_method('pdexv3_txWithdrawOrder') \
            .with_params([private_k, None, tx_fee, tx_privacy,
                          {
                              "TokenID": token_id,
                              "PoolPairID": pair_id,
                              "NftID": nft_id,
                              "Amount": amount,
                              "OrderID": order_id
                          }]).execute()

    def trade(self, private_k, token_sell, token_buy, sell_amount, min_acceptable, trade_path, trading_fee=100,
              use_prv_fee=True, tx_fee=-1, tx_privacy=1):
        """
        @param private_k:
        @param token_sell:
        @param token_buy:
        @param sell_amount:
        @param min_acceptable:
        @param trade_path: list of pair id, example ['pair
        @param trading_fee:
        @param use_prv_fee: True/False
        @param tx_fee:
        @param tx_privacy:
        @return:
        """
        return self.rpc_connection.with_method("pdexv3_txTrade") \
            .with_params([private_k, None, tx_fee, tx_privacy,
                          {
                              "TradePath": trade_path,
                              "TokenToSell": token_sell,
                              "TokenToBuy": token_buy,
                              "SellAmount": sell_amount,
                              "MinAcceptableAmount": min_acceptable,
                              "TradingFee": trading_fee,
                              "FeeInPRV": use_prv_fee
                          }]).execute()

    def get_estimated_lp_value(self, pool_pair_id, nft_id):
        return self.rpc_connection.with_method("pdexv3_getEstimatedLPValue") \
            .with_params([{"PoolPairID": pool_pair_id,
                           "NftID": nft_id}]).execute()

    def withdraw_lp_fee(self, private_k, receiver_payment_address, token_amount, token_id, pool_pair_id, nft_id,
                        token_tx_type=1, token_fee=0, token_name="", token_symbol=0,
                        burning_addr=Constants.BURNING_ADDR, burn_amount=1, tx_fee=-1, tx_privacy=1):
        """
        @param token_symbol:
        @param token_name:
        @param private_k:
        @param receiver_payment_address:
        @param token_amount:
        @param token_id: should be the same as nft_id, and should test the case which token_id != nft_id
        @param pool_pair_id:
        @param nft_id:
        @param token_tx_type:
        @param token_fee:
        @param burning_addr:
        @param burn_amount:
        @param tx_fee:
        @param tx_privacy:
        @return:
        """
        return self.rpc_connection.with_method("pdexv3_txWithdrawLPFee") \
            .with_params([private_k, None, tx_fee, tx_privacy, {
            "Privacy": True,
            "TokenID": token_id,
            "TokenTxType": token_tx_type,
            "TokenName": token_name,
            "TokenSymbol": token_symbol,
            "TokenAmount": token_amount,
            "TokenReceivers": {burning_addr: burn_amount},
            "TokenFee": str(token_fee),
            "PoolPairID": pool_pair_id,
            "NftID": nft_id,
            "FeeReceiver": receiver_payment_address}, "", 0]).execute()

    def get_withdrawal_lp_fee_status(self, tx_id):
        return self.rpc_connection.with_method("pdexv3_getWithdrawalLPFeeStatus") \
            .with_params([{"ReqTxID": tx_id}]).execute()

    def withdraw_protocol_fee(self, centralize_private_k, pool_pair_id, tx_fee=-1, tx_privacy=1):
        return self.rpc_connection.with_method("pdexv3_txWithdrawProtocolFee") \
            .with_params([centralize_private_k, None, tx_fee, tx_privacy,
                          {"PoolPairID": pool_pair_id}, "", 0]).execute()

    def get_withdraw_protocol_fee_status(self, tx_id):
        return self.rpc_connection.with_method("pdexv3_getWithdrawalProtocolFeeStatus") \
            .with_params([{"ReqTxID": tx_id}]).execute()

    def get_staking_status(self, *tx_id):
        return self.rpc_connection.with_method("pdexv3_getStakingStatus") \
            .with_params(tx_id).execute()

    def stake(self, private_k, token_id, stake_amount, nft_id="", burning_addr=Constants.BURNING_ADDR,
              burn_amount='unspecified', tx_fee=-1, tx_privacy=1):
        burn_amount = stake_amount if burn_amount == 'unspecified' else burn_amount
        return self.rpc_connection.with_method("pdexv3_txStake") \
            .with_params([private_k, {burning_addr: burn_amount}, tx_fee, tx_privacy,
                          {"TokenID": token_id,
                           "TokenAmount": stake_amount,
                           "NftID": nft_id}]).execute()

    def unstake(self, private_k, staking_pool_id, token_id, unstake_amount, token_amount=1,
                burning_addr=Constants.BURNING_ADDR, burn_amount='unspecified', tx_fee=-1, tx_privacy=1):
        burn_amount = token_amount if burn_amount == 'unspecified' else burn_amount
        return self.rpc_connection.with_method("pdexv3_txUnstake") \
            .with_params([{[private_k, {burning_addr: str(burn_amount)}, tx_fee, tx_privacy,
                            {"StakingPoolID": staking_pool_id,
                             "TokenID": token_id,
                             "TokenAmount": token_amount,
                             "UnstakingAmount": unstake_amount}], }]).execute()

    def get_estimated_staking_reward(self, staking_pool_id, nft_id):
        return self.rpc_connection.with_method("pdexv3_getEstimatedStakingReward") \
            .with_params([{"StakingPoolID": staking_pool_id,
                           "NftID": nft_id}]).execute()

    def withdraw_staking_reward(self, private_k, receiver_payment_addr, staking_pool_id, nft_id, token_id=unspecified,
                                burning_addr=Constants.BURNING_ADDR, burn_amount=1, privacy=True, token_fee=0,
                                token_tx_type=1, token_amount=1, tx_fee=-1, tx_privacy=1):
        token_id = nft_id if token_id == unspecified else token_id
        return self.rpc_connection.with_method("pdexv3_txWithdrawStakingReward") \
            .with_params([private_k, None, tx_fee, tx_privacy,
                          {"Privacy": privacy,
                           "TokenID": token_id,
                           "TokenTxType": token_tx_type,
                           "TokenName": "",
                           "TokenSymbol": "",
                           "TokenAmount": token_amount,
                           "TokenReceivers": {burning_addr: burn_amount},
                           "TokenFee": str(token_fee),
                           "StakingPoolID": staking_pool_id,
                           "NftID": nft_id,
                           "FeeReceiver": receiver_payment_addr
                           }, "", 0]).execute()

    def get_withdrawal_staking_reward_status(self, tx_id):
        return self.rpc_connection.with_method("pdexv3_getWithdrawalStakingRewardStatus") \
            .with_params([{"ReqTxID": tx_id}]).execute()

    def modify_param(self, centralized_private_k, tx_fee=-1, tx_privacy=1):
        # todo, not yet done
        return self.rpc_connection.with_method("pdexv3_txModifyParams") \
            .with_params([centralized_private_k, None, -1, 0,
                          {"NewParams": {
                              "DefaultFeeRateBPS": "1",
                              "FeeRateBPS": {
                                  "PRV-BTC-1": "1",
                                  "PRV-ETH-2": "2"
                              },
                              "PRVDiscountPercent": "2",
                              "TradingProtocolFeePercent": "5",
                              "TradingStakingPoolRewardPercent": "6",
                              "PDEXRewardPoolPairsShare": {
                                  "PRV-BTC-3": "100",
                                  "PRV-ETH-4": "20"
                              },
                              "StakingPoolsShare": {
                                  "0000000000000000000000000000000000000000000000000000000000000004": "200",
                                  "0000000000000000000000000000000000000000000000000000000000000006": "100"
                              },
                              "StakingRewardTokens": [
                                  "0000000000000000000000000000000000000000000000000000000000000004"
                              ],
                              "MintNftRequireAmount": "100",
                              "MaxOrdersPerNft": "10"
                          }}]).execute()

    def get_modify_param_status(self):
        pass

    def get_pdev3_state(self, beacon_height):
        return self.rpc_connection.with_method("pdexv3_getState") \
            .with_params([{"BeaconHeight": beacon_height}]).execute()

    def add_liquidity(self, private_k, token_id, amount, amplifier, pool_pair_id="", pair_hash="", nft_id="",
                      burning_addr=Constants.BURNING_ADDR, burn_amount=unspecified, tx_fee=-1, tx_privacy=1):
        burn_amount = amount if burn_amount == unspecified else burn_amount
        return self.rpc_connection.with_method("pdexv3_txAddLiquidity") \
            .with_params([private_k, {burning_addr: burn_amount}, tx_fee, tx_privacy,
                          {
                              "PoolPairID": pool_pair_id,
                              "TokenID": token_id,
                              "TokenAmount": amount,
                              "PairHash": pair_hash,
                              "Amplifier": amplifier,
                              "NftID": nft_id
                          }]).execute()

    def withdraw_liquidity(self, private_k, receiver_payment_k, pool_pair_id, token_id, share_amount,
                           token_amount=1, receiver_amount=unspecified, tx_fee=-1, tx_privacy=1):
        receiver_amount = token_amount if receiver_amount == unspecified else receiver_amount
        return self.rpc_connection.with_method("pdexv3_txWithdrawLiquidity") \
            .with_params([private_k, {receiver_payment_k: str(receiver_amount)}, tx_fee, tx_privacy,
                          {
                              "PoolPairID": pool_pair_id,
                              "TokenID": token_id,
                              "TokenAmount": str(token_amount),
                              "ShareAmount": str(share_amount)
                          }]).execute()

    def get_contribution_status(self, tx_id):
        return self.rpc_connection.with_method("pdexv3_getContributionStatus") \
            .with_params([tx_id]).execute()

    def get_withdraw_liquidity_status(self, tx_id):
        return self.rpc_connection.with_method("pdexv3_getWithdrawLiquidityStatus") \
            .with_params([tx_id]).execute()

    def mint_nft(self, private_k, amount, token_id=Constants.PRV_ID, burning_addr=Constants.BURNING_ADDR,
                 burn_amount=unspecified, tx_fee=-1, tx_privacy=1):
        burn_amount = amount if burn_amount == unspecified else burn_amount
        return self.rpc_connection.with_method("pdexv3_txMintNft") \
            .with_params([private_k, {burning_addr: str(burn_amount)}, tx_fee, tx_privacy,
                          {"TokenID": token_id,
                           "TokenAmount": str(amount)}]).execute()

    def get_mint_nft_status(self, tx_id):
        return self.rpc_connection.with_method("pdexv3_getMintNftStatus") \
            .with_params([tx_id]).execute()
