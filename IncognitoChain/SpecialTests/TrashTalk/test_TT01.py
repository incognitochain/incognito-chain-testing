from requests import ConnectionError

from IncognitoChain.Helpers.Logging import INFO, INFO_HEADLINE
from IncognitoChain.Helpers.TestHelper import make_random_str_list
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.NodeObject import Node
from IncognitoChain.SpecialTests.TrashTalk import RPC_METHODS

node_url = 'http://139.162.55.124:8334'


def test_crash_trash_talk():
    node = Node(url=node_url)
    node.ssh().is_node_alive()
    to_blame = []
    for method in RPC_METHODS:
        INFO(f'Invoke: {method}')
        try:
            node.rpc_connection().with_method(method).with_params(make_random_str_list()).execute()
        except ConnectionError:
            INFO(f'{method} causes the crash')
            to_blame.append(method)
            node.ssh().start_node()
            WAIT(15)
            continue

        WAIT(2)

    INFO_HEADLINE('''Trash talker report:''')
    for method in to_blame:
        INFO(method)
