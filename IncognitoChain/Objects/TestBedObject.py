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
    REQUEST_HANDLER = Node()

    def __init__(self, test_bed):
        tb = load_test_bed(test_bed)
        self.full_node: Node = tb.full_node
        self.beacons: Beacon = tb.beacon
        self.shards: List[Shard] = tb.shard_list
        TestBed.REQUEST_HANDLER = self.full_node

    def precondition_check(self):
        Log.INFO(f'Checking test bed')
        return self

    def get_committee_accounts(self, shard_id=None):
        acc_list = []
        shards_to_get = self.shards if shard_id is None else [self.shards[shard_id]]
        for shard in shards_to_get:
            shard_acc = [node.account for node in shard._node_list]
            acc_list += shard_acc

        return acc_list

    def get_beacon_accounts(self):
        acc_list = [node.account for node in self.beacons._node_list]
        return acc_list
