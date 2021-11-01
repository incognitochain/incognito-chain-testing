import copy
import math


class PdeMath:
    @staticmethod
    def cal_withdraw_share(share_mount_withdraw, available_share, total_share, pde_pool):
        """
        @param share_mount_withdraw: amount user want to withdraw
        @param available_share: current share of user
        @param total_share: total share of pool
        @param pde_pool:
        @return: tuple(receive mount token1, receive amount token2)
        """
        withdraw_amount = min(share_mount_withdraw, available_share)
        receive_amount_token1 = int((withdraw_amount / total_share) * pde_pool[0])
        receive_amount_token2 = int((withdraw_amount / total_share) * pde_pool[1])
        return receive_amount_token1, receive_amount_token2

    @staticmethod
    def cal_contribution(token_1_contribute_amount, token_2_contribute_amount, current_pool: list):
        """

        @param token_1_contribute_amount:
        @param token_2_contribute_amount:
        @param current_pool: [token1_pool, token2_pool]
        @return: (actual_contrib_amount1,  actual_contrib_amount2, refund_amount1, refund_amount2)
        """
        pool_token_1 = current_pool[0]
        pool_token_2 = current_pool[1]
        if current_pool != [0, 0]:
            actual_contribution_token1 = min(token_1_contribute_amount,
                                             int(token_2_contribute_amount * pool_token_1 / pool_token_2))
            # print(f"actual_contribution_token1 in min: {actual_contribution_token1}")

            actual_contribution_token2 = int(actual_contribution_token1 * pool_token_2 / pool_token_1)
            # print(f"actual_contribution_token2 in mul: {actual_contribution_token2}")

            if actual_contribution_token1 == token_1_contribute_amount:
                actual_contribution_token1 = int(actual_contribution_token2 * pool_token_1 / pool_token_2)
                # print(f"actual_contribution_token1 in iff: {actual_contribution_token1}")

            refund_token1 = token_1_contribute_amount - actual_contribution_token1
            refund_token2 = token_2_contribute_amount - actual_contribution_token2
            return actual_contribution_token1, actual_contribution_token2, refund_token1, refund_token2
        else:
            # print('Current rate is [0:0], first time contribute, take all, return none of it')
            return token_1_contribute_amount, token_2_contribute_amount, 0, 0

    @staticmethod
    def cal_contribution_share(contribute_amount, sum_all_share, token_pool, share_amount_before_contribute):
        """
        @param contribute_amount: must be amount of the token which use as token_pool
        @param sum_all_share: of the pair
        @param token_pool: pool value (before contribution) of token use as contribute_amount
        @param share_amount_before_contribute:
        @return:
        """
        return round((contribute_amount * sum_all_share / token_pool) + share_amount_before_contribute)

    @staticmethod
    def cal_trade_receive(sell_amount, pool_token_sell, pool_token_buy):
        pool_token_buy_remain = (pool_token_buy * pool_token_sell) / (sell_amount + pool_token_sell)
        # print("-remain before mod: " + str(remain))
        if (pool_token_buy * pool_token_sell) % (sell_amount + pool_token_sell) != 0:
            pool_token_buy_remain = int(pool_token_buy_remain) + 1
            # print("-remain after mod: " + str(remain))
        received_amount = pool_token_buy - pool_token_buy_remain
        return received_amount


class RewardMath:
    @staticmethod
    def calculate_actual_reward(total_tx_fee, block_on_epoch, max_shard_committee, number_active_shard,
                                number_of_beacon, basic_reward=400000000):
        """
        Function to calculate reward on a node and DAO

        @param total_tx_fee:
        @param block_on_epoch: block on epoch
        @param basic_reward: basic reward by default is 400000000 nanoPRV
        @param max_shard_committee: max shard committee
        @param number_active_shard: number active of shard
        @param number_of_beacon: number of beacon
        @return: reward_dao_receive, reward_on_node_in_shard, reward_of_beacon
        """
        total_reward_on_epoch = block_on_epoch * basic_reward + total_tx_fee
        print(f"Total reward received on a epoch: {total_reward_on_epoch}")

        reward_dao = (total_reward_on_epoch * 10) / 100  # 10% of total reward received on a epoch
        print(f"Total reward of DAO: {reward_dao}")

        total_reward_remain = total_reward_on_epoch - reward_dao

        reward_of_all_beacons = (2 * total_reward_remain) / (number_active_shard + 2)
        print(f"The reward of all beacons: {reward_of_all_beacons}")

        reward_a_shard = total_reward_remain - reward_of_all_beacons
        print(f"The reward of a shard: {reward_a_shard}")

        reward_on_node_in_shard = reward_a_shard / max_shard_committee
        print(f"The reward of a node in shard: {reward_on_node_in_shard}")

        reward_of_a_beacon = reward_of_all_beacons / number_of_beacon
        print(f"The reward of a beacon: {reward_of_a_beacon}")

        return reward_dao, reward_on_node_in_shard, reward_of_a_beacon


