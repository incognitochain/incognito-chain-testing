import json
import random
import string
import time
from json.decoder import JSONDecodeError

from IncognitoChain.Configs.Constants import ChainConfig
from IncognitoChain.Helpers.Logging import INFO
from IncognitoChain.Helpers.Time import WAIT


def l6(string):
    """
    Return the last 6 chars of a string
    @param string:
    @return:
    """
    return str(string)[-6:]


def l3(string):
    """
    Return the last 3 chars of a string
    @param string:
    @return:
    """
    return str(string)[-3:]


def json_extract(string):
    """
    strip all none json part a string
    @param string:
    @return: dictionary
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


def format_dict_side_by_side(dict1, dict2):
    # find max line len
    max_k_len = 0
    max_v_len = 0
    dict_mix = {}

    for key, value in dict1.items():
        if max_k_len < len(str(key)):
            max_k_len = len(str(key))
        if max_v_len < len(str(value)):
            max_v_len = len(str(value))
        dict_mix[key] = [value, '_']

    for key, value in dict2.items():
        if max_k_len < len(str(key)):
            max_k_len = len(str(key))
        try:
            dict_mix[key][1] = value
        except KeyError:
            dict_mix[key] = ['-', value]

    lines = ""
    for key, list in dict_mix.items():
        try:
            if list[0] == list[1]:
                compare = '='
            elif list[0] < list[1]:
                compare = '<'
            else:
                compare = '>'
        except TypeError:
            compare = '#'

        lines += f"%{max_k_len + 15}s : %{max_v_len}s %s %s\n" % (key, list[0], compare, list[1])

    return lines


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


class KeyExtractor:
    @staticmethod
    def incognito_addr(obj):
        from IncognitoChain.Objects.AccountObject import Account
        from IncognitoChain.Objects.PortalObjects import PortalStateInfo

        if type(obj) is str:
            addr = obj
        elif type(obj) is Account:
            addr = obj.incognito_addr
        elif type(obj) is PortalStateInfo.CustodianInfo:
            addr = obj.get_incognito_addr()
        else:
            raise TypeError("Input must be incognito address (string), CustodianInfo or Account object")
        return addr

    @staticmethod
    def committee_public_k(obj):
        from IncognitoChain.Objects.AccountObject import Account
        if type(obj) is str:
            addr = obj
        elif type(obj) is Account:
            addr = obj.committee_public_k
        else:
            raise TypeError("Input must be committee public key (string) or Account object")
        return addr

    @staticmethod
    def inc_public_k(obj):
        from IncognitoChain.Objects.AccountObject import Account
        from IncognitoChain.Objects.BeaconObject import BeaconBestStateDetailInfo
        if type(obj) is str:
            addr = obj
        elif type(obj) is Account:
            addr = obj.public_key
        elif type(obj) is BeaconBestStateDetailInfo.Committee:
            addr = obj.get_inc_public_key()
        else:
            raise TypeError("Input must be inc public key (string), "
                            "BeaconBestStateDetailInfo.Committee or Account object")
        return addr


class ChainHelper:
    @staticmethod
    def cal_epoch_from_height(height):
        return height // ChainConfig.BLOCK_PER_EPOCH + 1

    @staticmethod
    def cal_first_height_of_epoch(epoch):
        return ((epoch - 1) * ChainConfig.BLOCK_PER_EPOCH) + 1

    @staticmethod
    def cal_last_height_of_epoch(epoch):
        return ChainHelper.cal_first_height_of_epoch(epoch) + ChainConfig.BLOCK_PER_EPOCH - 1

    @staticmethod
    def wait_till_beacon_height(beacon_height, interval=ChainConfig.BLOCK_TIME, timeout=120):
        """
        Wait until a specific beacon height
        @param interval:
        @param timeout:
        @param beacon_height:
        @return:
        """
        INFO(f'Waiting till beacon height {beacon_height}')
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        current_beacon_h = SUT().help_get_beacon_height()
        if beacon_height <= current_beacon_h:
            INFO(f'Beacon height {beacon_height} is passed already')
            return current_beacon_h

        while beacon_height > current_beacon_h:
            WAIT(interval)
            timeout -= interval
            current_beacon_h = SUT().help_get_beacon_height()
            if timeout <= 0:
                INFO(f'Time out and current beacon height is {current_beacon_h}')
                return current_beacon_h

        INFO(f'Time out and current beacon height is {current_beacon_h}')
        return current_beacon_h

    @staticmethod
    def wait_till_next_beacon_height(num_of_beacon_height_to_wait=1, wait=40, timeout=120):
        """
        wait for an amount of beacon height to pass
        @param timeout:
        @param wait:
        @param num_of_beacon_height_to_wait:
        @return:
        """
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        current_beacon_h = SUT().help_get_beacon_height()

        return ChainHelper.wait_till_beacon_height(current_beacon_h + num_of_beacon_height_to_wait, wait, timeout)

    @staticmethod
    def wait_till_next_shard_height(shard_id, num_of_shard_height_to_wait=1, wait=40, timeout=120):
        """
        Function to wait for an amount of shard height to pass
        @param shard_id:
        @param num_of_shard_height_to_wait:
        @param wait:
        @param timeout:
        @return:
        """
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        current_shard_h = SUT().help_get_shard_height(shard_id)
        shard_height = current_shard_h + num_of_shard_height_to_wait
        INFO(f'Waiting till shard {shard_id} height {shard_height}')

        if shard_height <= current_shard_h:
            INFO(f'Shard {shard_id} height {shard_height} is passed already')
            return current_shard_h

        while shard_height > current_shard_h:
            WAIT(wait)
            timeout -= wait
            current_shard_h = SUT().help_get_shard_height(shard_id)
            if timeout <= 0:
                INFO(f'Time out and current shard {shard_id} height is {current_shard_h}')
                return current_shard_h

        INFO(f'Time out and current shard {shard_id} height is {current_shard_h}')
        return current_shard_h

    @staticmethod
    def wait_till_next_epoch(epoch_wait=None, check_interval=None, timeout=180):
        f"""
        Wait till {epoch_wait} to come, if {epoch_wait} is None, just wait till next epoch
        @param epoch_wait: 
        @param check_interval: 
        @param timeout: 
        @return: 
        """
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        check_interval = ChainConfig.get_epoch_time() if check_interval is None else check_interval
        blk_chain_info = SUT().get_block_chain_info()
        current_epoch = blk_chain_info.get_beacon_block().get_epoch()
        epoch_wait = current_epoch + 1 if epoch_wait is None else epoch_wait
        INFO(f'Wait until epoch {epoch_wait}, check every {check_interval}s, timeout {timeout}s')
        if current_epoch >= epoch_wait:
            return current_epoch
        time_start = time.perf_counter()
        while current_epoch < epoch_wait:
            WAIT(check_interval)
            blk_chain_info = SUT().get_block_chain_info()
            current_epoch = blk_chain_info.get_beacon_block().get_epoch()
            if current_epoch == epoch_wait:
                INFO(f"Now epoch = {current_epoch}")
                return current_epoch
            time_current = time.perf_counter()
            if time_current - time_start > timeout:
                INFO('Timeout')
                return None


def calculate_contribution(token_1_contribute_amount, token_2_contribute_amount, current_rate: list):
    """

    @param token_1_contribute_amount:
    @param token_2_contribute_amount:
    @param current_rate: [token1_pool, token2_pool]
    @return: (actual_contrib_amount1,  actual_contrib_amount2, refund_amount1, refund_amount2)
    """
    pool_token_1 = current_rate[0]
    pool_token_2 = current_rate[1]
    if current_rate != [0, 0]:
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
    else:
        print('Current rate is [0:0], first time contribute, take all, return none of it')
        return token_1_contribute_amount, token_2_contribute_amount, 0, 0


def calculate_actual_trade_received(trade_amount, pool_token_sell, pool_token_buy):
    """
    @param trade_amount:
    @param pool_token_sell:
    @param pool_token_buy:
    @return:
    """
    print(f'amount, pool sell-buy: {trade_amount}, {pool_token_sell} - {pool_token_buy}')
    remain = (pool_token_buy * pool_token_sell) / (trade_amount + pool_token_sell)
    print("-remain before mod: " + str(remain))
    if (pool_token_buy * pool_token_sell) % (trade_amount + pool_token_sell) != 0:
        remain = int(remain) + 1
        print("-remain after mod: " + str(remain))

    received_amount = pool_token_buy - remain
    print("-expecting received amount: " + str(received_amount))
    return received_amount


def calculate_actual_reward(total_tx_fee, block_on_epoch, max_shard_committee, number_active_shard, number_of_beacon,
                            basic_reward=400000000):
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


def get_beacon_best_state_detail(number_of_beacon_height_to_get=100, wait=5, timeout=50):
    """
    Function to get beacon best state detail
    @param number_of_beacon_height_to_get: number of beacon height to get
    @param wait:
    @param timeout:
    @return: a list beacon best state detail obj
    """
    from IncognitoChain.Objects.IncognitoTestCase import SUT
    list_beacon_best_state_detail_objs = []
    for i in range(1, number_of_beacon_height_to_get + 1):
        list_beacon_best_state_detail_objs.append(SUT().get_beacon_best_state_detail_info())
        # Waiting till beacon height increase
        ChainHelper.wait_till_next_beacon_height(num_of_beacon_height_to_wait=1, wait=wait, timeout=timeout)
        list_beacon_best_state_detail_objs.append(SUT().get_beacon_best_state_detail_info())
    return list_beacon_best_state_detail_objs


def get_shard_best_state_detail(shard_id, number_of_shard_height_to_get=100, wait=5, timeout=50):
    """
    Function to get shard best state detail
    @param shard_id:
    @param number_of_shard_height_to_get: number of shard height to get
    @param wait:
    @param timeout:
    @return: a list shard detail obj
    """
    from IncognitoChain.Objects.IncognitoTestCase import SUT
    list_shard_best_state_detail_objs = []
    for i in range(1, number_of_shard_height_to_get + 1):
        list_shard_best_state_detail_objs.append(SUT().get_shard_best_state_detail_info(shard_id))
        # Waiting till shard height increase
        ChainHelper.wait_till_next_shard_height(shard_id=shard_id, num_of_shard_height_to_wait=1, wait=wait,
                                                timeout=timeout)
        list_shard_best_state_detail_objs.append(SUT().get_shard_best_state_detail_info(shard_id))
    return list_shard_best_state_detail_objs


def get_beacon_best_state(number_of_beacon_height_to_get=100, wait=5, timeout=50):
    """
    Function to get beacon best state
    @param number_of_beacon_height_to_get: number of beacon height to get
    @param wait:
    @param timeout:
    @return: a list beacon best state obj
    """
    from IncognitoChain.Objects.IncognitoTestCase import SUT
    list_beacon_best_state_objs = []
    for i in range(1, number_of_beacon_height_to_get + 1):
        list_beacon_best_state_objs.append(SUT().get_beacon_best_state_info())
        # Waiting till beacon height increase
        ChainHelper.wait_till_next_beacon_height(num_of_beacon_height_to_wait=1, wait=wait, timeout=timeout)
        list_beacon_best_state_objs.append(SUT().get_beacon_best_state_info())
    return list_beacon_best_state_objs


def get_shard_best_state(shard_id, number_of_shard_height_to_get=100, wait=5, timeout=50):
    """
    Function to get shard best state
    @param shard_id: shard id
    @param number_of_shard_height_to_get: number of shard height to get
    @param wait:
    @param timeout:
    @return: a list shard best state obj
    """
    from IncognitoChain.Objects.IncognitoTestCase import SUT
    list_shard_best_state_objs = []
    for i in range(1, number_of_shard_height_to_get + 1):
        list_shard_best_state_objs.append(SUT().get_shard_best_state_info(shard_id))
        # Waiting till shard height increase
        ChainHelper.wait_till_next_shard_height(shard_id=shard_id, num_of_shard_height_to_wait=1, wait=wait,
                                                timeout=timeout)
        list_shard_best_state_objs.append(SUT().get_shard_best_state_info(shard_id))
    return list_shard_best_state_objs


def make_random_word(word_min_len=None, word_max_len=None):
    word_min_len = 3 if word_min_len is None else word_min_len
    word_max_len = 8 if word_max_len is None else word_max_len
    return ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(word_min_len, word_max_len)))


def make_random_str_list(length=None, word_min_len=None, word_max_len=None):
    length = random.randint(5, 10) if length is None else length
    random_list = []
    for i in range(length):
        random_list.append(make_random_word(word_min_len, word_max_len))
    return random_list


def make_random_str_dict(size=None):
    size = random.randint(5, 10) if size is None else size
    random_dict = {}
    for i in range(size):
        random_dict[make_random_word()] = make_random_word()
    return random_dict
