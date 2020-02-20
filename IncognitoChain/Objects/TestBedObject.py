from typing import List

import IncognitoChain.Helpers.Logging as Log
from IncognitoChain.Objects.NodeObject import Node
from IncognitoChain.Objects.ShardObject import Shard, Beacon


def load_test_data(name):
    Log.INFO(f'Loading: test data {name}')
    try:
        return __import__(f'IncognitoChain.TestData.{name}', fromlist=['object'])
    except ModuleNotFoundError:
        raise Exception(f"!!! Test data not found: {name}")


def load_test_bed(name):
    Log.INFO(f'Loading test bed: {name}')
    try:
        return __import__(f'IncognitoChain.TestBeds.{name}', fromlist=['object'])
    except ModuleNotFoundError:
        raise Exception(f"!!! Test bed not found: {name}")


class TestBed:
    def __init__(self, test_bed):
        tb = load_test_bed(test_bed)

        self.full_node: Node = tb.full_node
        self.beacon: Beacon = tb.beacon
        self.shards: List[Shard] = tb.shard_list

    def precondition_check(self):
        Log.INFO(f'Checking test bed')

    def get_request_handler(self, shard_id):
        """
        :param shard_id: if = -1 then return fullnode to handle the request.
         otherwise shard with id = {shard_id} will be returned
        :return:
        """
        if shard_id == -1:
            handler = self.__SUT.full_node
        else:
            handler = self.__SUT.shards[shard_id].get_representative_node()
        return handler
