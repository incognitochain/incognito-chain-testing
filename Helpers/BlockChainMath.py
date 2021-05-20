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
