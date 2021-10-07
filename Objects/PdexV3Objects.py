import copy
import json
from typing import List

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

            def __str__(self):
                return f"   Order ID: {self.get_id()} \n      " \
                       f"NFT ID: {self.get_nft_id()} \n      " \
                       f"Balance sell|buy: {self.get_balance_token_sell()} | {self.get_balance_token_buy()}\n      " \
                       f"Rate sell|buy   : {self.get_rate_token_sell()} | {self.get_rate_token_buy()}. " \
                       f"order rate {self.get_order_rate()}, buy rate {self.get_buy_rate()}"

            def get_id(self):
                return self.dict_data["Id"]

            def get_nft_id(self):
                return self.dict_data["NftID"]

            def get_token_rate(self, index):
                return self.dict_data["Token0Rate"] if index == 0 else self.dict_data["Token1Rate"]

            def get_token_balance(self, index):
                return self.dict_data["Token0Balance"] if index == 0 else self.dict_data["Token1Balance"]

            def _set_balance(self, bal_sell, bal_buy):
                self.dict_data[f"Token{self.get_trade_direction()}Balance"] = bal_sell
                self.dict_data[f"Token{1 - self.get_trade_direction()}Balance"] = bal_buy

            def get_trade_direction(self):
                return self.dict_data["TradeDirection"]

            def get_fee(self):
                return self.dict_data["Fee"]

            def get_order_rate(self):
                return self.get_rate_token_buy() / self.get_rate_token_sell()

            def get_buy_rate(self):
                return self.get_rate_token_sell() / self.get_rate_token_buy()

            def get_rate_token_sell(self):
                return self.get_token_rate(self.get_trade_direction())

            def get_rate_token_buy(self):
                return self.get_token_rate(1 - self.get_trade_direction())

            def get_balance_token_sell(self):
                return self.get_token_balance(self.get_trade_direction())

            def get_balance_token_buy(self):
                return self.get_token_balance(1 - self.get_trade_direction())

            def is_completed(self):
                completed = self.get_balance_token_sell() == 0
                Logging.INFO(f"Order {self.get_id()} is completed") if completed else None
                return completed

            def is_valid(self):
                check = self.get_balance_token_buy() == \
                        (self.get_rate_token_sell() - self.get_balance_token_sell()) * self.get_order_rate() \
                        and self.get_order_rate() > 0
                Logging.INFO(f"Order: {self.get_id()}\n\t"
                             f"valid = {check}")
                return check

            def is_un_touched(self):
                check = self.get_balance_token_buy() == 0 and \
                        self.get_balance_token_sell() == self.get_rate_token_sell()
                Logging.INFO(f"Order: {self.get_id()} \n\t"
                             f"un-touched = {check} , Bal buy: {self.get_balance_token_buy()}, "
                             f"Rate sell: {self.get_rate_token_sell()}, "
                             f"Rate buy: {self.get_rate_token_buy()}")
                return check

            def trade_this_order(self, sell_amount):
                """
                @param sell_amount:
                @return: receive amount, remain amount also update the current balance of the order object
                """
                Logging.INFO(f"\n  Calculate trade receive, remain and predict order after trade\n{self}")
                used_amount = min(sell_amount, self.get_rate_token_buy() - self.get_balance_token_buy())
                receive_amount = round(used_amount * self.get_buy_rate())
                bal_sell_remain = self.get_balance_token_sell() - receive_amount
                bal_buy_remain = self.get_balance_token_buy() + used_amount
                remain = sell_amount - used_amount
                self._set_balance(bal_sell_remain, bal_buy_remain)
                Logging.INFO(f"Trade amount {sell_amount}, used: {used_amount}, remain {remain}")
                Logging.INFO(f"Order after trade: \n"
                             f"{self}")
                return receive_amount, remain

        @staticmethod
        def make_up_a_pool(token_list, nft_ids):
            if len(token_list) != 2:
                raise ValueError(f"Expected 2 tokens while get {token_list}")
            nft_ids = nft_ids if isinstance(nft_ids, list) else [nft_ids]
            token_list.sort()
            share_datum = {"Amount": 0, "TradingFees": {}, "LastLPFeesPerShare": {}}
            share_data = {nft_id: share_datum for nft_id in nft_ids}
            data = {
                "unknown": {
                    "State": {
                        "Token0ID": token_list[0],
                        "Token1ID": token_list[1],
                        "Token0RealAmount": 0,
                        "Token1RealAmount": 0,
                        "Token0VirtualAmount": 0,
                        "Token1VirtualAmount": 0,
                        "Amplifier": 0,
                        "ShareAmount": 0
                    },
                    "Shares": share_data,
                    "Orderbook": {
                        # "orders": []
                    },
                    "LpFeesPerShare": {},
                    "ProtocolFees": {},
                    "StakingPoolFees": {
                        "0000000000000000000000000000000000000000000000000000000000000004": 0,
                        token_list[0]: 0,
                        token_list[1]: 0
                    }}}
            return PdeV3State.PoolPairData(data)

        def _get_token_index(self, token):
            if self.get_token_id(0) == token:
                return 0
            elif self.get_token_id(1) == token:
                return 1
            else:
                raise ValueError(f"Token {token}, does not belong to this pool.\n{self.get_pool_pair_id()}")

        def is_made_up_pool(self):
            """check if the pool is made up by self.make_up_a_pool()"""
            return self.total_share_amount == self.amplifier == 0 and self.get_pool_pair_id() == "unknown"

        def is_empty_pool(self):
            """check if the pool is withdrawn completely"""
            return self.total_share_amount == self.get_real_amount(0) == self.get_real_amount(1) == \
                   self.get_virtual_amount(0) == self.get_virtual_amount(1) == 0

        def get_pool_pair_id(self):
            return list(self.dict_data.keys())[0]

        def pair_data(self):
            return self.dict_data[self.get_pool_pair_id()]

        def get_state(self, sub_key=None):
            return self.pair_data()["State"][sub_key] if sub_key else self.pair_data()["State"]

        def get_token_id(self, index=None):
            """
            @param index:
            @return: Token id by index, or both if index is unspecified (None)
            """
            return self.get_state(f"Token{index}ID") if index is not None \
                else tuple(self.get_state(f"Token{i}ID") for i in [0, 1])

        def get_real_amount(self, by_token_id):
            """
            @param by_token_id: token id or index (0,1)
            @return:
            """
            if by_token_id == self.get_token_id(0) or by_token_id == 0:
                return self.get_state("Token0RealAmount")
            if by_token_id == self.get_token_id(1) or by_token_id == 1:
                return self.get_state("Token1RealAmount")
            Logging.WARNING(f"Token {by_token_id} does not belong to this pool")

        def get_virtual_amount(self, by_token_id):
            if by_token_id == self.get_token_id(0) or by_token_id == 0:
                return self.get_state("Token0VirtualAmount")
            if by_token_id == self.get_token_id(1) or by_token_id == 1:
                return self.get_state("Token1VirtualAmount")
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

        def get_order_books(self, **by):
            """
            @param by: id, nft_id (nft or nftid), direction, token_sell (or sell)
            @return:
            """
            all_order = self.pair_data()["Orderbook"]["orders"]
            all_order_obj = [PdeV3State.PoolPairData.Order(order) for order in all_order]
            by_id = by.get("id")
            if by_id:
                for obj in all_order_obj:
                    if obj.get_id() == by_id:
                        return obj
                return None

            by_nft_id = by.get("nft_id", by.get("nft", by.get("nftid")))
            by_direction = by.get("direction", by.get("trade_direction"))
            by_token_sell = by.get("token_sell", by.get("sell"))
            return_obj_list = []
            for obj in all_order_obj:
                include = True
                if by_nft_id:
                    include = include and obj.get_nft_id() == by_nft_id
                if by_direction is not None:
                    include = include and obj.get_trade_direction() == by_direction
                    print(f"by dir {obj.get_id()}: {include}")
                if by_token_sell:
                    include = include and obj.get_trade_direction() == self._get_token_index(by_token_sell)
                print("final ", include)
                return_obj_list.append(obj) if include else None

            return return_obj_list

        def set_real_pool(self, token, balance):
            if self.get_token_id(0) == token:
                self.get_state()["Token0RealAmount"] = balance
            if self.get_token_id(1) == token:
                self.get_state()["Token1RealAmount"] = balance

        def set_virtual_pool(self, token, balance):
            if self.get_token_id(0) == token:
                self.get_state()["Token0VirtualAmount"] = balance
            if self.get_token_id(1) == token:
                self.get_state()["Token1VirtualAmount"] = balance

        def cal_trade_receive(self, sell_amount, sell_token):
            if sell_token == self.get_token_id(1):
                buy__token = self.get_token_id(0)
            elif sell_token == self.get_token_id(0):
                buy__token = self.get_token_id(1)
            else:
                raise ValueError(f"Sell token {sell_token} does not belong to this pool pair")

            token_buy_index = 1 - self._get_token_index(sell_token)
            token_buy = self.get_token_id(token_buy_index)
            receive_amount = Pde3Math \
                .cal_trade_pool(sell_amount,
                                self.get_real_amount(sell_token), self.get_virtual_amount(sell_token),
                                self.get_real_amount(buy__token), self.get_virtual_amount(buy__token))
            self.set_real_pool(sell_token, self.get_real_amount(sell_token) + sell_amount)
            self.set_virtual_pool(sell_token, self.get_virtual_amount(sell_token) + sell_amount)
            self.set_real_pool(token_buy, self.get_real_amount(token_buy) - receive_amount)
            self.set_virtual_pool(token_buy, self.get_virtual_amount(token_buy) - receive_amount)
            return receive_amount

        def cal_distant_to_order(self, token_sell, order):
            tok_sell_index = self._get_token_index(token_sell)
            tok_buy_index = 1 - self._get_token_index(token_sell)
            tok_sell_bal = order.get_balance_token_sell()
            tok_buy_bal = order.get_balance_token_buy()
            if tok_buy_bal == 0 or tok_sell_bal == 0:
                x_sell = order.get_rate_token_sell()
                y_buy = order.get_rate_token_buy()
            else:
                x_sell = tok_sell_bal
                y_buy = tok_buy_bal
            return Pde3Math.cal_distance_to_order_book(
                self.get_virtual_amount(tok_sell_index), self.get_virtual_amount(tok_buy_index), y_buy, x_sell)

        def predict_pool_after_trade(self, sell_amount, token_sell):
            """ NOTICE that AMM pool must not be Null []
            @param sell_amount:
            @param token_sell:
            @return: receive amount
            """
            token_sell_index = self._get_token_index(token_sell)
            token_buy_index = abs(1 - token_sell_index)
            amm_rate = self.get_pool_rate(token_sell)
            orders = sorted(self.get_order_books(direction=token_buy_index), key=lambda o: o.get_buy_rate())
            if not orders:
                receive_amount = self.cal_trade_receive(sell_amount, token_sell)
                return receive_amount, self

            right_orders, left_orders = [], []
            for order in orders:
                right_orders.append(order) if order.get_buy_rate() >= amm_rate else left_orders.append(order)

            Logging.INFO(f"LEFT {'=' * 40}")
            [Logging.INFO(f"{o.get_id()} {o.get_buy_rate()}") for o in left_orders]
            Logging.INFO(f"RIGHT {'=' * 40}")
            [Logging.INFO(f"{o.get_id()} {o.get_buy_rate()}") for o in right_orders]
            Logging.INFO("=" * 80)
            Logging.INFO(f"Sell amount: {sell_amount}")

            total_receive = 0
            # trade right orders first
            while sell_amount > 0 and right_orders:
                best_order = right_orders[-1]
                Logging.INFO(
                    f"Trading best rate order book {best_order.get_id()}, rate {best_order.get_buy_rate()}")
                Logging.DEBUG(best_order)
                receive, remain = best_order.trade_this_order(sell_amount)
                total_receive += receive
                Logging.INFO(f"After trade order: traded {sell_amount}, remain {remain}, sum receive {total_receive}")
                sell_amount = remain  # more explicit than receive, sell_amount = best_order.trade(sell_amount)
                if best_order.is_completed():
                    right_orders.pop()

            while sell_amount > 0 and left_orders:
                # trade amm with amount = distance to next order
                next_order = left_orders[-1]
                Logging.INFO(f"next ORDER: {next_order}")
                distance = self.cal_distant_to_order(token_sell, next_order)
                Logging.INFO(f"Distance : {distance}")
                if 0 < sell_amount <= distance:
                    Logging.INFO(f"**Trade {sell_amount} (sell-amount) with pool**")
                    total_receive += self.cal_trade_receive(sell_amount, token_sell)
                    sell_amount = 0
                    return total_receive, self
                elif sell_amount > distance:
                    Logging.INFO(f"**Trade {distance} (distance) with pool**")
                    total_receive += self.cal_trade_receive(distance, token_sell)
                    sell_amount -= distance

                # trade left orders
                Logging.INFO(f"**Trade {sell_amount} w left orders list")
                receive, remain = next_order.trade_this_order(sell_amount)
                if next_order.is_completed():
                    left_orders.pop()

                total_receive += receive
                sell_amount = remain

            if sell_amount > 0:
                Logging.INFO(f"Still have token left to trade, continue trading {sell_amount} with pool")
                total_receive += self.cal_trade_receive(sell_amount, token_sell)

            return total_receive

        def predict_pool_when_add_liquidity(self, amount_dict, nft_id, amp=0):
            """
            @param amp: only use when the self.is_empty_pool() == True (first time contribution), ignore otherwise
            @param amount_dict:
            @param nft_id:
            @return: amount dict {token x: x return, token y: y return}
            """
            all_tok = list(amount_dict.keys())
            if not (self.get_token_id(0) in all_tok and self.get_token_id(1) in all_tok):
                raise ValueError(f"Wrong input tokens, cannot calculate.\n"
                                 f"Current pair is {self.get_pool_pair_id()}\n"
                                 f"While input tokens are: {all_tok}")
            token_x, token_y = all_tok
            delta_x, delta_y = amount_dict[token_x], amount_dict[token_y]
            virtual_x, virtual_y = self.get_virtual_amount(token_x), self.get_virtual_amount(token_y)
            current_real_x, current_real_y = self.get_real_amount(token_x), self.get_real_amount(token_y)
            if self.is_made_up_pool():  # first time contribute
                Logging.INFO("First time contribution for this pair\n\t"
                             f"{self.get_pool_pair_id()}\n\t"
                             f"NFT ID = {nft_id}")
                self.amplifier = amp
                accepted_x, accepted_y = delta_x, delta_y
                delta_share = Pde3Math.cal_share_new_pool(accepted_x, accepted_y)
            else:
                Logging.INFO("Contribute more to this pair")
                x, y = self.get_real_amount(token_x), self.get_real_amount(token_y)
                accepted_x, accepted_y, delta_share = \
                    Pde3Math.cal_contrib_both_end(self.total_share_amount, delta_x, delta_y, x, y)
            new_total_share = self.total_share_amount + delta_share
            new_virtual_x = Pde3Math.cal_virtual_after_contribution(virtual_x, self.total_share_amount, new_total_share)
            new_virtual_y = Pde3Math.cal_virtual_after_contribution(virtual_y, self.total_share_amount, new_total_share)
            return_amount = {token_x: delta_x - accepted_x, token_y: delta_y - accepted_y}
            # predict the pool
            self.set_real_pool(token_x, current_real_x + accepted_x)
            self.set_real_pool(token_y, current_real_y + accepted_y)
            self.set_virtual_pool(token_x, new_virtual_x)
            self.set_virtual_pool(token_y, new_virtual_y)
            self.total_share_amount += delta_share
            # predict contributor's share
            existing_share = self.get_share(nft_id)
            existing_share.amount += delta_share
            Logging.INFO("Predicted pool after adding liquidity \n\t"
                         f"Contributed: \n\t\t {json.dumps(amount_dict, indent=3)}\n\t"
                         f"Return:\n\t\t {json.dumps(return_amount, indent=3)}\n\t"
                         f"Accepted:\n\t\t {json.dumps({token_x: accepted_x, token_y: accepted_y}, indent=3)}\n\t"
                         f"Old | Added | New total share: "
                         f"{self.total_share_amount} | {delta_share} | {self.total_share_amount}")
            return return_amount

        def get_pool_rate(self, token_sell):
            token_buy_index = 1 - self._get_token_index(token_sell)
            return self.get_virtual_amount(token_buy_index) / self.get_virtual_amount(token_sell)

        def sum_all_share(self):
            return sum([x.amount for x in self.get_share()])

        def cal_share_by_real_pool(self):
            return Pde3Math.cal_share_new_pool(self.get_real_amount(0), self.get_real_amount(1))

        def predict_pool_after_withdraw_share(self, withdraw_amount, nft_id):
            """
            @param withdraw_amount:
            @param nft_id:
            @return: dict receive {token x: amount, token y: amount}
            """
            token_x, token_y = self.get_token_id(0), self.get_token_id(1)
            my_share = self.get_share(nft_id)
            my_current_share = my_share.amount
            withdraw_able = min(withdraw_amount, my_current_share)
            x_real = self.get_real_amount(token_x)
            y_real = self.get_real_amount(token_y)
            x_virtual = self.get_virtual_amount(token_x)
            y_virtual = self.get_virtual_amount(token_y)
            Logging.INFO(f"NFT: {nft_id}\n\t"
                         f"Want to withdraw share {withdraw_amount}, while has {my_current_share}, "
                         f"able to withdraw {withdraw_able}")
            x_receive, y_receive = Pde3Math.cal_withdraw_share(withdraw_able, x_real, y_real, self.total_share_amount)
            x_real_new = x_real - x_receive
            y_real_new = y_real - y_receive
            remain_share_total = self.total_share_amount - withdraw_able
            self.set_real_pool(token_x, x_real_new)
            self.set_real_pool(token_y, y_real_new)
            x_virtual_new = max(x_real_new, int(remain_share_total * x_virtual / self.total_share_amount))
            y_virtual_new = max(y_real_new, int(remain_share_total * y_virtual / self.total_share_amount))
            self.set_virtual_pool(token_x, x_virtual_new)
            self.set_virtual_pool(token_y, y_virtual_new)
            self.total_share_amount = remain_share_total
            # update user share
            my_share = self.get_share(nft_id)
            my_share.amount -= withdraw_able
            return {token_x: x_receive, token_y: y_receive}

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
        @param by: id, tokens (list of tokens, max 2), token0, token1, nft_id, amplifier
        @return:
        """
        by_tokens = by.get("tokens")
        by_token0 = by.get("token0")
        by_token1 = by.get("token1")
        by_id = by.get("id", by.get("pair_id", by.get("pool_id", by.get("pairid", by.get("poolid")))))
        by_nft = by.get("nft_id", by.get("nft", by.get("nftid")))
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
                matched = sum([x in [obj.get_token_id(0), obj.get_token_id(1)] for x in by_tokens]) == len(by_tokens)
                included = included and matched
            else:
                if by_token0:
                    included = included and obj.get_token_id(0) == by_token0
                if by_token1:
                    included = included and obj.get_token_id(0) == by_token1
            if by_nft:
                included = included and obj.get_share(by_nft)
            if by_amp:
                included = included and obj.amplifier == by_amp
            return_list.append(obj) if included else None
        return return_list

    def pre_dict_state_after_trade(self, sell_token, sell_amount, trade_path):
        for pair_id in trade_path:
            pool = self.get_pool_pair(id=pair_id)
            pool.predict_pool_after_trade(sell_amount, sell_token)
