import math


def l6(string):
    """
    Return the last 6 chars of a string
    :param string:
    :return:
    """
    return string[-6:]


def calculate_contribution(token_1_contribute_amount, token_2_contribute_amount, current_rate: list):
    pool_token_1 = current_rate[0]
    pool_token_2 = current_rate[1]
    actual_contribution_token1 = min(token_1_contribute_amount,
                                     math.floor(token_2_contribute_amount * pool_token_1 / pool_token_2))
    print(f"actual_contribution_token1 in min: {actual_contribution_token1}")

    actual_contribution_token2 = math.floor(actual_contribution_token1 * pool_token_2 / pool_token_1)
    print(f"actual_contribution_token2 in mul: {actual_contribution_token2}")

    if actual_contribution_token1 == token_1_contribute_amount:
        actual_contribution_token1 = math.floor(actual_contribution_token2 * pool_token_1 / pool_token_2)
        print(f"actual_contribution_token1 in iff: {actual_contribution_token1}")

    refund_token1 = token_1_contribute_amount - actual_contribution_token1
    refund_token2 = token_2_contribute_amount - actual_contribution_token2
    return actual_contribution_token1, actual_contribution_token2, refund_token1, refund_token2


def calculate_actual_trade_received(trade_amount, pool_token2_sell, pool_token2_buy):
    remain = (pool_token2_buy * pool_token2_sell) / (trade_amount + pool_token2_sell)
    # print("-remain before mod: " + str(remain))
    if (pool_token2_buy * pool_token2_sell) % (trade_amount + pool_token2_sell) != 0:
        remain = math.floor(remain) + 1
        # print("-remain after mod: " + str(remain))

    received_amount = pool_token2_buy - remain
    print("-expecting received amount: " + str(received_amount))
    return received_amount


class PortalHelper:

    @staticmethod
    def cal_lock_collateral(token_amount, token_rate, prv_rate):
        estimated_lock_collateral = (int(token_amount) * 150 // 100) * int(token_rate) // int(prv_rate)
        return estimated_lock_collateral

    @staticmethod
    def cal_portal_exchange_to_prv(token_amount, token_rate, prv_rate):
        return int(token_amount) * int(token_rate) // int(prv_rate)

    @staticmethod
    def cal_portal_exchange_to_token(prv_amount, prv_rate, token_rate):
        return round(int(prv_amount) * int(prv_rate) / int(token_rate))

    @staticmethod
    def cal_portal_portal_fee(token_amount, token_rate, prv_rate):
        return round((int(token_amount) * int(token_rate) / int(prv_rate)) / 10000)  # fee = 0.01%
