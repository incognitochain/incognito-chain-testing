from requests import ConnectionError

from Helpers.Logging import INFO, INFO_HEADLINE
from Helpers.TestHelper import make_random_str_list
from Helpers.Time import WAIT
from Objects.NodeObject import Node
from SpecialTests.TrashTalk import RPC_METHODS

node_url = 'http://139.162.55.124:8334'


def test_crash_trash_talk():
    node = Node(url=node_url)

    node._ssh_session.ssh_connect().is_node_alive()
    to_blame = []
    not_found = []
    for method in RPC_METHODS:
        INFO(f'Invoke: {method}')
        try:
            res = node.rpc_connection().with_method(method).with_params(make_random_str_list()).execute()
            if res.get_error_msg() == "Method not found":
                not_found.append(method)
        except ConnectionError:
            INFO(f'{method} causes the crash')
            to_blame.append(method)
            node.start_node()
            WAIT(15)
            continue

        WAIT(1)

    INFO_HEADLINE('''Not exist method:''')
    for method in not_found:
        INFO(method)

    INFO_HEADLINE('''Trash talker report:''')
    for method in to_blame:
        INFO(method)

    INFO_HEADLINE('Summary')
    INFO(f"""
            Tested:    {len(RPC_METHODS)} methods
            Not found: {len(not_found)}
            Crash:     {len(to_blame)}""")
