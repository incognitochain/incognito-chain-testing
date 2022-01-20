from APIs import BaseRpcApi, unspecified
from Configs import Constants
from Drivers.Response import RPCResponseBase, RPCResponseWithTxHash
from Helpers import Logging
from Objects.PdexV3Objects import PdeV3State

logger = Logging.config_logger(__name__)


class ResponseStatusBase(RPCResponseBase):
    def get_status(self):
        return self.get_result("Status")


class ResponseTxBase(RPCResponseWithTxHash):
    def get_base58_check_data(self):
        return self.response.get_result("Base58CheckData")

    def get_shard_id(self):
        return self.response.get_result("ShardID")


class ResponseTradeStatus(ResponseStatusBase):
    def get_buy_mount(self):
        return self.get_result("BuyAmount")

    def get_token_buy(self):
        return self.get_result("TokenToBuy")


class ResponseOrderStatus(ResponseStatusBase):
    """{
                "OrderID": "ea54e6b4dc56adb546cf8096bac6204159aa77f4c897f58625be09017d35c140",
                "Status": 1
        }"""

    def get_order_id(self):
        return self.get_result("OrderID")


class ResponseWithdrawOrderStatus(ResponseStatusBase):
    """: {
                "Amount": 669,
                "Status": 1,
                "TokenID": "0000000000000000000000000000000000000000000000000000000000000004"
        }"""

    def get_amount(self):
        return self.get_result("Amount")

    def get_token_id(self):
        return self.get_result("TokenID")


class ResponseWithdraw(ResponseTxBase):
    """  example:
        "Base58CheckData": "",
        "ShardID": 0,
        "TxID": "6f37444b9a1935fa1632779bc464b8bad691513bc67d76b95df914e8d636dc14",
        "TokenID": "e55476d221e72bf5950bbc60ccf43ae35f5a38fd89ee0d7273e28313b8e1d248",
        "TokenName": "",
        "TokenAmount": 0    """

    def get_token_id(self):
        return self.get_result("TokenID")

    def get_token_name(self):
        return self.get_result("TokenName")

    def get_token_amount(self):
        return self.get_result("TokenAmount")


class ResponseMintNftStatus(ResponseStatusBase):
    def get_burn_amount(self):
        return self.get_result("BurntAmount")

    def get_nft_id(self):
        return self.get_result("NftID")


class ResponseContributeStatus(ResponseStatusBase):
    def get_token_contribute_amount(self, index_or_token_id):
        if index_or_token_id in [self.get_token_id(0), 0]:
            return self.get_result("Token0ContributedAmount")
        if index_or_token_id in [self.get_token_id(1), 1]:
            return self.get_result("Token1ContributedAmount")

    def get_token_returned_amount(self, index_or_token_id):
        if index_or_token_id in [self.get_token_id(0), 0]:
            return self.get_result("Token0ReturnedAmount")
        if index_or_token_id in [self.get_token_id(1), 1]:
            return self.get_result("Token1ReturnedAmount")

    def get_token_id(self, index):
        return self.get_result(f"Token{index}ID")


class ResponseWithdrawLiquidityStatus(ResponseStatusBase):
    """ {
        "Status": "accepted",
        "Token0Amount": 16029395423,
        "Token0ID": "0000000000000000000000000000000000000000000000000000000000000004",
        "Token1Amount": 8014601537,
        "Token1ID": "1411bdcae86863b0c09d94de0c6617d6729f0c5b550f6aac236931b8989207c1"
    }"""

    def get_token0_amount(self):
        return self.get_result("Token0Amount")

    def get_token0_id(self):
        return self.get_result("Token0ID")

    def get_token1_amount(self):
        return self.get_result("Token1Amount")

    def get_token1_id(self):
        return self.get_result("Token1ID")


class ResponseAddLiquidity(ResponseWithdraw):
    pass  # nothing to add


class ResponseMintNft(ResponseTxBase):
    pass  # nothing to add


