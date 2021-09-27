import copy
import json
from typing import List

from Configs.Configs import ChainConfig
from Drivers.Response import RPCResponseBase
from Helpers import Logging
from Helpers.BlockChainMath import Pde3Math
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
            @property
            def nft_id(self):
                return list(self.dict_data.keys())[0]

            @property
            def amount(self):
                return self.dict_data[self.nft_id]["Amount"]

            @amount.setter
            def amount(self, amount):
                self.dict_data[self.nft_id]["Amount"] = amount

            def get_trading_fee(self, by_token=None):
                all_fee = self.dict_data[self.nft_id]["TradingFees"]
                if by_token:
                    return all_fee[by_token]
                return all_fee

            def get_last_lp_fee_per_share(self, by_token):
                all_fee = self.dict_data[self.nft_id]["LastLPFeesPerShare"]
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

        @staticmethod
        def make_empty_pool(token_list, nft_ids):
            if len(token_list) != 2:
                raise ValueError(f"Expected 2 tokens while get {token_list}")
            nft_ids = nft_ids if isinstance(nft_ids, list) else [nft_ids]
            token_list.sort()
            token_1, token_2 = token_list
            share_datum = {"Amount": 0, "TradingFees": {}, "LastLPFeesPerShare": {}}
            share_data = {nft_id: share_datum for nft_id in nft_ids}
            data = {
                "unknown": {
                    "State": {
                        "Token0ID": token_1,
                        "Token1ID": token_2,
                        "Token0RealAmount": 0,
                        "Token1RealAmount": 0,
                        "Token0VirtualAmount": 0,
                        "Token1VirtualAmount": 0,
                        "Amplifier": 0,
                        "ShareAmount": 0
                    },
                    "Shares": share_data,
                    "Orderbook": {
                        "orders": []
                    },
                    "LpFeesPerShare": {},
                    "ProtocolFees": {},
                    "StakingPoolFees": {
                        "0000000000000000000000000000000000000000000000000000000000000004": 0,
                        token_1: 0,
                        token_2: 0
                    }}}
            return PdeV3State.PoolPairData(data)

        def is_empty_pool(self):
            return self.total_share_amount == 0 and self.amplifier == 0

        def get_pool_pair_id(self):
            return list(self.dict_data.keys())[0]

        def pair_data(self):
            return self.dict_data[self.get_pool_pair_id()]

        def get_state(self, sub_key=None):
            return self.pair_data()["State"][sub_key] if sub_key else self.pair_data()["State"]

        def get_token0_id(self):
            return self.get_state("Token0ID")

        def get_token1_id(self):
            return self.get_state("Token1ID")

        def get_token0_real_amount(self):
            return self.get_state("Token0RealAmount")

        def get_token1_real_amount(self):
            return self.get_state("Token1RealAmount")

        def get_real_amount(self, by_token_id):
            if by_token_id == self.get_token0_id():
                return self.get_token0_real_amount()
            if by_token_id == self.get_token1_id():
                return self.get_token1_real_amount()
            Logging.WARNING(f"Token {by_token_id} does not belong to this pool")

        def get_token0_virtual_amount(self):
            return self.get_state("Token0VirtualAmount")

        def get_token1_virtual_amount(self):
            return self.get_state("Token1VirtualAmount")

        def get_virtual_amount(self, by_token_id):
            if by_token_id == self.get_token0_id():
                return self.get_token0_virtual_amount()
            if by_token_id == self.get_token1_id():
                return self.get_token1_virtual_amount()
            Logging.WARNING(f"Token {by_token_id} does not belong to this pool")

        @property
        def amplifier(self):
            return self.get_state("Amplifier")

        @amplifier.setter
        def amplifier(self, amp):
            self.dict_data[self.get_pool_pair_id()]["State"]["Amplifier"] = amp

        @property
        def total_share_amount(self):
            return self.get_state("ShareAmount")

        @total_share_amount.setter
        def total_share_amount(self, amount):
            self.dict_data[self.get_pool_pair_id()]["State"]["ShareAmount"] = amount

        def get_lp_fee_per_share(self, by_token=None):
            all_fee = self.get_state("LPFeesPerShare")
            return all_fee[by_token] if by_token else all_fee

        def get_protocol_fee(self, by_token=None):
            all_fee = self.get_state("ProtocolFees")
            return all_fee[by_token] if by_token else all_fee

        def get_staking_pool_fee(self, by_token=None):
            all_fee = self.get_state("StakingPoolFees")
            return all_fee[by_token] if by_token else all_fee

        def get_creator_nft_id(self):
            return self.get_pool_pair_id().split('-')[-1]

        def get_share(self, by_nft_id=None):
            """
            @param by_nft_id: leave default (None) to get all share object
            @return: if by_nft_id, return Share object, else return list of Share objects
            """
            all_share = self.pair_data()["Shares"]
            if by_nft_id:
                try:
                    return PdeV3State.PoolPairData.Share({by_nft_id: all_share[by_nft_id]})
                except (KeyError, AttributeError):
                    empty_share = {by_nft_id: {
                        "Amount": 0,
                        "TradingFees": {},
                        "LastLPFeesPerShare": {}}}
                    return PdeV3State.PoolPairData.Share(empty_share)
            all_share_obj = []
            for nft_id, share_data in all_share.items():
                all_share_obj.append(PdeV3State.PoolPairData.Share({nft_id: share_data}))
            return all_share_obj

        def get_order_books(self, by_nft_id=None):
            all_order = self.pair_data()["Orderbook"]["orders"]
            all_order_obj = [PdeV3State.PoolPairData.Order(order) for order in all_order]
            if by_nft_id:
                for order in all_order_obj:
                    if order.get_nft_id() == by_nft_id:
                        return order
                return None
            return all_order_obj

        def set_real_pool(self, token, balance):
            if self.get_token0_id() == token:
                self.get_state()["Token0RealAmount"] = balance
            if self.get_token1_id() == token:
                self.get_state()["Token1RealAmount"] = balance

        def set_virtual_pool(self, token, balance):
            if self.get_token0_id() == token:
                self.get_state()["Token0VirtualAmount"] = balance
            if self.get_token1_id() == token:
                self.get_state()["Token1VirtualAmount"] = balance

        def cal_trade_pool(self, sell_amount, token_sell, token_buy):
            pool_sell = self.get_real_amount(token_sell)
            pool_buy = self.get_real_amount(token_buy)
            v_pool_sell = self.get_virtual_amount(token_sell)
            v_pool_buy = self.get_virtual_amount(token_buy)
            buy_amount = Pde3Math.cal_trade_pool(sell_amount, pool_sell, v_pool_sell, pool_buy, v_pool_buy)
            new_pool_obj = self.clone()
            new_pool_obj.set_virtual_pool(token_sell, v_pool_sell + sell_amount)
            new_pool_obj.set_virtual_pool(token_buy, v_pool_buy - buy_amount)
            new_pool_obj.set_real_pool(token_sell, pool_sell + sell_amount)
            new_pool_obj.set_real_pool(token_buy, pool_buy - buy_amount)
            return buy_amount, new_pool_obj

        def predict_pool_when_add_liquidity(self, amount_dict, nft_id, amp=0):
            """
            @param amp: only use when the self.is_empty_pool() == True, ignore otherwise
            @param amount_dict:
            @param nft_id:
            @return: Share object after contribution, return amount dict {token x: x return, token y: y return}
            """
            all_tok = list(amount_dict.keys())
            if not (self.get_token0_id() in all_tok and self.get_token1_id() in all_tok):
                raise ValueError(f"""Wrong input tokens, cannot calculate.
                Current pair is {self.get_pool_pair_id()}
                While input tokens are: {all_tok}""")
            token_x, token_y = all_tok
            delta_x, delta_y = amount_dict[token_x], amount_dict[token_y]
            current_virtual_x, current_virtual_y = self.get_virtual_amount(token_x), self.get_virtual_amount(token_y)
            current_real_x, current_real_y = self.get_real_amount(token_x), self.get_real_amount(token_y)
            if self.is_empty_pool():  # first time contribute
                self.amplifier = amp
                accepted_x, accepted_y = delta_x, delta_y
                share_added = Pde3Math.cal_share_new_pool(accepted_x, accepted_y)
            else:
                x, y = self.get_real_amount(token_x), self.get_real_amount(token_y)
                accepted_x, accepted_y = Pde3Math.cal_contrib_both_end(delta_x, delta_y, x, y)
                share_added = Pde3Math.cal_share_add_liquidity(self.total_share_amount, accepted_x, accepted_y, x, y)
            accepted_virtual_x = Pde3Math.cal_contribution_virtual(accepted_x,
                                                                   self.amplifier / ChainConfig.Dex3.AMP_DECIMAL)
            accepted_virtual_y = Pde3Math.cal_contribution_virtual(accepted_y,
                                                                   self.amplifier / ChainConfig.Dex3.AMP_DECIMAL)
            return_amount = {token_x: delta_x - accepted_x, token_y: delta_y - accepted_y}
            # predict the pool
            new_pool_obj: PdeV3State.PoolPairData = self.clone()
            new_pool_obj.set_real_pool(token_x, current_real_x + accepted_x)
            new_pool_obj.set_real_pool(token_y, current_real_y + accepted_y)
            new_pool_obj.set_virtual_pool(token_x, current_virtual_x + accepted_virtual_x)
            new_pool_obj.set_virtual_pool(token_y, current_virtual_y + accepted_virtual_y)
            new_pool_obj.total_share_amount += share_added
            # predict contributor's share
            existing_share = new_pool_obj.get_share(nft_id)
            existing_share.amount += share_added
            Logging.INFO(f""" Predicted pool after adding liquidity
            Contributed:
            {json.dumps(amount_dict, indent=3)}
            Return:
            {json.dumps(return_amount, indent=3)}
            Accepted:
            {json.dumps({token_x: accepted_x, token_y: accepted_y}, indent=3)}
            Old | Added | New total share: {self.total_share_amount} | {share_added} | {new_pool_obj.total_share_amount}
            """)
            return new_pool_obj, return_amount

        def cal_sum_share(self):
            return sum([x.amount for x in self.get_share()])

        def _cal_trade_order(self):
            pass

        def predict_pool_after_trade(self, token_sell, sell_amount):
            if token_sell not in [self.get_token0_id(), self.get_token1_id()]:
                raise ValueError(f"Token {token_sell} does not belong to this pair: {self.get_pool_pair_id()}")

    class Param(BlockChainInfoBaseClass):
        def get_default_fee_rate_bps(self):
            return self.dict_data["DefaultFeeRateBPS"]

        def get_fee_rate_bps(self, by_pool_pair=None):
            all_rate = self.dict_data["FeeRateBPS"]
            return all_rate.get(by_pool_pair) if by_pool_pair else all_rate

        def get_prv_discount_percent(self):
            return self.dict_data["PRVDiscountPercent"]

        def get_trading_protocol_fee_percent(self):
            return self.dict_data["TradingProtocolFeePercent"]

        def get_trading_staking_pool_reward_percent(self):
            return self.dict_data["TradingStakingPoolRewardPercent"]

        def get_pdex_reward_pool_pair_share(self, by_pool_pair=None):
            all_reward = self.dict_data["PDEXRewardPoolPairsShare"]
            return all_reward.get(by_pool_pair) if by_pool_pair else all_reward

        def get_staking_pool_share(self, by_token=None):
            all_share = self.dict_data["StakingPoolsShare"]
            return all_share.get(by_token) if by_token else all_share

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
        return all_nft.get(by_nft_id) if by_nft_id else all_nft

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
            filtered_result.append(obj) if included else None

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
            return_list.append(obj) if included else None
        return return_list

    def get_params(self):
        return PdeV3State.Param(self.get_result("Params"))

    def get_pool_pair(self, **by):
        """
        @param by: id, tokens (list of tokens), token0, token1, nft_id, amplifier
        @return:
        """
        by_tokens = by.get("tokens")
        by_token0 = by.get("token0")
        by_token1 = by.get("token1")
        by_id = by.get("id")
        by_nft = ''.join([by.get(key, "") for key in ["nft", "nftid", "nft_id"]])
        by_amp = by.get("amp")
        all_pp = self.get_result("PoolPairs")
        all_pp_obj = [PdeV3State.PoolPairData({pair_id: pair_data}) for pair_id, pair_data in all_pp.items()]
        return_list = []
        if by_id:
            for obj in all_pp_obj:
                if obj.get_pool_pair_id() == by_id:
                    return obj
            return None
        for obj in all_pp_obj:
            included = True
            if by_tokens:
                included = included and (by_tokens == [obj.get_token0_id(), obj.get_token1_id()] or
                                         by_tokens == [obj.get_token1_id(), obj.get_token0_id()])
            else:
                if by_token0:
                    included = included and obj.get_token0_id() == by_token0
                if by_token1:
                    included = included and obj.get_token0_id() == by_token1
            if by_nft:
                included = included and obj.get_share(by_nft)
            if by_amp:
                included = included and obj.amplifier == by_amp
            return_list.append(obj) if included else None
        return return_list

    def estimate_direct_pool_trade(self, sell_amount, token_sell, token_buy):
        direct_pool_rate = self.get_pool_pair(tokens=[token_sell, token_buy])
        pass

    def estimate_cross_pool_trade(self, sell_amount, token_sell, token_buy):
        pass

    def estimate_trade(self, sell_amount, token_sell, token_buy):
        pass