class Pde3Math:
    @staticmethod
    def cal_trade_pool(sell_amount, pool_token_sell, v_pool_token_sell, pool_token_buy, v_pool_token_buy):
        """
        @param sell_amount:
        @param pool_token_sell:
        @param v_pool_token_sell:
        @param pool_token_buy:
        @param v_pool_token_buy:
        @return: receiving_amount
        """
        k_virtual = v_pool_token_buy * v_pool_token_sell
        receiving_amount = int(v_pool_token_buy - k_virtual / (v_pool_token_sell + sell_amount))
        return receiving_amount

    @staticmethod
    def cal_contribution_other_end(delta_x, x, y):
        """
        https://docs.dmm.exchange/adding-liquidity-in-dmm/index.html
        Calculate amount of Y token require when contrib x amount of token X.
        Can be use to calculate share withdraw,
        then the x_contrib_amount is negative and equal amount of X token user want to withdraw
        @param delta_x: amount of X token contribute to the pool
        @param x: current balance of token X in pool (x0 + delta_x0)
        @param y: current balance of token Y in pool (y0 + delta_y0)
        @return: delta_y (amount of token Y must contribute)
        """
        return int(delta_x * y / x)

    @staticmethod
    def cal_contrib_both_end(current_total_share, delta_x, delta_y, x, y):
        """
        @param current_total_share:
        @param delta_x: contribute amount of X token
        @param delta_y: contribute amount of y token
        @param x: current balance of token X in pool (x0 + delta_x0)
        @param y: current balance of token Y in pool (y0 + delta_y0)
        @return: accepted amount of X, accepted amount of Y
        """

        delta_share = min(delta_x * current_total_share / x, delta_y * current_total_share / y)
        accepted_y = min(delta_y, Pde3Math.cal_contribution_other_end(delta_x, x, y))
        accepted_x = min(delta_x, Pde3Math.cal_contribution_other_end(delta_y, y, x))
        return int(accepted_x), int(accepted_y), int(delta_share)

    @staticmethod
    def cal_virtual_after_contribution(current_virtual, current_total_share, new_total_share):
        """
        Calculate new virtual amount of pool after contribution
        """
        return int(current_virtual * new_total_share / current_total_share)

    @staticmethod
    def cal_price_min_max(a, x, y, x_current_virtual_pool, y_current_virtual_pool):
        """
        @param a: amplifier
        @param x: current balance of token X in pool
        @param y: current balance of token Y in pool
        @param x_current_virtual_pool:
        @param y_current_virtual_pool:
        @return: min and max price of token X over Y
        """
        virtual_k = x_current_virtual_pool * y_current_virtual_pool
        p_min = pow(a * x - x, 2) / virtual_k
        p_max = virtual_k / pow(a * y - y, 2)
        return int(p_min), int(p_max)

    @staticmethod
    def cal_share_new_pool(amount_x, amount_y):
        return int(math.sqrt(amount_x * amount_y))

    @staticmethod
    def cal_distance_to_order_book(x_virtual, y_virtual, x_order, y_order):
        """
        Calculate distance of a pool to a specific order
        @param x_virtual: current virtual balance of token X of the pool (sell)
        @param y_virtual: current virtual balance of token Y of the pool (buy)
        @param x_order: current balance of token X of the order (sell)
        @param y_order: current balance of token Y of the order (buy)
        @return:
        """
        return int(abs(math.sqrt(x_virtual * y_virtual * x_order / y_order) - x_virtual))

    @staticmethod
    def cal_withdraw_share(delta_s, x, y, current_share):
        """
        @param delta_s: amount of share to be withdraw
        @param x: current balance of token X in pool
        @param y: current balance of token Y in pool
        @param current_share:
        @return: amount or token X and Y receive
        """
        x_receive = int(x * delta_s / current_share)
        y_receive = int(y * delta_s / current_share)
        return x_receive, y_receive

    @staticmethod
    def sort_trade_path(token_sell, trade_path):
        """
        sort trade path in case the paths are not in order BUT MUST have enough necessary pairs to complete the trade.
        the path must also contains no redundant or duplicate pairs
        USE WITH CAUTION!
        """
        if len(trade_path) <= 1:
            return trade_path
        trade_path_unsorted = copy.deepcopy(trade_path)
        trade_path_sorted = []
        token = token_sell
        while trade_path_unsorted:
            for pair in trade_path_unsorted:
                if token in pair:
                    trade_path_sorted.append(pair)
                    tokens_in_pair = pair.split('-')[:2]
                    print(tokens_in_pair)
                    token = tokens_in_pair[1 - tokens_in_pair.index(token)]
                    trade_path_unsorted.remove(pair)
                    break
        return trade_path_sorted
