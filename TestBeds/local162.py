from Objects.TestBedObject import Node, Shard, Beacon

addr = '68.183.187.162'
full_node = Node(address=addr, rpc_port=8334, ws_port=18334, node_name='fullnode-testnet')

beacon = Beacon([
    Node(address=addr, rpc_port=9335, ws_port=30000, node_name='beacon_0'),
    Node(address=addr, rpc_port=9336, ws_port=30001, node_name='beacon_1'),
    Node(address=addr, rpc_port=9337, ws_port=30002, node_name='beacon_2'),
    Node(address=addr, rpc_port=9338, ws_port=30003, node_name='beacon_3')
])

shard_list = [Shard([Node(address=addr, rpc_port=9339, ws_port=30004, node_name='shard_0_0'),
                     Node(address=addr, rpc_port=9340, ws_port=30005, node_name='shard_0_1'),
                     Node(address=addr, rpc_port=9341, ws_port=30006, node_name='shard_0_2'),
                     Node(address=addr, rpc_port=9342, ws_port=30007, node_name='shard_0_3'),
                     ]),
              Shard([Node(address=addr, rpc_port=9343, ws_port=30008, node_name='shard_1_0'),
                     Node(address=addr, rpc_port=9344, ws_port=30009, node_name='shard_1_1'),
                     Node(address=addr, rpc_port=9345, ws_port=30010, node_name='shard_1_2'),
                     Node(address=addr, rpc_port=9346, ws_port=30011, node_name='shard_1_3'),
                     ])
              ]

stakers = [Node(address=addr, rpc_port=10335, ws_port=30004, node_name='staker_0'),
           Node(address=addr, rpc_port=10336, ws_port=30005, node_name='staker_1'),
           Node(address=addr, rpc_port=10337, ws_port=30006, node_name='staker_2'),
           Node(address=addr, rpc_port=10338, ws_port=30007, node_name='staker_3'),
           Node(address=addr, rpc_port=10339, ws_port=30004, node_name='staker_4'),
           Node(address=addr, rpc_port=10340, ws_port=30005, node_name='staker_5'),
           Node(address=addr, rpc_port=10341, ws_port=30006, node_name='staker_6'),
           Node(address=addr, rpc_port=10342, ws_port=30007, node_name='staker_7'),
           Node(address=addr, rpc_port=10343, ws_port=30004, node_name='staker_8'),
           Node(address=addr, rpc_port=10344, ws_port=30005, node_name='staker_9'),
           Node(address=addr, rpc_port=10345, ws_port=30006, node_name='staker_10'),
           Node(address=addr, rpc_port=10346, ws_port=30007, node_name='staker_11'),
           Node(address=addr, rpc_port=10347, ws_port=30004, node_name='staker_12'),
           Node(address=addr, rpc_port=10348, ws_port=30005, node_name='staker_13'),
           Node(address=addr, rpc_port=10349, ws_port=30006, node_name='staker_14'),
           Node(address=addr, rpc_port=10350, ws_port=30007, node_name='staker_15'),
           ]
