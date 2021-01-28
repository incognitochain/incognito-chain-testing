from IncognitoChain.Objects.TestBedObject import Node, Shard, Beacon

addr = "192.168.0.91"

full_node = Node(address=addr, rpc_port=9363, ws_port=19334, node_name='fullnode-testnet')

beacon = Beacon([
    Node(address=addr, rpc_port=29335, node_name='beacon1'),
    Node(address=addr, rpc_port=29336, node_name='beacon2'),
    Node(address=addr, rpc_port=29337, node_name='beacon3'),
    Node(address=addr, rpc_port=29338, node_name='beacon4'),
])

shard_list = [Shard([Node(address=addr, rpc_port=29339, ws_port=39335, node_name='shard0-0'),
                     Node(address=addr, rpc_port=29340, ws_port=39336, node_name='shard0-1'),
                     Node(address=addr, rpc_port=29341, ws_port=39337, node_name='shard0-2'),
                     Node(address=addr, rpc_port=29342, ws_port=39338, node_name='shard0-3'),
                     Node(address=addr, rpc_port=29343, ws_port=39339, node_name='shard0-4'),
                     Node(address=addr, rpc_port=29344, ws_port=39340, node_name='shard0-5'),
                     ]),
              Shard([Node(address=addr, rpc_port=29345, ws_port=39341, node_name='shard1-0'),
                     Node(address=addr, rpc_port=29346, ws_port=39342, node_name='shard1-1'),
                     Node(address=addr, rpc_port=29347, ws_port=39353, node_name='shard1-2'),
                     Node(address=addr, rpc_port=29348, ws_port=39344, node_name='shard1-3'),
                     Node(address=addr, rpc_port=29349, ws_port=39345, node_name='shard1-4'),
                     Node(address=addr, rpc_port=29350, ws_port=39346, node_name='shard1-5'),
                     ])
              ]
