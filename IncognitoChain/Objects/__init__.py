from abc import ABC


class BlockChainInfoBaseClass(ABC):
    def __init__(self, dict_data=None):
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        self.data: dict = dict_data
        self.err = None
        self.SUT = SUT

    def __eq__(self, other):
        return self.data == other.data

    def __ne__(self, other):
        return self.data != other.data

    def is_none(self):
        return self.data is None or self.data == ''
