import json
from json.decoder import JSONDecodeError

from IncognitoChain.Configs.Constants import ChainConfig, Status
from IncognitoChain.Helpers.Logging import INFO
from IncognitoChain.Helpers.Time import WAIT


def l6(string):
    """
    Return the last 6 chars of a string
    :param string:
    :return:
    """
    return str(string)[-6:]


def json_extract(string):
    """
    strip all none json part a string
    :param string:
    :return: dictionary
    """
    try:
        string = '{' + string.split('{', 1)[-1]  # remove all non-sense before the first {
        string = string.split(', error', 1)[0]  # remove all non-sense from ', error'
        return json.loads(string)
    except JSONDecodeError:
        return None


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


def extract_incognito_addr(obj):
    from IncognitoChain.Objects.AccountObject import Account
    from IncognitoChain.Objects.PortalObjects import PortalStateInfo

    if type(obj) == str:
        addr = obj
    elif type(obj) == Account:
        addr = obj.incognito_addr
    elif type(obj) == PortalStateInfo.CustodianInfo:
        addr = obj.get_incognito_addr()
    else:
        raise TypeError("Input must be incognito address (string), CustodianInfo or Account object")
    return addr


class ChainHelper:
    @staticmethod
    def cal_epoch_from_height(height):
        return height / ChainConfig.BLOCK_PER_EPOCH + 1

    @staticmethod
    def cal_first_height_of_epoch(epoch):
        return ((epoch - 1) * ChainConfig.BLOCK_PER_EPOCH) + 1

    @staticmethod
    def cal_last_height_of_epoch(epoch):
        return ChainHelper.cal_first_height_of_epoch(epoch) + ChainConfig.BLOCK_PER_EPOCH - 1

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

    @staticmethod
    def wait_till_next_shard_height(shard_id, num_of_shard_height_to_wait=1, wait=40, timeout=120):
        """
        Function to wait for an amount of shard height to pass
        :param shard_id:
        :param num_of_shard_height_to_wait:
        :param wait:
        :param timeout:
        :return:
        """
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        current_shard_h = SUT.full_node.help_get_shard_height(shard_id)
        shard_height = current_shard_h + num_of_shard_height_to_wait
        INFO(f'Waiting till shard {shard_id} height {shard_height}')

        if shard_height <= current_shard_h:
            INFO(f'Shard {shard_id} height {shard_height} is passed already')
            return current_shard_h

        while shard_height > current_shard_h:
            WAIT(wait)
            timeout -= wait
            current_shard_h = SUT.full_node.help_get_shard_height(shard_id)
            if timeout <= 0:
                INFO(f'Time out and current shard {shard_id} height is {current_shard_h}')
                return current_shard_h

        INFO(f'Time out and current shard {shard_id} height is {current_shard_h}')
        return current_shard_h


def calculate_contribution(token_1_contribute_amount, token_2_contribute_amount, current_rate: list):
    pool_token_1 = current_rate[0]
    pool_token_2 = current_rate[1]
    actual_contribution_token1 = min(token_1_contribute_amount,
                                     int(token_2_contribute_amount * pool_token_1 / pool_token_2))
    print(f"actual_contribution_token1 in min: {actual_contribution_token1}")

    actual_contribution_token2 = int(actual_contribution_token1 * pool_token_2 / pool_token_1)
    print(f"actual_contribution_token2 in mul: {actual_contribution_token2}")

    if actual_contribution_token1 == token_1_contribute_amount:
        actual_contribution_token1 = int(actual_contribution_token2 * pool_token_1 / pool_token_2)
        print(f"actual_contribution_token1 in iff: {actual_contribution_token1}")

    refund_token1 = token_1_contribute_amount - actual_contribution_token1
    refund_token2 = token_2_contribute_amount - actual_contribution_token2
    return actual_contribution_token1, actual_contribution_token2, refund_token1, refund_token2


def calculate_actual_trade_received(trade_amount, pool_token2_sell, pool_token2_buy):
    remain = (pool_token2_buy * pool_token2_sell) / (trade_amount + pool_token2_sell)
    # print("-remain before mod: " + str(remain))
    if (pool_token2_buy * pool_token2_sell) % (trade_amount + pool_token2_sell) != 0:
        remain = int(remain) + 1
        # print("-remain after mod: " + str(remain))

    received_amount = pool_token2_buy - remain
    print("-expecting received amount: " + str(received_amount))
    return received_amount


