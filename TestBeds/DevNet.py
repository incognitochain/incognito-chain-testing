from Objects.TestBedObject import Node, Shard, Beacon

full_node = Node(address="54.39.158.106", rpc_port=9334, ws_port=19334, node_name='fullnode-devnet')

beacon = Beacon([
    Node(address="54.39.158.106", rpc_port=20000, ws_port=30000, node_name='beacon0'),
    Node(address="54.39.158.106", rpc_port=20001, ws_port=30001, node_name='beacon1'),
    Node(address="54.39.158.106", rpc_port=20002, ws_port=30002, node_name='beacon2'),
    Node(address="54.39.158.106", rpc_port=20003, ws_port=30003, node_name='beacon3')
])

shard_list = [Shard([Node(address="54.39.158.106", rpc_port=20004, ws_port=30004, node_name='shard0-0'),
                     Node(address="54.39.158.106", rpc_port=20005, ws_port=30005, node_name='shard0-1'),
                     Node(address="54.39.158.106", rpc_port=20006, ws_port=30006, node_name='shard0-2'),
                     Node(address="54.39.158.106", rpc_port=20007, ws_port=30007, node_name='shard0-3'),
                     ]),
              Shard([Node(address="54.39.158.106", rpc_port=20008, ws_port=30008, node_name='shard1-0'),
                     Node(address="54.39.158.106", rpc_port=20009, ws_port=30009, node_name='shard1-1'),
                     Node(address="54.39.158.106", rpc_port=20010, ws_port=30010, node_name='shard1-2'),
                     Node(address="54.39.158.106", rpc_port=20011, ws_port=30011, node_name='shard1-3'),
                     ]),
              Shard([Node(address="54.39.158.106", rpc_port=20012, ws_port=30012, node_name='shard2-0'),
                     Node(address="54.39.158.106", rpc_port=20013, ws_port=30013, node_name='shard2-1'),
                     Node(address="54.39.158.106", rpc_port=20014, ws_port=30014, node_name='shard2-2'),
                     Node(address="54.39.158.106", rpc_port=20015, ws_port=30015, node_name='shard2-3'),
                     ]),
              Shard([Node(address="54.39.158.106", rpc_port=20016, ws_port=30016, node_name='shard3-0'),
                     Node(address="54.39.158.106", rpc_port=20017, ws_port=30017, node_name='shard3-1'),
                     Node(address="54.39.158.106", rpc_port=20018, ws_port=30018, node_name='shard3-2'),
                     Node(address="54.39.158.106", rpc_port=20019, ws_port=30019, node_name='shard3-3'),
                     ]),
              Shard([Node(address="54.39.158.106", rpc_port=20020, ws_port=30020, node_name='shard4-0'),
                     Node(address="54.39.158.106", rpc_port=20021, ws_port=30021, node_name='shard4-1'),
                     Node(address="54.39.158.106", rpc_port=20022, ws_port=30022, node_name='shard4-2'),
                     Node(address="54.39.158.106", rpc_port=20023, ws_port=30023, node_name='shard4-3'),
                     ]),
              Shard([Node(address="54.39.158.106", rpc_port=20024, ws_port=30024, node_name='shard5-0'),
                     Node(address="54.39.158.106", rpc_port=20025, ws_port=30025, node_name='shard5-1'),
                     Node(address="54.39.158.106", rpc_port=20026, ws_port=30026, node_name='shard5-2'),
                     Node(address="54.39.158.106", rpc_port=20027, ws_port=30027, node_name='shard5-3'),
                     ]),
              Shard([Node(address="54.39.158.106", rpc_port=20028, ws_port=30028, node_name='shard6-0'),
                     Node(address="54.39.158.106", rpc_port=20029, ws_port=30029, node_name='shard6-1'),
                     Node(address="54.39.158.106", rpc_port=20030, ws_port=30030, node_name='shard6-2'),
                     Node(address="54.39.158.106", rpc_port=20031, ws_port=30031, node_name='shard6-3'),
                     ]),
              Shard([Node(address="54.39.158.106", rpc_port=20032, ws_port=30032, node_name='shard7-0'),
                     Node(address="54.39.158.106", rpc_port=20033, ws_port=30033, node_name='shard7-1'),
                     Node(address="54.39.158.106", rpc_port=20034, ws_port=30034, node_name='shard7-2'),
                     Node(address="54.39.158.106", rpc_port=20035, ws_port=30035, node_name='shard7-3'),
                     ])
              ]