class ResponseAddOrder(ResponseTxBase):
    pass  # nothing to add


class ResponseTrade(ResponseTxBase):
    pass  # nothing to add


class ResponseStake(RPCResponseWithTxHash):
    pass  # nothing to add


class ResponseModifyParam(RPCResponseWithTxHash):
    pass  # nothing to add


class ResponseGetEstimatedLPValue(RPCResponseBase):
    """{
        "PoolValue": {
            "0000000000000000000000000000000000000000000000000000000000000004": 16970666577,
            "1411bdcae86863b0c09d94de0c6617d6729f0c5b550f6aac236931b8989207c1": 8485229468
        },
        "TradingFee": {
            "0000000000000000000000000000000000000000000000000000000000000004": 498
        }
    }"""

    def get_pool_value(self, token_id=None):
        if not token_id:
            return self.get_result("PoolValue")
        else:
            return self.get_result("PoolValue").get(token_id)

    def get_trading_fee(self, token_id=None):
        if not token_id:
            return self.get_result("TradingFee")
        else:
            return self.get_result("TradingFee").get(token_id)


class ResponseWithdrawLPFeeStatus(ResponseStatusBase):
    """ {
        "Status": 1,
        "Receivers": {
            "0000000000000000000000000000000000000000000000000000000000000004": { # todo: ask dev, should it be multi-receiver?
                "Address": "15aJPpUvgCNu978sppxG3KKMewCetCK5aNiJAVttcjwHeBTvQuMhpsGjDtvtt57tuUc3jbqNP9SuKyEbgTyJFKMGjqaYaQbtyERWzhCFDB55KTuhSwhzkFGvPqDoACsEfCqpPUdrgxYwAD55",
                "Amount": 498
            }
        }
    }"""

    def get_receivers(self, token=None, amount=None, address=None):
        return self.get_result("Receivers")

    def get_amounts(self, token=None):
        return {token: receiver['Amount'] for token, receiver in self.get_receivers().items()}


class ResponseWithdrawProtocolFeeStatus(ResponseStatusBase):
    """ {
        "Status": 1,
        "Amount": {
            "0000000000000000000000000000000000000000000000000000000000000004": 0
        }
    }"""

    def get_amount(self, token=None):
        """
        @param token: if none, return the amount of the first token on the list
        @return:
        """
        if not token:
            return self.get_result("Amount").get(token)

        return list(self.get_result("Amount").values())[0]

    def get_token_id(self):
        return list(self.get_result("Amount").keys())[0]


class ResponseStakingStatus(ResponseStatusBase):
    """{
        "Liquidity": 100,
        "NftID": "e55476d221e72bf5950bbc60ccf43ae35f5a38fd89ee0d7273e28313b8e1d248",
        "StakingPoolID": "0000000000000000000000000000000000000000000000000000000000000004",
        "Status": "accept"
    }"""

    def get_liquidity(self):
        return self.get_result("Liquidity")

    def get_nft_id(self):
        return self.get_result("NftID")

    def get_staking_pool_id(self):
        return self.get_result("StakingPoolID")


class ResponseTxUnstake(ResponseWithdraw):
    pass  # nothing to add


class ResponseEstimatedStakingReward(RPCResponseBase):
    def get_amount(self, by_token=None):
        if not by_token:
            return self.get_result()
        return self.get_result(by_token)


