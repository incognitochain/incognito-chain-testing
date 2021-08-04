from Objects.TestBedObject import Node, Shard, Beacon

full_node = Node(url='http://51.195.4.15:29906', ws_port=30002, node_name='fullnode-testnet')

beacon = Beacon([
    Node(address="51.79.76.116", rpc_port=20000, ws_port=30000, node_name='beacon0'),
    Node(address="51.79.76.116", rpc_port=20001, ws_port=30001, node_name='beacon0'),
    Node(address="51.79.76.116", rpc_port=20002, ws_port=30002, node_name='beacon0'),
    Node(address="51.79.76.116", rpc_port=20003, ws_port=30003, node_name='beacon0')
])

shard_list = [Shard([Node(address="172.105.115.134", rpc_port=20004, ws_port=30004, node_name='shard0-0',
                          # validator=Account(
                          #     private_key='112t8rnXB47RhSdyVRU41TEf78nxbtWGtmjutwSp9YqsNaCpFxQGXcnwcXTtBkCGDk1KLBRBeWMvb2aXG5SeDUJRHtFV8jTB3weHEkbMJ1AL')
                          ),
                     Node(address="172.105.200.109", rpc_port=20005, ws_port=30005, node_name='shard0-1',
                          # validator=Account(
                          #     private_key='112t8rnXVdfBqBMigSs5fm9NSS8rgsVVURUxArpv6DxYmPZujKqomqUa2H9wh1zkkmDGtDn2woK4NuRDYnYRtVkUhK34TMfbUF4MShSkrCw5')
                          ),
                     Node(address="172.105.112.133", rpc_port=20006, ws_port=30006, node_name='shard0-2',
                          # validator=Account(
                          #     private_key='112t8rnXi8eKJ5RYJjyQYcFMThfbXHgaL6pq5AF5bWsDXwfsw8pqQUreDv6qgWyiABoDdphvqE7NFr9K92aomX7Gi5Nm1e4tEoV3qRLVdfSR')
                          ),
                     Node(address="172.104.82.133", rpc_port=20007, ws_port=30007, node_name='shard0-3',
                          # validator=Account(
                          #     private_key='112t8rnY42xRqJghQX3zvhgEa2ZJBwSzJ46SXyVQEam1yNpN4bfAqJwh1SsobjHAz8wwRvwnqJBfxrbwUuTxqgEbuEE8yMu6F14QmwtwyM43')
                          ),
                     ]),
              Shard([Node(address="172.105.115.134", rpc_port=20008, ws_port=30008, node_name='shard1-0'),
                     Node(address="172.105.200.109", rpc_port=20009, ws_port=30009, node_name='shard1-1'),
                     Node(address="172.105.112.133", rpc_port=20010, ws_port=30010, node_name='shard1-2'),
                     Node(address="172.104.82.133", rpc_port=20011, ws_port=30011, node_name='shard1-3'),
                     ]),
              Shard([Node(address="172.105.115.134", rpc_port=20012, ws_port=30012, node_name='shard2-0'),
                     Node(address="172.105.200.109", rpc_port=20013, ws_port=30013, node_name='shard2-1'),
                     Node(address="172.105.112.133", rpc_port=20014, ws_port=30014, node_name='shard2-2'),
                     Node(address="172.104.82.133", rpc_port=20015, ws_port=30015, node_name='shard2-3'),
                     ]),
              Shard([Node(address="172.105.115.134", rpc_port=20016, ws_port=30016, node_name='shard3-0'),
                     Node(address="172.105.200.109", rpc_port=20017, ws_port=30017, node_name='shard3-1'),
                     Node(address="172.105.112.133", rpc_port=20018, ws_port=30018, node_name='shard3-2'),
                     Node(address="172.104.82.133", rpc_port=20019, ws_port=30019, node_name='shard3-3'),
                     ]),
              Shard([Node(address="172.105.113.133", rpc_port=20020, ws_port=30020, node_name='shard4-0'),
                     Node(address="139.162.69.44", rpc_port=20021, ws_port=30021, node_name='shard4-1'),
                     Node(address="172.105.115.135", rpc_port=20022, ws_port=30022, node_name='shard4-2'),
                     Node(address="139.162.114.95", rpc_port=20023, ws_port=30023, node_name='shard4-3'),
                     ]),
              Shard([Node(address="172.105.113.133", rpc_port=20024, ws_port=30024, node_name='shard5-0'),
                     Node(address="139.162.69.44", rpc_port=20025, ws_port=30025, node_name='shard5-1'),
                     Node(address="172.105.115.135", rpc_port=20026, ws_port=30026, node_name='shard5-2'),
                     Node(address="139.162.114.95", rpc_port=20027, ws_port=30027, node_name='shard5-3'),
                     ]),
              Shard([Node(address="172.105.113.133", rpc_port=20028, ws_port=30028, node_name='shard6-0'),
                     Node(address="139.162.69.44", rpc_port=20029, ws_port=30029, node_name='shard6-1'),
                     Node(address="172.105.115.135", rpc_port=20030, ws_port=30030, node_name='shard6-2'),
                     Node(address="139.162.114.95", rpc_port=20031, ws_port=30031, node_name='shard6-3'),
                     ]),
              Shard([Node(address="172.105.113.133", rpc_port=20032, ws_port=30032, node_name='shard7-0'),
                     Node(address="139.162.69.44", rpc_port=20033, ws_port=30033, node_name='shard7-1'),
                     Node(address="172.105.115.135", rpc_port=20034, ws_port=30034, node_name='shard7-2'),
                     Node(address="139.162.114.95", rpc_port=20035, ws_port=30035, node_name='shard7-3'),
                     ])
              ]
