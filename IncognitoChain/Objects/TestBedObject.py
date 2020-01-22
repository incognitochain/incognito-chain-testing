from typing import List

import IncognitoChain.Helpers.Logging as Log
from IncognitoChain.Objects.NodeObject import Node
from IncognitoChain.Objects.ShardObject import Shard, Beacon


def load_test_data(name):
    Log.INFO(f'Loading {name} test data')
    return __import__(f'IncognitoChain.TestBeds.{name}', fromlist=['object'])


class TestBed:
    def __init__(self, test_bed):
        tb = load_test_data(test_bed)

        self.full_node: Node = tb.full_node
        self.beacon: Beacon = tb.beacon
        self.shards: List[Shard] = tb.shard_list

    def precondition_check(self):
        print(f'Checking test bed')