class ResponseWithdrawStakingRewardStatus(ResponseStatusBase):
    """{
        "Status": 1,
        "Receivers": {
            "0000000000000000000000000000000000000000000000000000000000000004": {
                "Address": "15wTh6NkrqBwCCkETVscuLdA3dDiid12YhCAdHTaGdkE57oDJhDnf5JXMRju1kE3mKjrBVNQjh5ASrKXCuYG55ef27HfsuzsiYbBSS5Cr8GB1UPvxd83iZXhh7xKPD7PahVGmJBMUhTktxn7",
                "Amount": 26
            }
        }
    },
    """

    def get_amount(self, by_token=None, by_receiver=None):
        all_reward = self.get_result("Receivers")
        if not (by_token and by_receiver):
            return all_reward
        if by_receiver and not by_token:  # get amount by address, return {token: amount}
            return {token: value["Amount"] for token, value in all_reward.items() if by_receiver == value["Address"]}
        if by_token and not by_receiver:  # get amount by token, return {receiver: amount}
            return all_reward[by_token]["Amount"]
        if by_token and by_receiver:
            raise SyntaxError("Only support query amount by token nor by receiver, not both")


class ResponseModifyParamStatus(ResponseStatusBase, PdeV3State.Param):
    @property
    def dict_data(self):
        return self.get_result("Pdexv3Params")

    def get_error(self):
        return self.get_result("ErrorMsg")

    def is_success(self):
        error = self.get_error()
        if error:
            logger.error(f"{self.rpc_params()}\n{error}")
            return False
        return True


