import math

from IncognitoChain.Configs.Constants import PORTAL_COLLATERAL_LIQUIDATE_PERCENT, PORTAL_COLLATERAL_PERCENT, \
    PortalDepositStatus, PORTAL_COLLATERAL_LIQUIDATE_TO_POOL_PERCENT
from IncognitoChain.Helpers.Logging import INFO
from IncognitoChain.Helpers.Time import WAIT


def l6(string):
    """
    Return the last 6 chars of a string
    :param string:
    :return:
    """
    return string[-6:]


def to_num(*args):
    ret = ()
    for arg in args:
        if type(arg) is float:
            ret += (float(arg),)
        else:
            try:
                ret += (int(arg),)
            except ValueError:
                raise ValueError('WTF?? why TF did you input text here???')

    return ret


class ChainHelper:
    @staticmethod
    def wait_till_beacon_height(beacon_height, wait=40, timeout=120):
        """
        Wait until a specific beacon height
        :param wait:
        :param timeout:
        :param beacon_height:
        :return:
        """
        INFO(f'Waiting till beacon height {beacon_height}')
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        current_beacon_h = SUT.full_node.help_get_beacon_height()
        if beacon_height <= current_beacon_h:
            INFO(f'Beacon height {beacon_height} is passed already')
            return current_beacon_h

        while beacon_height > current_beacon_h:
            WAIT(wait)
            timeout -= wait
            current_beacon_h = SUT.full_node.help_get_beacon_height()
            if timeout <= 0:
                INFO(f'Time out and current beacon height is {current_beacon_h}')
                return current_beacon_h

        INFO(f'Time out and current beacon height is {current_beacon_h}')
        return current_beacon_h

    @staticmethod
    def wait_till_next_beacon_height(num_of_beacon_height_to_wait=1, wait=40, timeout=120):
        """
        wait for an amount of beacon height to pass
        :param timeout:
        :param wait:
        :param num_of_beacon_height_to_wait:
        :return:
        """
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        current_beacon_h = SUT.full_node.help_get_beacon_height()

        return ChainHelper.wait_till_beacon_height(current_beacon_h + num_of_beacon_height_to_wait, wait, timeout)


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
        token_amount, token_rate, prv_rate = to_num(token_amount, token_rate, prv_rate)
        estimated_lock_collateral = int(token_amount * PORTAL_COLLATERAL_PERCENT) * token_rate // prv_rate
        return int(estimated_lock_collateral)

    @staticmethod
    def cal_portal_exchange_tok_to_prv(token_amount, token_rate, prv_rate):
        token_amount, token_rate, prv_rate = to_num(token_amount, token_rate, prv_rate)
        return token_amount * token_rate // prv_rate

    @staticmethod
    def cal_portal_exchange_prv_to_tok(prv_amount, prv_rate, token_rate):
        prv_amount, prv_rate, token_rate = to_num(prv_amount, prv_rate, token_rate)
        return prv_amount * prv_rate // token_rate

    @staticmethod
    def cal_portal_portal_fee(token_amount, token_rate, prv_rate, fee_rate=0.0001):
        token_amount, token_rate, prv_rate = to_num(token_amount, token_rate, prv_rate)
        return round(token_amount * fee_rate * token_rate / prv_rate)  # fee = 0.01%

    @staticmethod
    def cal_liquidate_rate(percent, token_rate, prv_rate, change_token_rate=False):
        """

        :param percent:
        :param token_rate:
        :param prv_rate:
        :param change_token_rate: if true, return new token rate. otherwise , return new prv rate
        :return:
        """

        new_prv_rate = (percent * prv_rate) // PORTAL_COLLATERAL_PERCENT
        new_tok_rate = (PORTAL_COLLATERAL_PERCENT * token_rate) // percent

        if change_token_rate:
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
                                         current_prv_rate, new_rate='token',
                                         liquidate_percent=PORTAL_COLLATERAL_LIQUIDATE_PERCENT):
        """

        :param liquidate_percent:
        :param token_holding:
        :param prv_collateral:
        :param current_tok_rate:
        :param current_prv_rate:
        :param new_rate: 'token' or 'prv', to indicate which of the new rate you want to get
        :return:
        """
        if new_rate == 'token':
            return PortalHelper.cal_rate_to_match_collateral_percent(
                liquidate_percent, token_holding, prv_collateral, current_tok_rate, current_prv_rate)
        else:
            return PortalHelper.cal_rate_to_match_collateral_percent(
                liquidate_percent, token_holding, prv_collateral, current_tok_rate, current_prv_rate,
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
        sum_holding = holding_token + holding_token_of_waiting_redeem
        return int(sum_holding * 1.05 * rate_token / rate_prv)

    @staticmethod
    def check_custodian_deposit_tx_status(tx_id, expected='accept'):
        from IncognitoChain.Objects.PortalObjects import DepositTxInfo

        info = DepositTxInfo()
        info.get_deposit_info(tx_id)
        if expected.lower() == "accept":
            assert info.get_status() == PortalDepositStatus.ACCEPT
        else:
            assert info.get_status() == PortalDepositStatus.REJECTED

    @staticmethod
    def cal_liquidation_of_porting(porting_amount, current_token_rate, current_prv_rate):
        porting_amount_in_new_prv_rate = PortalHelper.cal_portal_exchange_tok_to_prv(porting_amount, current_token_rate,
                                                                                     current_prv_rate)

        estimate_lock_collateral = PortalHelper.cal_lock_collateral(porting_amount, current_token_rate,
                                                                    current_prv_rate)
        estimated_liquidated_collateral = int(
            PORTAL_COLLATERAL_LIQUIDATE_TO_POOL_PERCENT * porting_amount_in_new_prv_rate)
        return_collateral = estimate_lock_collateral - estimated_liquidated_collateral
        return int(estimated_liquidated_collateral), int(return_collateral)

    @staticmethod
    def cal_token_amount_from_collateral(collateral, token_rate, prv_rate):
        prv_equivalent = collateral // PORTAL_COLLATERAL_PERCENT
        return int(
            PortalHelper.cal_portal_exchange_prv_to_tok(prv_equivalent, prv_rate, token_rate))
