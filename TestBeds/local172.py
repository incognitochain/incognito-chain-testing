from Objects.TestBedObject import Node, Shard, Beacon

addr = '172.105.114.134'
full_node = Node(address=addr, rpc_port=8334, ws_port=18334, node_name='fullnode-testnet')

beacon = Beacon([
    Node(address=addr, rpc_port=9335, ws_port=30000, node_name='beacon0'),
    Node(address=addr, rpc_port=9336, ws_port=30001, node_name='beacon0'),
    Node(address=addr, rpc_port=9337, ws_port=30002, node_name='beacon0'),
    Node(address=addr, rpc_port=9338, ws_port=30003, node_name='beacon0')
])
stakers = []
shard_list = [Shard([Node(address=addr, rpc_port=9339, ws_port=19339, node_name='shard0-0',
                          # validator=Account(
                          #     private_key='112t8rnXB47RhSdyVRU41TEf78nxbtWGtmjutwSp9YqsNaCpFxQGXcnwcXTtBkCGDk1KLBRBeWMvb2aXG5SeDUJRHtFV8jTB3weHEkbMJ1AL')
                          ),
                     Node(address=addr, rpc_port=9340, ws_port=19340, node_name='shard0-1',
                          # validator=Account(
                          #     private_key='112t8rnXVdfBqBMigSs5fm9NSS8rgsVVURUxArpv6DxYmPZujKqomqUa2H9wh1zkkmDGtDn2woK4NuRDYnYRtVkUhK34TMfbUF4MShSkrCw5')
                          ),
                     Node(address=addr, rpc_port=9341, ws_port=19341, node_name='shard0-2',
                          # validator=Account(
                          #     private_key='112t8rnXi8eKJ5RYJjyQYcFMThfbXHgaL6pq5AF5bWsDXwfsw8pqQUreDv6qgWyiABoDdphvqE7NFr9K92aomX7Gi5Nm1e4tEoV3qRLVdfSR')
                          ),
                     Node(address=addr, rpc_port=9342, ws_port=19342, node_name='shard0-3',
                          # validator=Account(
                          #     private_key='112t8rnY42xRqJghQX3zvhgEa2ZJBwSzJ46SXyVQEam1yNpN4bfAqJwh1SsobjHAz8wwRvwnqJBfxrbwUuTxqgEbuEE8yMu6F14QmwtwyM43')
                          ),
                     ]),
              Shard([Node(address=addr, rpc_port=9343, ws_port=19343, node_name='shard1-0'),
                     Node(address=addr, rpc_port=9344, ws_port=19344, node_name='shard1-1'),
                     Node(address=addr, rpc_port=9345, ws_port=19345, node_name='shard1-2'),
                     Node(address=addr, rpc_port=9346, ws_port=19346, node_name='shard1-3'),
                     ])
              ]
