from typing import List

import IncognitoChain.Helpers.Logging as Log
from IncognitoChain.Objects.NodeObject import Node
from IncognitoChain.Objects.ShardObject import Shard, Beacon


def load_test_data(name):
    Log.INFO(f'Loading: test data {name}')
    return __import__(f'IncognitoChain.TestData.{name}', fromlist=['object'])


def load_test_bed(name):
    Log.INFO(f'Loading test bed: {name}')
    return __import__(f'IncognitoChain.TestBeds.{name}', fromlist=['object'])


class TestBed:
    def __init__(self, test_bed):
        tb = load_test_bed(test_bed)

        self.full_node: Node = tb.full_node
        self.beacon: Beacon = tb.beacon
        self.shards: List[Shard] = tb.shard_list

    def precondition_check(self):
        Log.INFO(f'Checking test bed')
