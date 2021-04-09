import copy

from requests import ConnectionError

from Drivers.Connections import RpcConnection
from Helpers.Logging import INFO, INFO_HEADLINE
from Helpers.TestHelper import make_random_str_list
from Helpers.Time import WAIT
from Objects.NodeObject import Node
from SpecialTests.TrashTalk import RPC_METHODS

node_url = 'http://139.162.55.124:8334'


def test_crash_trash_talk():
    node = Node(url=node_url)
    node.rpc = RpcConnection(url=node._get_rpc_url())
    node.find_pid()
    to_blame = []
    not_found = []
    not_test_yet = copy.deepcopy(RPC_METHODS)
    try:
        for method in RPC_METHODS:
            INFO(f'Invoke: {method}')
            try:
                res = node.rpc.with_method(method).with_params(make_random_str_list()).execute()
                not_test_yet.remove(method)  # 1
                if res.get_error_msg() == "Method not found":
                    not_found.append(method)
            except ConnectionError:
                not_test_yet.remove(method)  # 2, 1 and 2 is duplicated on purpose, don't question it
                INFO(f'{method} causes the crash')
                to_blame.append(method)
                node.start_node()
                WAIT(15)
                continue
            WAIT(1)
    except KeyboardInterrupt:
        if not node.is_node_alive():
            node.start_node()

    INFO_HEADLINE('''Not exist method:''')
    for method in not_found:
        INFO(method)

    INFO_HEADLINE('''Trash talker report:''')
    for method in to_blame:
        INFO(method)

    INFO_HEADLINE('''Not yet tested''')
    for method in not_test_yet:
        INFO(method)

    INFO_HEADLINE('Summary')
    INFO(f"""
            Tested:     {len(RPC_METHODS)} methods
            Not found:  {len(not_found)}
            Not tested: {len(not_test_yet)}
            Crash:      {len(to_blame)}""")