# ======================================================================================================================
class DEXv3RPC(BaseRpcApi):
    def get_trade_status(self, tx_id):
        return ResponseTradeStatus(
            self.rpc_connection.with_method('pdexv3_getTradeStatus').with_params([tx_id]).execute())

    def get_add_order_status(self, tx_id):
        return ResponseOrderStatus(
            self.rpc_connection.with_method('pdexv3_getAddOrderStatus').with_params([tx_id]).execute())

    def get_withdraw_order_status(self, tx_id):
        return ResponseWithdrawOrderStatus(
            self.rpc_connection.with_method('pdexv3_getWithdrawOrderStatus').with_params([tx_id]).execute())

    def add_order(self, private_k, nft_id, token_sell, token_buy, pool_pair_id, sell_amount, min_acceptable,
                  main_tx_receiver=None, tx_fee=-1, tx_privacy=1):
        return ResponseAddOrder(
            self.rpc_connection.with_method('pdexv3_txAddOrder')
                .with_params([private_k, main_tx_receiver, tx_fee, tx_privacy,
                              {"TokenToSell": token_sell,
                               "TokenToBuy": token_buy,
                               "PoolPairID": pool_pair_id,
                               "NftID": nft_id,
                               "SellAmount": sell_amount,
                               "MinAcceptableAmount": min_acceptable}
                              ]).execute())

    def withdraw_order(self, private_k, pair_id, order_id, nft_id, token_id_list, amount,
                       main_tx_receiver=None, tx_fee=-1, tx_privacy=1):
        return ResponseWithdraw(
            self.rpc_connection.with_method('pdexv3_txWithdrawOrder')
                .with_params([private_k, main_tx_receiver, tx_fee, tx_privacy,
                              {
                                  "WithdrawTokenIDs": token_id_list,
                                  "PoolPairID": pair_id,
                                  "NftID": nft_id,
                                  "Amount": amount,
                                  "OrderID": order_id
                              }]).execute())

    def trade(self, private_k, token_sell, token_buy, sell_amount, min_acceptable, trade_path, trading_fee=100,
              use_prv_fee=True, main_tx_receiver=None, tx_fee=-1, tx_privacy=1):
        """
        @param main_tx_receiver: {} by default
        @param private_k:
        @param token_sell:
        @param token_buy:
        @param sell_amount:
        @param min_acceptable:
        @param trade_path: list of pair id, example ['pair1', 'pair2', ...]
        @param trading_fee:
        @param use_prv_fee: True/False
        @param tx_fee:
        @param tx_privacy:
        @return:
        """
        if main_tx_receiver is None:
            main_tx_receiver = {}
        return ResponseTrade(
            self.rpc_connection.with_method("pdexv3_txTrade")
                .with_params([private_k, main_tx_receiver, tx_fee, tx_privacy,
                              {
                                  "TradePath": trade_path,
                                  "TokenToSell": token_sell,
                                  "TokenToBuy": token_buy,
                                  "SellAmount": sell_amount,
                                  "MinAcceptableAmount": min_acceptable,
                                  "TradingFee": trading_fee,
                                  "FeeInPRV": use_prv_fee
                              }]).execute())

    def get_estimated_lp_value(self, pool_pair_id, nft_id, beacon_height=0):
        return ResponseGetEstimatedLPValue(
            self.rpc_connection.with_method("pdexv3_getEstimatedLPValue")
                .with_params([{"BeaconHeight": beacon_height,
                               "PoolPairID": pool_pair_id,
                               "NftID": nft_id}]).execute())

    def withdraw_lp_fee(self, private_k, receiver_payment_address, token_amount, token_id, pool_pair_id, nft_id,
                        token_tx_type=1, token_fee=0, token_name="", token_symbol="",
                        sub_tx_receiver=None, sub_tx_privacy=True, main_tx_receiver=None, tx_fee=-1, tx_privacy=1):
        """
        @param sub_tx_privacy:
        @param main_tx_receiver: None by default, accept dict type
        @param sub_tx_receiver: dict {burn addr: burn amount}, should test multiple output burn tx
        @param token_symbol:
        @param token_name:
        @param private_k:
        @param receiver_payment_address:
        @param token_amount:
        @param token_id: should be the same as nft_id, and should test the case which token_id != nft_id
        @param pool_pair_id:
        @param nft_id:
        @param token_tx_type:
        @param token_fee: string num, should be "0"
        @param tx_fee:
        @param tx_privacy:
        @return:
        """
        if sub_tx_receiver is None:
            sub_tx_receiver = {Constants.BURNING_ADDR: 1}
        return ResponseWithdraw(
            self.rpc_connection.with_method("pdexv3_txWithdrawLPFee")
                .with_params([private_k, main_tx_receiver, tx_fee, tx_privacy,
                              {"Privacy": sub_tx_privacy,
                               "TokenID": token_id,
                               "TokenTxType": token_tx_type,
                               "TokenName": token_name,
                               "TokenSymbol": token_symbol,
                               "TokenAmount": token_amount,
                               "TokenReceivers": sub_tx_receiver,
                               "TokenFee": token_fee,
                               "PoolPairID": pool_pair_id,
                               "NftID": nft_id,
                               "FeeReceiver": receiver_payment_address}, "", 0]).execute())

    def get_withdrawal_lp_fee_status(self, tx_id):
        return ResponseWithdrawLPFeeStatus(
            self.rpc_connection.with_method("pdexv3_getWithdrawalLPFeeStatus")
                .with_params([{"ReqTxID": tx_id}]).execute())

    def withdraw_protocol_fee(self, centralize_private_k, pool_pair_id, main_tx_receivers=None, tx_fee=-1,
                              tx_privacy=1):
        return ResponseWithdraw(self.rpc_connection.with_method("pdexv3_txWithdrawProtocolFee")
                                .with_params([centralize_private_k, main_tx_receivers, tx_fee, tx_privacy,
                                              {"PoolPairID": pool_pair_id}, "", 0]).execute())

    def get_withdraw_protocol_fee_status(self, tx_id):
        return ResponseWithdrawProtocolFeeStatus(
            self.rpc_connection.with_method("pdexv3_getWithdrawalProtocolFeeStatus")
                .with_params([{"ReqTxID": tx_id}]).execute())

    def get_staking_status(self, *tx_id):
        return ResponseStakingStatus(
            self.rpc_connection.with_method("pdexv3_getStakingStatus").with_params(tx_id).execute())

    def stake(self, private_k, staking_pool_id, stake_amount, nft_id="", main_tx_receivers=None,
              tx_fee=-1, tx_privacy=1):
        """
        @param private_k:
        @param staking_pool_id:
        @param stake_amount:
        @param nft_id:
        @param main_tx_receivers: dict {burn addr: burn amount}, should test multiple output burn tx
        @param tx_fee:
        @param tx_privacy:
        @return:
        """
        if main_tx_receivers is None:
            main_tx_receivers = {}

        return ResponseStake(
            self.rpc_connection.with_method("pdexv3_txStake")
                .with_params([private_k, main_tx_receivers, tx_fee, tx_privacy,
                              {"StakingPoolID": staking_pool_id,
                               "Amount": stake_amount,
                               "NftID": nft_id}]).execute())

    def unstake(self, private_k, staking_pool_id, nft_id, unstake_amount,
                main_tx_receivers=None, tx_fee=-1, tx_privacy=1):
        """
        @param private_k:
        @param staking_pool_id:
        @param nft_id:
        @param unstake_amount: String num
        @param main_tx_receivers: dict {burn addr: burn amount}, should test multiple output burn tx
        @param tx_fee:
        @param tx_privacy:
        @return:
        """
        return ResponseTxUnstake(self.rpc_connection.with_method("pdexv3_txUnstake")
                                 .with_params([private_k, main_tx_receivers, tx_fee, tx_privacy,
                                               {
                                                   "Amount": unstake_amount,
                                                   "NftID": nft_id,
                                                   "StakingPoolID": staking_pool_id
                                               }]).execute())

    def get_estimated_staking_reward(self, staking_pool_id, nft_id):
        return ResponseEstimatedStakingReward(self.rpc_connection.with_method("pdexv3_getEstimatedStakingReward")
                                              .with_params([{"StakingPoolID": staking_pool_id,
                                                             "NftID": nft_id}]).execute())

    def withdraw_staking_reward(self, private_k, receiver_payment_addr, staking_pool_id, nft_id, token_id=unspecified,
                                sub_tx_receivers=unspecified, sub_tx_privacy=True, token_fee="0", token_tx_type=1,
                                token_amount=1, main_tx_receivers=None, tx_fee=-1, tx_privacy=1):
        """
        @param private_k:
        @param receiver_payment_addr:
        @param staking_pool_id:
        @param nft_id:
        @param token_id: if unspecified, will be nft_id
        @param sub_tx_receivers: should be {burning addr: 1}
        @param sub_tx_privacy:
        @param token_fee:
        @param token_tx_type:
        @param token_amount:
        @param main_tx_receivers:
        @param tx_fee:
        @param tx_privacy:
        @return:
        """
        token_id = nft_id if token_id == unspecified else token_id
        if sub_tx_receivers == unspecified:
            sub_tx_receivers = {Constants.BURNING_ADDR: 1}
        return ResponseWithdraw(self.rpc_connection.with_method("pdexv3_txWithdrawStakingReward")
                                .with_params([private_k, main_tx_receivers, tx_fee, tx_privacy,
                                              {"Privacy": sub_tx_privacy,
                                               "TokenID": token_id,
                                               "TokenTxType": token_tx_type,
                                               "TokenName": "",
                                               "TokenSymbol": "",
                                               "TokenAmount": token_amount,
                                               "TokenReceivers": sub_tx_receivers,
                                               "TokenFee": token_fee,
                                               "StakingPoolID": staking_pool_id,
                                               "NftID": nft_id,
                                               "FeeReceiver": receiver_payment_addr
                                               }, "", 0]).execute())

    def get_withdrawal_staking_reward_status(self, tx_id):
        return ResponseWithdrawStakingRewardStatus(
            self.rpc_connection.with_method("pdexv3_getWithdrawalStakingRewardStatus")
                .with_params([{"ReqTxID": tx_id}]).execute())

    def modify_param(self, centralized_private_k, new_config_dict, main_tx_receivers=None, tx_fee=-1, tx_privacy=1):
        return ResponseModifyParam(
            self.rpc_connection.with_method("pdexv3_txModifyParams")
                .with_params([centralized_private_k, main_tx_receivers, tx_fee, tx_privacy,
                              {"NewParams": new_config_dict}]).execute())

    def get_modify_param_status(self, tx_id):
        return ResponseModifyParamStatus(
            self.rpc_connection.with_method("pdexv3_getParamsModifyingStatus")
                .with_params([{"ReqTxID": tx_id}]).execute())

    def get_pdev3_state(self, beacon_height, key_filter="All", id_filter="1", verbose=1, ):
        return PdeV3State(self.rpc_connection.with_method("pdexv3_getState")
                          .with_params([{"BeaconHeight": beacon_height,
                                         "Filter": {
                                             "Key": key_filter,
                                             "Verbosity": verbose,
                                             "ID": id_filter
                                         }}]).execute())

    def add_liquidity(self, private_k, token_id, amount, amplifier, pool_pair_id="", pair_hash="", nft_id="",
                      main_tx_receivers=unspecified, tx_fee=-1, tx_privacy=1):
        """
        @param private_k:
        @param token_id:
        @param amount: String num
        @param amplifier:
        @param pool_pair_id:
        @param pair_hash:
        @param nft_id:
        @param main_tx_receivers: dict {burn addr: burn amount}, should test multiple output burn tx
        @param tx_fee:
        @param tx_privacy:
        @return:
        """
        main_tx_receivers = {} if main_tx_receivers == unspecified else main_tx_receivers
        return ResponseAddLiquidity(self.rpc_connection.with_method("pdexv3_txAddLiquidity")
                                    .with_params([private_k, main_tx_receivers, tx_fee, tx_privacy,
                                                  {
                                                      "PoolPairID": pool_pair_id,
                                                      "TokenID": token_id,
                                                      "ContributedAmount": amount,
                                                      "PairHash": pair_hash,
                                                      "Amplifier": amplifier,
                                                      "NftID": nft_id
                                                  }]).execute())

    def withdraw_liquidity(self, private_k, pool_pair_id, nft_id, share_amount,
                           main_tx_receivers=None, tx_fee=-1, tx_privacy=1):
        """
        @param nft_id:
        @param private_k:
        @param pool_pair_id:
        @param share_amount: string number
        @param main_tx_receivers: None by default
        @param tx_fee:
        @param tx_privacy:
        @return:
        """
        return ResponseWithdraw(self.rpc_connection.with_method("pdexv3_txWithdrawLiquidity") \
                                .with_params([private_k, main_tx_receivers, tx_fee, tx_privacy,
                                              {"NftID": nft_id,
                                               "PoolPairID": pool_pair_id,
                                               "ShareAmount": share_amount
                                               }]).execute())

    def get_contribution_status(self, tx_id):
        return ResponseContributeStatus(self.rpc_connection.with_method("pdexv3_getContributionStatus")
                                        .with_params([tx_id]).execute())

    def get_withdraw_liquidity_status(self, tx_id):
        return ResponseWithdrawLiquidityStatus(self.rpc_connection.with_method("pdexv3_getWithdrawLiquidityStatus")
                                               .with_params([tx_id]).execute())

    def mint_nft(self, private_k, amount, token_id=Constants.PRV_ID, main_tx_receivers=unspecified, tx_fee=-1,
                 tx_privacy=1):
        """
        @param private_k:
        @param amount: String num
        @param token_id:
        @param main_tx_receivers: default and should be {burn addr: "1"}
        @param tx_fee:
        @param tx_privacy:
        @return:
        """
        if main_tx_receivers == unspecified:
            main_tx_receivers = {Constants.BURNING_ADDR: "1"}
        return ResponseMintNft(self.rpc_connection.with_method("pdexv3_txMintNft")
                               .with_params([private_k, main_tx_receivers, tx_fee, tx_privacy,
                                             {"Amount": amount}]).execute())

    def get_mint_nft_status(self, tx_id):
        return ResponseMintNftStatus(self.rpc_connection.with_method("pdexv3_getMintNftStatus")
                                     .with_params([tx_id]).execute())
