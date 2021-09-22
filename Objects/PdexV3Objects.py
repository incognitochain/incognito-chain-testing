import copy
from typing import List

from Drivers.Response import RPCResponseBase
from Helpers import Logging
from Objects import BlockChainInfoBaseClass


class PdeV3State(RPCResponseBase):
    class PoolPairData(BlockChainInfoBaseClass):
        """"{
            "0000000000000000000000000000000000000000000000000000000000000004-1411bdcae86863b0c09d94de0c6617d6729f0c5b550f6aac236931b8989207c1-de7cee45ee7be4f179592feaf79b1fbc5c1e96baad5bcb17d265b08bf32cf09e": {
                "State": {
                    "Token0ID": "0000000000000000000000000000000000000000000000000000000000000004",
                    "Token1ID": "1411bdcae86863b0c09d94de0c6617d6729f0c5b550f6aac236931b8989207c1",
                    "Token0RealAmount": 16970667777,
                    "Token1RealAmount": 8485230063,
                    "Token0VirtualAmount": 33941231692,
                    "Token1VirtualAmount": 16970512023,
                    "Amplifier": 20000,
                    "ShareAmount": 12000000839,
                    "LPFeesPerShare": {
                        "0000000000000000000000000000000000000000000000000000000000000004": 47475468957
                    },
                    "ProtocolFees": {
                        "0000000000000000000000000000000000000000000000000000000000000004": 0
                    },
                    "StakingPoolFees": {}
                },
                "Shares": {
                    "e55476d221e72bf5950bbc60ccf43ae35f5a38fd89ee0d7273e28313b8e1d248": {
                        "Amount": 12000000839,
                        "TradingFees": {
                            "0000000000000000000000000000000000000000000000000000000000000004": 498
                        },
                        "LastLPFeesPerShare": {
                            "0000000000000000000000000000000000000000000000000000000000000004": 47475468957
                        }
                    }
                },
                "Orderbook": {
                    "orders": [{
                            "Id": "b832a5dbc0dad6fb8d36d56e4754f9a1b8e05ba2ae90e8b149f468cd200d390c",
                            "NftID": "ef72a79eaa139376068e2e6ac949ded22ee6aa1262794802ea59d2402e635961",
                            "Token0Rate": 668,
                            "Token1Rate": 100,
                            "Token0Balance": 668,
                            "Token1Balance": 0,
                            "TradeDirection": 0,
                            "Fee": 0
                        },
                        {
                            "Id": "a36943bb6aa3a5f6a7bd73e775a7cef07d29d9051797b39d48e9c7ea794c2ffd",
                            "NftID": "ef72a79eaa139376068e2e6ac949ded22ee6aa1262794802ea59d2402e635961",
                            "Token0Rate": 667,
                            "Token1Rate": 100,
                            "Token0Balance": 667,
                            "Token1Balance": 0,
                            "TradeDirection": 0,
                            "Fee": 0
                        }
                    ]
                }
            }"""

        class Share(BlockChainInfoBaseClass):
            def get_nft_id(self):
                return list(self.dict_data.keys())[0]

            def get_amount(self):
                return self.dict_data[self.get_nft_id()]["Amount"]

            def get_trading_fee(self, by_token=None):
                all_fee = self.dict_data[self.get_nft_id()]["TradingFees"]
                if by_token:
                    return all_fee[by_token]
                return all_fee

            def get_last_lp_fee_per_share(self, by_token):
                all_fee = self.dict_data[self.get_nft_id()]["LastLPFeesPerShare"]
                if by_token:
                    return all_fee[by_token]
                return all_fee

        class Order(BlockChainInfoBaseClass):
            """{
                            "Id": "b832a5dbc0dad6fb8d36d56e4754f9a1b8e05ba2ae90e8b149f468cd200d390c",
                            "NftID": "ef72a79eaa139376068e2e6ac949ded22ee6aa1262794802ea59d2402e635961",
                            "Token0Rate": 668,
                            "Token1Rate": 100,
                            "Token0Balance": 668,
                            "Token1Balance": 0,
                            "TradeDirection": 0,
                            "Fee": 0
                        }"""

            def get_id(self):
                return self.dict_data["Id"]

            def get_nft_id(self):
                return self.dict_data["NftID"]

            def get_token0_rate(self):
                return self.dict_data["Token0Rate"]

            def get_token1_rate(self):
                return self.dict_data["Token1Rate"]

            def get_token0_balance(self):
                return self.dict_data["Token0Balance"]

            def get_token1_balance(self):
                return self.dict_data["Token1Balance"]

            def get_trade_direction(self):
                return self.dict_data["TradeDirection"]

            def get_fee(self):
                return self.dict_data["Fee"]

            def get_rate(self):
                if self.get_trade_direction() == 0:
                    return self.get_token1_rate() / self.get_token0_rate()
                else:
                    return self.get_token0_rate() / self.get_token1_rate()

        def get_pool_pair_id(self):
            return list(self.dict_data.keys())[0]

        def __pair_data(self):
            return self.dict_data[self.get_pool_pair_id()]

        def get_state(self):
            return self.__pair_data()["State"]

        def get_state_token_id_0(self):
            return self.get_state()["Token0ID"]

        def get_state_token_id_1(self):
            return self.get_state()["Token1ID"]

        def get_state_token0_real_amount(self):
            return self.get_state()["Token0RealAmount"]

        def get_state_token1_real_amount(self):
            return self.get_state()["Token1RealAmount"]

        def get_real_amount(self, by_token_id):
            if by_token_id == self.get_state_token_id_0():
                return self.get_state_token0_real_amount()
            if by_token_id == self.get_state_token_id_1():
                return self.get_state_token1_real_amount()
            Logging.WARNING(f"Token {by_token_id} does not belong to this pool")

        def get_state_token0_virtual_amount(self):
            return self.get_state()["Token0VirtualAmount"]

        def get_state_token1_virtual_amount(self):
            return self.get_state()["Token1VirtualAmount"]

        def get_virtual_amount(self, by_token_id):
            if by_token_id == self.get_state_token_id_0():
                return self.get_state_token0_virtual_amount()
            if by_token_id == self.get_state_token_id_1():
                return self.get_state_token1_virtual_amount()
            Logging.WARNING(f"Token {by_token_id} does not belong to this pool")

        def get_amplifier(self):
            return self.get_state()["Amplifier"]

        def get_share_amount(self):
            return self.get_state()["ShareAmount"]

        def get_lp_fee_per_share(self, by_token=None):
            all_fee = self.get_state()["LPFeesPerShare"]
            return all_fee[by_token] if by_token else all_fee

        def get_protocol_fee(self, by_token=None):
            all_fee = self.get_state()["ProtocolFees"]
            return all_fee[by_token] if by_token else all_fee

        def get_staking_pool_fee(self, by_token=None):
            all_fee = self.get_state()["StakingPoolFees"]
            return all_fee[by_token] if by_token else all_fee

        def get_share(self, by_nft_id=None):
            all_share = self.__pair_data()["Shares"]
            if by_nft_id:
                try:
                    return PdeV3State.PoolPairData.Share({by_nft_id: all_share[by_nft_id]})
                except (KeyError, AttributeError):
                    return None
            all_share_obj = []
            for nft_id, share_data in all_share.items():
                all_share_obj.append(PdeV3State.PoolPairData.Share({nft_id: share_data}))
            return all_share_obj

        def get_order_books(self, by_nft_id=None):
            all_order = self.__pair_data()["Orderbook"]["orders"]
            all_order_obj = [PdeV3State.PoolPairData.Order(order) for order in all_order]
            if by_nft_id:
                for order in all_order_obj:
                    if order.get_nft_id() == by_nft_id:
                        return order
                return None
            return all_order_obj

        def _cal_trade_pool(self):
            pass

        def _cal_trade_order(self):
            pass

        def cal_trade(self):
            pass

    class Param(BlockChainInfoBaseClass):
        def get_default_fee_rate_bps(self):
            return self.dict_data["DefaultFeeRateBPS"]

        def get_fee_rate_bps(self, by_pool_pair=None):
            all_rate = self.dict_data["FeeRateBPS"]
            if by_pool_pair:
                return all_rate.get(by_pool_pair)
            return all_rate

        def get_prv_discount_percent(self):
            return self.dict_data["PRVDiscountPercent"]

        def get_trading_protocol_fee_percent(self):
            return self.dict_data["TradingProtocolFeePercent"]

        def get_trading_staking_pool_reward_percent(self):
            return self.dict_data["TradingStakingPoolRewardPercent"]

        def get_pdex_reward_pool_pair_share(self, by_pool_pair=None):
            all_reward = self.dict_data["PDEXRewardPoolPairsShare"]
            if by_pool_pair:
                return all_reward.get(by_pool_pair)
            return all_reward

        def get_staking_pool_share(self, by_token=None):
            all_share = self.dict_data["StakingPoolsShare"]
            if by_token:
                return all_share.get(by_token)
            return all_share

        def get_staking_reward_token(self):
            return self.dict_data["StakingRewardTokens"]

        def get_mint_nft_require_amount(self):
            return self.dict_data["MintNftRequireAmount"]

        def get_max_order_per_nft(self):
            return self.dict_data["MaxOrdersPerNft"]

        def data_convert(self, to_class=str):
            """
            @param to_class: accept str or int only
            @return: new dict which has all number converted to string
            """
            to_class = str if to_class == 'str' else to_class
            to_class = int if to_class == 'int' else to_class
            if not (to_class is str or to_class is int):
                raise ValueError("to_class argument only accepts 'str' or 'int'")

            def convert(d, to):
                for key, value in d.items():
                    if isinstance(value, dict):
                        convert(value, to)
                    elif isinstance(value, list):
                        value = [convert(item, to) if isinstance(item, dict) else str(item) for item in value]
                    else:
                        try:
                            d[key] = to(value)
                        except ValueError:  # ignore if cannot convert
                            pass

            return_dict = copy.deepcopy(self.dict_data)
            convert(return_dict, to_class)
            return return_dict

    class StakingPool(BlockChainInfoBaseClass):
        """"0000000000000000000000000000000000000000000000000000000000000004": {
                "Liquidity": 100,
                "Stakers": {
                    "e55476d221e72bf5950bbc60ccf43ae35f5a38fd89ee0d7273e28313b8e1d248": {
                        "Liquidity": 100,
                        "Rewards": {},
                        "LastRewardsPerShare": {}
                    }
                },
                "RewardsPerShare": {}
            }"""

        class Staker(BlockChainInfoBaseClass):
            def get_nft_id(self):
                return self._1_item_dict_key()

            def get_liquidity(self):
                return self._1_item_dict_value()["Liquidity"]

            def get_reward(self, *args): pass  # todo TBD, not yet have sample response

            def get_last_reward_per_share(self, *args): pass  # todo TBD, not yet have sample response

        def get_token_id(self):
            return self._1_item_dict_key()

        def get_liquidity(self):
            return self._1_item_dict_value()["Liquidity"]

        def get_stakers(self, by_nft_id=None):
            all_stakers = self._1_item_dict_value()["Stakers"]
            all_stakers_obj = [PdeV3State.StakingPool.Staker({nft_id: staker_data}) for nft_id, staker_data in
                               all_stakers.items()]

            if by_nft_id:
                for obj in all_stakers_obj:
                    if by_nft_id and obj.get_nft_id() == by_nft_id:
                        return obj
                return None
            return all_stakers_obj

    class Contribution(BlockChainInfoBaseClass):
        """"TK1_Z1UbH-TK1_pjBEx": {
        "PoolPairID": "",
        "OtaReceiver": "15ZUQX2Yk7PH8PWLqfcP9fzuEVfeGy5y2A3DY8gtHtW8NRz9SCe4y9q5Bg8gC3hqBUDHAeEKD2Gv7SRMFQqe47jGLNzKgQeyKpK2yAvLRJdGBNgHJFDFCTQtE3VVbeBbjPpGfAj4yEjDFFVH",
        "TokenID": "92f9e5aa0683568d041af306d8b029f919bb1cd432241fd751b6f0a8ac0ccc98",
        "Amount": 1000000000,
        "Amplifier": 10000,
        "TxReqID": "e150a6ac7a28a7641505dbee64bd51f5ea522128922c6024e9d618ee5f8bc517",
        "NftID": "1d307f116c6374a246345dac7d9c09c1481d93243bcc388da8861603579336c1",
        "ShardID": 1
         },"""

        def __init__(self, data):
            l_id = len(self.dict_data.keys())
            if l_id != 1:
                raise ValueError(f"This waiting contribution has {l_id} id while expecting only 1: data {data}")
            super().__init__(data)

        def get_contribution_id(self):
            return list(self.dict_data.keys())[0]

        def __contrib_info(self):
            return self.dict_data[self.get_contribution_id()]

        def get_pool_pair_id(self):
            return self.__contrib_info()["PoolPairID"]

        def get_ota_receiver(self):
            return self.__contrib_info()["OtaReceiver"]

        def get_token_id(self):
            return self.__contrib_info()["TokenID"]

        def get_amount(self):
            return self.__contrib_info()["Amount"]

        def get_amplifier(self):
            return self.__contrib_info()["Amplifier"]

        def get_tx_req_id(self):
            return self.__contrib_info()["TxReqID"]

        def get_nft_id(self):
            return self.__contrib_info()["NftID"]

        def get_shard_id(self):
            return self.__contrib_info()["ShardID"]

    def get_nft_id(self, by_nft_id=None):
        """
        @param by_nft_id: if None, return dict of NTF ids. If not None, find NFT id entry and return the value, if not
        found, return None.
        @return:
        """
        all_nft = self.get_result("NftIDs")
        if by_nft_id:
            return all_nft.get(by_nft_id)
        return all_nft

    def get_waiting_contribution(self, by_contrib_id=None, by_token_id=None, by_nft_id=None):
        all_waiting = self.get_result("WaitingContributions")
        all_waiting_obj = [PdeV3State.Contribution({contrib_id: info}) for contrib_id, info in all_waiting.items()]
        filtered_result = []
        for obj in all_waiting_obj:
            included = True
            if by_contrib_id:
                included = included and obj.get_contribution_id() == by_contrib_id
            if by_token_id:
                included = included and obj.get_token_id() == by_token_id
            if by_nft_id:
                included = included and obj.get_nft_id() == by_nft_id
            if included:
                filtered_result.append(obj)

    def get_staking_pools(self, by_token=None, by_nft_id=None) -> List[StakingPool]:
        all_pool = self.get_result("StakingPools")
        all_pool_obj = [PdeV3State.StakingPool({token_id: pool_data}) for token_id, pool_data in all_pool.items()]
        return_list = []
        for obj in all_pool_obj:
            included = True
            if by_token:
                included = included and obj.get_token_id() == by_token
            if by_nft_id:
                included = included and obj.get_stakers(by_nft_id)
            if included:
                return_list.append(obj)

        return return_list

    def get_params(self):
        return PdeV3State.Param(self.get_result("Params"))

    def get_pool_pair(self, **by):
        """
        @param by: tokens (list of tokens), token0, token1, nft_id
        @return:
        """
        by_tokens = by.get("tokens")
        by_token0 = by.get("token0")
        by_token1 = by.get("token1")
        by_nft = None
        for nft_name in ["nft", "nftid", "nft_id"]:
            by_nft = by.get(nft_name)
            if by_nft:
                break
        all_pool_pair = self.get_result("PoolPairs")
        all_pool_pair_obj = [PdeV3State.PoolPairData({pair_id: pair_data})
                             for pair_id, pair_data in all_pool_pair.items()]

        return_list = []
        for obj in all_pool_pair_obj:
            included = True
            if by_tokens:
                included = included and (by_tokens == [obj.get_state_token_id_0(), obj.get_state_token_id_1()] or
                                         by_tokens == [obj.get_state_token_id_1(), obj.get_state_token_id_0()])
            else:
                if by_token0:
                    included = included and obj.get_state_token_id_0() == by_token0
                if by_token1:
                    included = included and obj.get_state_token_id_0() == by_token1
            if by_nft:
                included = included and obj.get_share(by_nft)
            if included:
                return_list.append(obj)
        return return_list

    def estimate_direct_pool_trade(self, sell_amount, token_sell, token_buy):
        direct_pool_rate = self.get_pool_pair(tokens=[token_sell, token_buy])
        pass

    def estimate_cross_pool_trade(self, sell_amount, token_sell, token_buy):
        pass

    def estimate_trade(self, sell_amount, token_sell, token_buy):
        pass
