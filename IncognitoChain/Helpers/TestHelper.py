import math

from IncognitoChain.Configs.Constants import PORTAL_COLLATERAL_LIQUIDATE_PERCENT, PORTAL_COLLATERAL_PERCENT
from IncognitoChain.Helpers.Logging import INFO


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
        estimated_lock_collateral = (int(token_amount) * PORTAL_COLLATERAL_PERCENT) * int(token_rate) // int(prv_rate)
        return estimated_lock_collateral

    @staticmethod
    def cal_portal_exchange_tok_to_prv(token_amount, token_rate, prv_rate):
        return round(int(token_amount) * int(token_rate) / int(prv_rate))

    @staticmethod
    def cal_portal_exchange_prv_to_tok(prv_amount, prv_rate, token_rate):
        return round(int(prv_amount) * int(prv_rate) / int(token_rate))

    @staticmethod
    def cal_portal_portal_fee(token_amount, token_rate, prv_rate):
        return round((int(token_amount) * int(token_rate) / int(prv_rate)) / 10000)  # fee = 0.01%

    @staticmethod
    def cal_liquidate_rate(percent, token_id, token_rate, prv_rate, token_to_change_rate=None):

        new_prv_rate = (percent * prv_rate) // PORTAL_COLLATERAL_PERCENT
        new_tok_rate = (PORTAL_COLLATERAL_PERCENT * token_rate) // percent

        if token_to_change_rate == token_id:
            INFO(f'Current token rate {token_rate}, new rate {new_tok_rate}')
            return int(new_tok_rate)
        else:
            INFO(f'Current prv rate {prv_rate}, new rate {new_prv_rate}')
            return int(new_prv_rate)

    @staticmethod
    def cal_rate_to_match_collateral_percent(percent, token_holding, prv_collateral, current_tok_rate,
                                             current_prv_rate, rate_return='token'):
        """

        :param current_tok_rate:
        :param current_prv_rate:
        :param percent:
        :param token_holding:
        :param prv_collateral:
        :param rate_return: select new rate to return, PRV or token
        :return:
        """

        new_prv_rate = int(current_tok_rate * percent * token_holding / prv_collateral)
        new_tok_rate = int(prv_collateral * current_prv_rate / percent / token_holding)

        if rate_return == 'token':
            INFO(f'Current token rate {current_tok_rate}, new rate {new_tok_rate}')
            return int(new_tok_rate)
        else:
            INFO(f'Current prv rate {current_prv_rate}, new rate {new_prv_rate}')
            return int(new_prv_rate)

    @staticmethod
    def cal_rate_to_liquidate_collateral(token_holding, prv_collateral, current_tok_rate,
                                         current_prv_rate, rate_return='token'):
        if rate_return == 'token':
            return PortalHelper.cal_rate_to_match_collateral_percent(
                PORTAL_COLLATERAL_LIQUIDATE_PERCENT, token_holding, prv_collateral, current_tok_rate, current_prv_rate)
        else:
            return PortalHelper.cal_rate_to_match_collateral_percent(
                PORTAL_COLLATERAL_LIQUIDATE_PERCENT, token_holding, prv_collateral, current_tok_rate, current_prv_rate,
                rate_return='prv')

    @staticmethod
    def cal_liquidation_amount_of_collateral(holding_token, holding_token_of_waiting_redeem, rate_token, rate_prv):
        """
        :param rate_prv:
        :param rate_token:
        :param holding_token: of custodian
        :param holding_token_of_waiting_redeem: of custodian
        :return: (sum_holding * 1.05 * ratePubToken) / ratePRV
        """
        sum_holding = holding_token, holding_token_of_waiting_redeem
        return sum_holding * 1.05 * rate_token / rate_prv
