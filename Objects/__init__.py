import copy
import json
from abc import ABC

from deepdiff import DeepDiff

from Helpers.Logging import config_logger

logger = config_logger(__name__)


class BlockChainInfoBaseClass(ABC):
    def __init__(self, dict_data=None):
        self.dict_data: dict = dict_data
        self.err = None

    def __deepcopy__(self, memo=None):
        clone = object.__new__(type(self))
        clone.dict_data = copy.deepcopy(self.dict_data)
        clone.err = copy.deepcopy(self.err)
        return clone

    def __eq__(self, other):
        diff = DeepDiff(self.dict_data, other.dict_data)
        if diff:
            logger.info(f"\n{diff.pretty()}", self.__class__.__name__)
            return False
        return True

    def __ne__(self, other):
        return self.dict_data != other.dict_data

    def is_none(self):
        return bool(self.dict_data)

    def pretty(self):
        return json.dumps(self.dict_data, indent=3)

    def pretty_print(self):
        print(self.pretty())

    def clone(self):
        return self.__deepcopy__()

    def __str__(self):
        return self.pretty()

    def _1_item_dict_key(self):
        return list(self.dict_data.keys())[0]

    def _1_item_dict_value(self):
        return self.dict_data[self._1_item_dict_key()]
