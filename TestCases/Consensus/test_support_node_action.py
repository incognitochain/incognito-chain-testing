import pytest

from Helpers.Logging import INFO
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import SUT


@pytest.mark.parametrize('sync_mode, enable_ffstorage, list_nodes_shard', [
    # ("archive", True, {"-1": [0],
    #                    "0": [0, 3, 10],
    #                    "1": [3, 5, 9],
    #                    "2": [1, 2, 5, 9],
    #                    "3": [7, 11, 0]}),
    # ("batchcommit", True, {"-1": [1],
    #                        "0": [1, 2, 8],
    #                        "1": [0, 6, 7, 11],
    #                        "2": [3, 11, 6],
    #                        "3": [2, 6, 9, 10]}),
    # ("lite", True, {"-1": [2],
    #                 "0": [4, 11, 5, 9],
    #                 "1": [1, 4, 8],
    #                 "2": [0, 4, 7, 10],
    #                 "3": [1, 3, 5, 8]}),
    ("batchcommit", False, {"-1": [3],
                            "0": [6, 7],
                            "1": [2, 10],
                            "2": [8],
                            "3": [4]}),
    # ("Beacon", False, {"-1": [0, 1, 2, 3]}),
])
def test_support_kill_clear_db(sync_mode, enable_ffstorage, list_nodes_shard):
    INFO()
    folder_logs = 1156
    string_info = f'\n\tlogs: {folder_logs + 1}\n\tConfig: sync_mode "{sync_mode}", enable_ffstorage: {enable_ffstorage}\n' \
                  '\tNodes: '
    list_nodes = []
    for s_id, value in list_nodes_shard.items():
        if s_id == "-1":
            for i in value:
                string_info += f'beacon_{i}, '
                list_nodes.append(SUT.beacons.get_node(i))
        else:
            for i in value:
                string_info += f'shard_{s_id}_{i}, '
                list_nodes.append(SUT.shards[int(s_id)].get_node(i))
    INFO(string_info)
    for node in list_nodes:
        node.kill_node()
        WAIT(2)
        # node.clear_data()
    INFO()


def test_support_clear_log():
    INFO()
    node = SUT()
    range_shard = range(12)
    range_beacon = range(4)
    folder_logs = '1157_0331_1026/'
    list_nodes_skips = {"-1": [2],
                        "0": [4, 11, 5, 9],
                        "1": [1, 4, 8],
                        "2": [0, 4, 7, 10],
                        "3": [1, 3, 5, 8]}
    files_need_clear = []
    for s_id, value in list_nodes_skips.items():
        if s_id == "-1":
            for i in range_beacon:
                if i not in value:
                    files_need_clear.append(f'beacon_{i}-*')
                    files_need_clear.append(f'beacon_{i}.*')
        else:
            for i in range_shard:
                if i not in value:
                    files_need_clear.append(f'shard_{s_id}_{i}-*')
                    files_need_clear.append(f'shard_{s_id}_{i}.*')
    # files_need_clear.append('full_node*')
    # files_need_clear.append('mstaker_0*')
    node.find_pid()
    folder = f'{node.get_log_folder()}/{folder_logs}'
    INFO(f'Clear files:\n{files_need_clear}')
    node._ssh_session.goto_folder(folder)
    for file in files_need_clear:
        node._ssh_session.send_cmd(f'rm -rf {file}')
