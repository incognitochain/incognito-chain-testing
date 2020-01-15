from IncognitoChain.Objects.NodeObject import Node
from IncognitoChain.Objects.ShardObject import Shard

full_node = Node(address="test-node.incognito.org", rpc_port=9334, ws_port=19334, node_name='fullnode0')

beacon = Shard([
    Node(address="51.79.76.116", rpc_port=20000, ws_port=30000, node_name='beacon0'),
    Node(address="51.79.76.116", rpc_port=20001, ws_port=30001, node_name='beacon0'),
    Node(address="51.79.76.116", rpc_port=20002, ws_port=30002, node_name='beacon0'),
    Node(address="51.79.76.116", rpc_port=20003, ws_port=30003, node_name='beacon0')
])

shard0 = Shard([
    Node(),
    Node(node_name='shard0-1'),
    Node(address="172.105.112.133", rpc_port=20006, ws_port=30006, node_name='shard0-2'),
    Node(address="172.105.112.133", rpc_port=20007, ws_port=30007, node_name='shard0-3'),
])

shard1 = Shard([
    Node(rpc_port=9338),
    Node(node_name='shard1-1'),
    Node(address='172.105.112.133', rpc_port=20010, ws_port=30010, node_name="shard1-2"),
    Node(address='172.105.112.133', rpc_port=20011, ws_port=30011, node_name="shard1-3")
])

shard2 = Shard([
    Node(node_name="shard2-0"),
    Node(node_name="shard2-1"),
    Node(node_name="shard2-2"),
    Node(node_name="shard2-3", address='172.104.82.133', rpc_port=20015, ws_port=30015),
])

shard3 = Shard([
    Node(node_name="shard3-0"),
    Node(node_name="shard3-1"),
    Node(node_name="shard3-2"),
    Node(node_name="shard3-3", address='172.104.82.133', rpc_port=20019, ws_port=30019)
])

shard4 = Shard([
    Node(node_name="shard4-0"),
    Node(node_name="shard4-1"),
    Node(node_name="shard4-2", address='172.105.115.135', rpc_port=20022, ws_port=30022),
    Node(node_name="shard4-3", address='139.162.114.95', rpc_port=20023, ws_port=30023)
])

shard5 = Shard([
    Node(node_name="shard5-0"),
    Node(node_name="shard5-1"),
    Node(node_name="shard5-2"),
    Node(node_name="shard5-3", address='139.162.114.95', rpc_port=20027, ws_port=30027),
])

shard6 = Shard([
    Node(node_name="shard6-0"),
    Node(node_name="shard6-1"),
    Node(node_name="shard6-2"),
    Node(node_name="shard6-3", address='139.162.114.95', rpc_port=20031, ws_port=30031),
])

shard7 = Shard([
    Node(node_name="shard7-0"),
    Node(node_name="shard7-1"),
    Node(node_name="shard7-2"),
    Node(node_name="shard7-3", address='139.162.114.95', rpc_port=20025, ws_port=30035),
])
