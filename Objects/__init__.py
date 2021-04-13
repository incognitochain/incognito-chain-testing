import json
from abc import ABC


class BlockChainInfoBaseClass(ABC):
    def __init__(self, dict_data=None):
        self.data: dict = dict_data
        self.err = None

    def __eq__(self, other):
        return self.data == other.data

    def __ne__(self, other):
        return self.data != other.data

    def is_none(self):
        return bool(self.data)

    def pretty_format(self):
        return json.dumps(self.data, indent=3)

    def pretty_print(self):
        print(self.pretty_format())

    def __str__(self):
        return self.pretty_format()
