from Objects.TestBedObject import Node, Shard, Beacon

addr = "139.162.55.124"

full_node = Node(address=addr, rpc_port=9334, ws_port=28334, node_name='fullnode-testnet')

beacon = Beacon([
    Node(address=addr, rpc_port=9335, node_name='beacon1'),
    Node(address=addr, rpc_port=9336, node_name='beacon2'),
    Node(address=addr, rpc_port=9337, node_name='beacon3'),
    Node(address=addr, rpc_port=9338, node_name='beacon4'),
])

shard_list = [Shard([Node(address=addr, rpc_port=19340, ws_port=18335, node_name='shard0-0'),
                     Node(address=addr, rpc_port=19341, ws_port=18336, node_name='shard0-1'),
                     Node(address=addr, rpc_port=19342, ws_port=18337, node_name='shard0-2'),
                     Node(address=addr, rpc_port=19343, ws_port=18338, node_name='shard0-3'),
                     ]),
              Shard([Node(address=addr, rpc_port=19345, ws_port=18341, node_name='shard1-0'),
                     Node(address=addr, rpc_port=19346, ws_port=18342, node_name='shard1-1'),
                     Node(address=addr, rpc_port=19347, ws_port=18353, node_name='shard1-2'),
                     Node(address=addr, rpc_port=19348, ws_port=18344, node_name='shard1-3'),
                     ])
              ]
