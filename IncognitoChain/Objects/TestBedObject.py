from typing import List

from IncognitoChain.Objects.NodeObject import Node
from IncognitoChain.Objects.ShardObject import Shard, Beacon


def load_test_bed(name):
    print(f' !!! Loading {name} test bed')
    return __import__(f'IncognitoChain.TestBeds.{name}', fromlist=['object'])


class TestBed:
    def __init__(self, test_bed):
        from IncognitoChain.Objects.AccountObject import Account

        tb = load_test_bed(test_bed)

        self.full_node: Node = tb.full_node
        self.beacon: Beacon = tb.beacon
        self.shards: List[Shard] = tb.shard_list
        self.accounts: List[Account] = tb.account_list

    def precondition_check(self):
        print(f'Checking test bed')
