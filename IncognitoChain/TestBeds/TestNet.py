from IncognitoChain.Objects.AccountObject import *
from IncognitoChain.Objects.ShardObject import *

full_node = Node(address="test-node.incognito.org", rpc_port=9334, ws_port=19334, node_name='fullnode0')

beacon = Beacon([
    Node(address="51.79.76.116", rpc_port=20000, ws_port=30000, node_name='beacon0'),
    Node(address="51.79.76.116", rpc_port=20001, ws_port=30001, node_name='beacon0'),
    Node(address="51.79.76.116", rpc_port=20002, ws_port=30002, node_name='beacon0'),
    Node(address="51.79.76.116", rpc_port=20003, ws_port=30003, node_name='beacon0')
])

shard_list = [Shard([Node(),
                     Node(node_name='shard0-1'),
                     Node(address="172.105.112.133", rpc_port=20006, ws_port=30006, node_name='shard0-2'),
                     Node(address="172.105.112.133", rpc_port=20007, ws_port=30007, node_name='shard0-3'),
                     ]),
              Shard([Node(rpc_port=9338),
                     Node(node_name='shard1-1'),
                     Node(address='172.105.112.133', rpc_port=20010, ws_port=30010, node_name="shard1-2"),
                     Node(address='172.105.112.133', rpc_port=20011, ws_port=30011, node_name="shard1-3")
                     ]),
              Shard([Node(node_name="shard2-0"),
                     Node(node_name="shard2-1"),
                     Node(node_name="shard2-2"),
                     Node(node_name="shard2-3", address='172.104.82.133', rpc_port=20015, ws_port=30015),
                     ]),
              Shard([Node(node_name="shard3-0"),
                     Node(node_name="shard3-1"),
                     Node(node_name="shard3-2"),
                     Node(node_name="shard3-3", address='172.104.82.133', rpc_port=20019, ws_port=30019)
                     ]),
              Shard([Node(node_name="shard4-0"),
                     Node(node_name="shard4-1"),
                     Node(node_name="shard4-2", address='172.105.115.135', rpc_port=20022, ws_port=30022),
                     Node(node_name="shard4-3", address='139.162.114.95', rpc_port=20023, ws_port=30023)
                     ]),
              Shard([Node(node_name="shard5-0"),
                     Node(node_name="shard5-1"),
                     Node(node_name="shard5-2"),
                     Node(node_name="shard5-3", address='139.162.114.95', rpc_port=20027, ws_port=30027),
                     ]),
              Shard([Node(node_name="shard6-0"),
                     Node(node_name="shard6-1"),
                     Node(node_name="shard6-2"),
                     Node(node_name="shard6-3", address='139.162.114.95', rpc_port=20031, ws_port=30031),
                     ]),
              Shard([Node(node_name="shard7-0"),
                     Node(node_name="shard7-1"),
                     Node(node_name="shard7-2"),
                     Node(node_name="shard7-3", address='139.162.114.95', rpc_port=20025, ws_port=30035),
                     ]),
              ]
account_list = \
    [
        Account(
            "112t8rnXVMJJZzfF1naXvfE9nkTKwUwFWFeh8cfEyViG1vpA8A9khJk3mhyB1hDuJ4RbreDTsZpgJK4YcSxdEpXJKMEd8Vmp5UqKWwBcYzxv",
            "12RyJTSL2G8KvjN7SUFuiS9Ek4pvFFze3EMMic31fmXVw8McwYzpKPpxeW6TLsNo1UoPhCHKV3GDRLQwdLF41PED3LQNCLsGNKzmCE5",
            shard=2),
        Account(
            "112t8rnX6USJnBzswUeuuanesuEEUGsxE8Pj3kkxkqvGRedUUPyocmtsqETX2WMBSvfBCwwsmMpxonhfQm2N5wy3SrNk11eYxEyDtwuGxw2E",
            "12RwbexYzKJwGaJDdDE7rgLEkNC1dL5cJf4xNaQ29EmpPN52C6oepWiTtQCpyHAoo6ZTHMx2Nt3A8p5jYqpYvbrVYGpVTen1rVstCpr",
            shard=2),
        Account(
            "112t8rnXoEWG5H8x1odKxSj6sbLXowTBsVVkAxNWr5WnsbSTDkRiVrSdPy8QfMujntKRYBqywKMJCyhMpdr93T3XiUD5QJR1QFtTpYKpjBEx",
            "12RqmK5woGNeBTy16ouYepSw4QEq28gsv2m81ebcPQ82GgS5S8PHEY37NU2aTacLRruFvjTqKCgffTeMDL83snTYz5zDp1MTLwjVhZS",
            shard=5),
        Account(
            "112t8rnZ5UZouZU9nFmYLfpHUp8NrvQkGLPD564mjzNDM8rMp9nc9sXZ6CFxCGEMuvHQpYN7af6KCPJnq9MfEnXQfntbM8hpy9LW8p4qzPxS",
            "12Rw9oesEgd8t5NGrfqxtWTCzh1eDif55miqZ1kFzj5zeQ6UQnNB9JXRn5Vc5QVbBaiFhoYdYPnQZ5tWwcBpse5EJXM3Av6qEV2wspv",
            shard=4),
        Account(
            "112t8rnan3pbXtdvfKSk3kti1tFcFpVSq5wp7c3hhLk7E4jQih2zsv8ynjpP1UQivExGwbMf9Ezp9qmKBJuHhNZPAzheqX4WTV8LfrdZY5Mh",
            "12RxCyrWFCkpzfnMcnN8MuDrXkFAsEAkhyn4zHhy3n6CNZPYJ4cNDesBGycwu62PJn8rQ8uLiC5zSYDiXFa9hXtQMUJvVCMT2uUNn8G",
            shard=4),
        Account(
            "112t8rnZ9qPE7C6RbrK6Ygat1H94kEkYGSd84fAGiU396yQHu8CBHmV1DDHE947d7orfHnDtKA9WCffDk7NS5zUu5CMCUHK8nkRtrv4nw6uu",
            "12Rrk9r3Chmt5Wibkmu2VcFSUffGZbkz2rzMWdmmB3GEu8t8RF4v2wc1gBQtkJFZmPfUP29bSXR4Wn8kDveLQBTBK5Hck9BoGRnuM7n",
            shard=4),
        Account(
            "112t8rnaK4C17Chu8rEAPXHUaPYNeGz8VsjV7BzdeLA9VBc8oiYwQXNrc6XEABb4uNEfG9LFgvVfi4KQmVpQrwMWph4E1YoVS1m37HwrFDsE",
            "12RtmaJMoRbUCsYxLC4RatP2vWVR3QdZXpbkXR7LwZjVrZfXF46ZNL4QgpCU71SXjz2eCeruA7ZiHM91otTJXzqJiztq5mrdHA35yaf",
            shard=4)
    ]
