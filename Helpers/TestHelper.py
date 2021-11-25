import json
import random
import string
from json.decoder import JSONDecodeError

from Configs.Configs import ChainConfig
from Helpers.Logging import INFO
from Helpers.Time import WAIT


class CustomAssert:
    @staticmethod
    def compare_with_margin(a, b, margin):
        if abs(a - b) > margin:
            raise AssertionError(f"{a} vs {b}, margin {margin}")
        INFO(f"{a} vs {b} is tolerable, margin = {margin}")
        return True


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


def convert_dict_num_to(d, to=str):
    """
    @param d: dictionary to convert
    @param to: type to convert to, accept only 'int' or 'str'
    @return: None
    """
    for key, value in d.items():
        if isinstance(value, dict):
            convert_dict_num_to(value, to)
        elif isinstance(value, list):
            value = [convert_dict_num_to(item, to) if isinstance(item, dict) else str(item) for item in value]
        else:
            try:
                d[key] = to(value)
            except ValueError:  # ignore if cannot convert
                pass


class KeyExtractor:
    @staticmethod
    def incognito_addr(obj):
        from Objects.AccountObject import Account
        from Objects.PortalObjects import PortalStateInfo

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
        from Objects.AccountObject import Account
        if type(obj) is str:
            addr = obj
        elif type(obj) is Account:
            addr = obj.committee_public_k
        else:
            raise TypeError("Input must be committee public key (string) or Account object")
        return addr

    @staticmethod
    def inc_public_k(obj):
        from Objects.AccountObject import Account
        from Objects.BeaconObject import BeaconBestStateDetailInfo
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
    def cal_first_height_of_epoch(epoch, index_epoch_change=0, block_per_epoch_b4=0, block_per_epoch_af=None):
        """

        @param epoch:
        @param index_epoch_change: input if there is change block_per_epoch in chain
        @param block_per_epoch_b4: input if there is change block_per_epoch in chain
        @param block_per_epoch_af: input if there is change block_per_epoch in chain
        @return:
        """
        if block_per_epoch_af is None:
            block_per_epoch_af = ChainConfig.BLOCK_PER_EPOCH
        return ((index_epoch_change + 1) * block_per_epoch_b4 + (
                epoch - index_epoch_change - 1) * block_per_epoch_af) + 1

    @staticmethod
    def cal_last_height_of_epoch(epoch):
        return ChainHelper.cal_first_height_of_epoch(epoch) + ChainConfig.BLOCK_PER_EPOCH - 1

    @staticmethod
    def cal_random_height_of_epoch(epoch, index_epoch_change=0, block_per_epoch_b4=0, block_per_epoch_af=None):
        if block_per_epoch_af is None:
            block_per_epoch_af = ChainConfig.BLOCK_PER_EPOCH
        block_height_random = ((index_epoch_change + 1) * block_per_epoch_b4 + (
                epoch - index_epoch_change - 1) * block_per_epoch_af) + ChainConfig.RANDOM_TIME
        return block_height_random

    @staticmethod
    def wait_till_beacon_height(beacon_height, interval=None, timeout=120):
        """
        Wait until a specific beacon height
        @param interval:
        @param timeout:
        @param beacon_height:
        @return:
        """
        INFO(f'Waiting till beacon height {beacon_height}')
        from Objects.IncognitoTestCase import SUT
        current_beacon_h = SUT().help_get_beacon_height()
        if beacon_height <= current_beacon_h:
            INFO(f'Beacon height {beacon_height} is passed already')
            return current_beacon_h

        while beacon_height > current_beacon_h:
            if timeout <= 0:
                INFO(f'Time out and current beacon height is {current_beacon_h}')
                return current_beacon_h
            if interval is None:
                block_remain = beacon_height - current_beacon_h
                interval = block_remain * ChainConfig.BLOCK_TIME
            WAIT(interval)
            timeout -= interval
            current_beacon_h = SUT().help_get_beacon_height()

        INFO(f'Beacon height {beacon_height} is passed already')
        return current_beacon_h

    @staticmethod
    def wait_till_next_beacon_height(num_of_beacon_height_to_wait=1, wait=None, timeout=120):
        """
        wait for an amount of beacon height to pass
        @param timeout:
        @param wait:
        @param num_of_beacon_height_to_wait:
        @return:
        """
        from Objects.IncognitoTestCase import SUT
        current_beacon_h = SUT().help_get_beacon_height()
        return ChainHelper.wait_till_beacon_height(current_beacon_h + num_of_beacon_height_to_wait, wait, timeout)

    @staticmethod
    def wait_till_next_shard_height(shard_id, num_of_shard_height_to_wait=1, wait=None, timeout=120):
        """
        Function to wait for an amount of shard height to pass
        @param shard_id:
        @param num_of_shard_height_to_wait:
        @param wait:
        @param timeout:
        @return:
        """
        from Objects.IncognitoTestCase import SUT
        wait = ChainConfig.BLOCK_TIME if wait is None else wait
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
    def wait_till_next_epoch(epoch_to_wait=1, block_of_epoch=1, node=None):
        f"""
        Wait till {epoch_to_wait} to come, if {epoch_to_wait} is None, just wait till next epoch
        @param epoch_to_wait: number of epoch to wait
        @param block_of_epoch: the n(th) block of epoch, default is the first block
        @param node: Node object, node to get info from to wait
        @return: current epoch number and beacon height
        """
        from Objects.IncognitoTestCase import SUT
        from Objects.NodeObject import Node
        node: Node = SUT() if not node else node
        blk_chain_info = node.get_block_chain_info()
        current_epoch = blk_chain_info.get_beacon_block().get_epoch()
        current_height = blk_chain_info.get_beacon_block().get_height()
        first_blk_of_current_epoch = ChainHelper.cal_first_height_of_epoch(current_epoch)
        num_of_block_till_next_epoch = blk_chain_info.get_beacon_block().get_remaining_block_epoch()
        if epoch_to_wait == 0:
            block_to_wait = first_blk_of_current_epoch + block_of_epoch - current_height
        else:
            block_to_wait = num_of_block_till_next_epoch + block_of_epoch \
                            + (epoch_to_wait - 1) * ChainConfig.BLOCK_PER_EPOCH
        time_to_wait = ChainConfig.get_epoch_n_block_time(0, block_to_wait)
        INFO(f'Current height = {current_height} @ epoch = {current_epoch}. '
             f'Wait {time_to_wait}s until epoch {current_epoch + epoch_to_wait} and B height {block_of_epoch}')
        WAIT(time_to_wait)
        blk_chain_info = node.get_block_chain_info()
        return blk_chain_info.get_epoch_number(), blk_chain_info.get_beacon_block().get_height()


def get_beacon_best_state_detail(number_of_beacon_height_to_get=100, wait=5, timeout=50):
    """
    Function to get beacon best state detail
    @param number_of_beacon_height_to_get: number of beacon height to get
    @param wait:
    @param timeout:
    @return: a list beacon best state detail obj
    """
    from Objects.IncognitoTestCase import SUT
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
    from Objects.IncognitoTestCase import SUT
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
    from Objects.IncognitoTestCase import SUT
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
    from Objects.IncognitoTestCase import SUT
    list_shard_best_state_objs = []
    for i in range(1, number_of_shard_height_to_get + 1):
        list_shard_best_state_objs.append(SUT().get_shard_best_state_info(shard_id))
        # Waiting till shard height increase
        ChainHelper.wait_till_next_shard_height(shard_id=shard_id, num_of_shard_height_to_wait=1, wait=wait,
                                                timeout=timeout)
        list_shard_best_state_objs.append(SUT().get_shard_best_state_info(shard_id))
    return list_shard_best_state_objs


def make_random_word(word_min_len=3, word_max_len=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(word_min_len, word_max_len)))


def make_random_str_list(length=None, word_min_len=3, word_max_len=8):
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