def calculate_actual_reward(total_tx_fee, block_on_epoch, max_shard_committee, number_active_shard, number_of_beacon,
                            basic_reward=400000000):
    """
    Function to calculate reward on a node and DAO

    :param total_tx_fee:
    :param block_on_epoch: block on epoch
    :param basic_reward: basic reward by default is 400000000 nanoPRV
    :param max_shard_committee: max shard committee
    :param number_active_shard: number active of shard
    :param number_of_beacon: number of beacon
    :return: reward_dao_receive, reward_on_node_in_shard, reward_of_beacon
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


class PortalHelper:

    @staticmethod
    def cal_lock_collateral(token_amount, token_rate, prv_rate):
        token_amount, token_rate, prv_rate = to_num(token_amount, token_rate, prv_rate)
        estimated_lock_collateral = int(
            int(token_amount * ChainConfig.Portal.COLLATERAL_PERCENT) * token_rate // prv_rate)
        INFO(f'''Calculating lock collateral: 
            token amount: {token_amount}, 
            token rate:   {token_rate}, 
            prv rate:     {prv_rate},
            lock amount:  {estimated_lock_collateral} 
        -------------------------------------------------------------------''')
        return estimated_lock_collateral

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

        new_prv_rate = (percent * prv_rate) // ChainConfig.Portal.COLLATERAL_PERCENT
        new_tok_rate = (ChainConfig.Portal.COLLATERAL_PERCENT * token_rate) // percent

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
                                         liquidate_percent=ChainConfig.Portal.COLLATERAL_LIQUIDATE_PERCENT):
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
            assert info.get_status() == Status.Portal.DepositStatus.ACCEPT
        else:
            assert info.get_status() == Status.Portal.DepositStatus.REJECTED

    @staticmethod
    def cal_liquidation_of_porting(porting_amount, current_token_rate, current_prv_rate):
        porting_amount_in_new_prv_rate = PortalHelper.cal_portal_exchange_tok_to_prv(porting_amount, current_token_rate,
                                                                                     current_prv_rate)

        estimate_lock_collateral = PortalHelper.cal_lock_collateral(porting_amount, current_token_rate,
                                                                    current_prv_rate)
        estimated_liquidated_collateral = int(
            ChainConfig.Portal.COLLATERAL_LIQUIDATE_TO_POOL_PERCENT * porting_amount_in_new_prv_rate)
        return_collateral = estimate_lock_collateral - estimated_liquidated_collateral
        return int(estimated_liquidated_collateral), int(return_collateral)

    @staticmethod
    def cal_token_amount_from_collateral(collateral, token_rate, prv_rate):
        prv_equivalent = collateral // ChainConfig.Portal.COLLATERAL_PERCENT
        return int(
            PortalHelper.cal_portal_exchange_prv_to_tok(prv_equivalent, prv_rate, token_rate))


def get_beacon_best_state_detail(number_of_beacon_height_to_get=100, wait=5, timeout=50):
    """
    Function to get beacon best state detail
    :param number_of_beacon_height_to_get: number of beacon height to get
    :param wait:
    :param timeout:
    :return: a list beacon best state detail obj
    """
    from IncognitoChain.Objects.IncognitoTestCase import SUT
    list_beacon_best_state_detail_objs = []
    for i in range(1, number_of_beacon_height_to_get + 1):
        list_beacon_best_state_detail_objs.append(SUT.REQUEST_HANDLER.get_beacon_best_state_detail_info())
        # Waiting till beacon height increase
        ChainHelper.wait_till_next_beacon_height(num_of_beacon_height_to_wait=1, wait=wait, timeout=timeout)
        list_beacon_best_state_detail_objs.append(SUT.REQUEST_HANDLER.get_beacon_best_state_detail_info())
    return list_beacon_best_state_detail_objs


def get_shard_best_state_detail(shard_id, number_of_shard_height_to_get=100, wait=5, timeout=50):
    """
    Function to get shard best state detail
    :param shard_id:
    :param number_of_shard_height_to_get: number of shard height to get
    :param wait:
    :param timeout:
    :return: a list shard detail obj
    """
    from IncognitoChain.Objects.IncognitoTestCase import SUT
    list_shard_best_state_detail_objs = []
    for i in range(1, number_of_shard_height_to_get + 1):
        list_shard_best_state_detail_objs.append(SUT.REQUEST_HANDLER.get_shard_best_state_detail_info(shard_id))
        # Waiting till shard height increase
        ChainHelper.wait_till_next_shard_height(shard_id=shard_id, num_of_shard_height_to_wait=1, wait=wait,
                                                timeout=timeout)
        list_shard_best_state_detail_objs.append(SUT.REQUEST_HANDLER.get_shard_best_state_detail_info(shard_id))
    return list_shard_best_state_detail_objs


def get_beacon_best_state(number_of_beacon_height_to_get=100, wait=5, timeout=50):
    """
    Function to get beacon best state
    :param number_of_beacon_height_to_get: number of beacon height to get
    :param wait:
    :param timeout:
    :return: a list beacon best state obj
    """
    from IncognitoChain.Objects.IncognitoTestCase import SUT
    list_beacon_best_state_objs = []
    for i in range(1, number_of_beacon_height_to_get + 1):
        list_beacon_best_state_objs.append(SUT.REQUEST_HANDLER.get_beacon_best_state_info())
        # Waiting till beacon height increase
        ChainHelper.wait_till_next_beacon_height(num_of_beacon_height_to_wait=1, wait=wait, timeout=timeout)
        list_beacon_best_state_objs.append(SUT.REQUEST_HANDLER.get_beacon_best_state_info())
    return list_beacon_best_state_objs


def get_shard_best_state(shard_id, number_of_shard_height_to_get=100, wait=5, timeout=50):
    """
    Function to get shard best state
    :param shard_id: shard id
    :param number_of_shard_height_to_get: number of shard height to get
    :param wait:
    :param timeout:
    :return: a list shard best state obj
    """
    from IncognitoChain.Objects.IncognitoTestCase import SUT
    list_shard_best_state_objs = []
    for i in range(1, number_of_shard_height_to_get + 1):
        list_shard_best_state_objs.append(SUT.REQUEST_HANDLER.get_shard_best_state_info(shard_id))
        # Waiting till shard height increase
        ChainHelper.wait_till_next_shard_height(shard_id=shard_id, num_of_shard_height_to_wait=1, wait=wait,
                                                timeout=timeout)
        list_shard_best_state_objs.append(SUT.REQUEST_HANDLER.get_shard_best_state_info(shard_id))
    return list_shard_best_state_objs
