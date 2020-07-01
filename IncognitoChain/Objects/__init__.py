from abc import ABC


class BlockChainInfoBaseClass(ABC):
    def __init__(self, dict_data=None):
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        self.data: dict = dict_data
        self.err = None
        self.SUT = SUT
