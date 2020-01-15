from IncognitoChain.Objects.NodeObject import load_node
from IncognitoChain.Objects.ShardObject import load_shard


def load_test_bed(name):
    return __import__(f'IncognitoChain.TestBeds.{name}', fromlist=['object'])


class TestBed:
    def __init__(self, test_bed):
        tb = load_test_bed(test_bed)

        self.full_node = load_node(tb.full_node)
        self.beacon = load_shard(tb.beacon)
        self.shards = [load_shard(tb.shard0),
                       load_shard(tb.shard1),
                       load_shard(tb.shard2),
                       load_shard(tb.shard3),
                       load_shard(tb.shard4),
                       load_shard(tb.shard5),
                       load_shard(tb.shard6),
                       load_shard(tb.shard7)]
