import json
import random
import string
from json.decoder import JSONDecodeError

from Configs.Configs import ChainConfig
from Helpers.Logging import config_logger

logger = config_logger(__name__)


class CustomAssert:
    @staticmethod
    def compare_with_margin(a, b, margin):
        if abs(a - b) > margin:
            raise AssertionError(f"{a} vs {b}, margin {margin}")
        logger.info(f"{a} vs {b} is tolerable, margin = {margin}")
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
